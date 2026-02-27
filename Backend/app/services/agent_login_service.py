"""Agent Login Service — tự động đăng nhập upstream với ddddocr captcha + RSA.

Login flow (EE88 upstream platform):
1. POST {base_url}/agent/login  {scene: "init"}  → {public_key, captcha_url}
2. GET  {base_url}{captcha_url}                   → image bytes
3. ddddocr.classification(image)                  → captcha_code
4. RSA PKCS1v15 encrypt(password, public_key)     → encrypted_password (base64)
5. POST {base_url}/agent/login  {username, password: encrypted, captcha, scene: "login"}
   → {code: 1}  = success, Set-Cookie = session
6. Retry tối đa 3 lần nếu captcha sai
"""

import base64
import hashlib
import logging
from typing import Optional

import httpx
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from app.core.config import settings

logger = logging.getLogger(__name__)

HTTP_TIMEOUT = 30
MAX_CAPTCHA_ATTEMPTS = 3

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
}

# ── Fernet password encryption ───────────────────────────────────────────────


def _get_fernet() -> Fernet:
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    return Fernet(key)


def encrypt_password(plain: str) -> str:
    """Mã hóa mật khẩu bằng Fernet (symmetric). Dùng để lưu DB."""
    return _get_fernet().encrypt(plain.encode()).decode()


def decrypt_password(enc: str) -> str:
    """Giải mã mật khẩu đã lưu DB."""
    return _get_fernet().decrypt(enc.encode()).decode()


# ── Cookie helpers ───────────────────────────────────────────────────────────


def cookie_str_to_dict(cookie_str: str) -> dict:
    """Chuyển chuỗi cookie header sang dict."""
    result: dict = {}
    for part in (cookie_str or "").split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
    return result


def cookie_dict_to_str(cookies: dict) -> str:
    """Chuyển dict sang chuỗi cookie header."""
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


# ── Login Service ────────────────────────────────────────────────────────────


class AgentLoginService:
    """Tự động đăng nhập upstream agent platform.

    Dùng blocking httpx.Client + ddddocr OCR (CPU-bound).
    Gọi từ async code qua asyncio.to_thread().
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._login_url = f"{self._base_url}/agent/login"
        self._client: Optional[httpx.Client] = None
        self._public_key: Optional[str] = None
        self._captcha_url: Optional[str] = None
        self._ocr = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=HTTP_TIMEOUT,
                headers=_HEADERS,
                follow_redirects=False,
            )
        return self._client

    def _get_ocr(self):
        if self._ocr is None:
            import ddddocr  # lazy import — nặng, chỉ load khi cần

            self._ocr = ddddocr.DdddOcr(show_ad=False)
        return self._ocr

    @staticmethod
    def _rsa_encrypt(plain_text: str, public_key_pem: str) -> str:
        """RSA PKCS1v15 encrypt — tương thích JSEncrypt của upstream."""
        key_data = (
            public_key_pem
            .replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        lines = [key_data[i : i + 64] for i in range(0, len(key_data), 64)]
        pem = (
            "-----BEGIN PUBLIC KEY-----\n"
            + "\n".join(lines)
            + "\n-----END PUBLIC KEY-----\n"
        ).encode()
        public_key = serialization.load_pem_public_key(pem)
        encrypted = public_key.encrypt(plain_text.encode("utf-8"), padding.PKCS1v15())
        return base64.b64encode(encrypted).decode("utf-8")

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
        self._ocr = None

    # ─── Init ────────────────────────────────────────────────────────────────

    def init_login(self) -> tuple[bool, str]:
        """Gọi scene=init để lấy public_key + captcha_url."""
        client = self._get_client()
        try:
            resp = client.post(self._login_url, json={"scene": "init"})
            if resp.status_code != 200:
                return False, f"HTTP {resp.status_code}"
            data = resp.json().get("data", {})
            self._public_key = data.get("public_key", "")
            self._captcha_url = data.get("captcha_url", "")
            if not self._public_key:
                return False, "Không lấy được public key"
            if not self._captcha_url:
                return False, "Không lấy được captcha URL"
            logger.info("Init OK: captcha_url=%s", self._captcha_url)
            return True, "Init thành công"
        except (httpx.HTTPError, ValueError) as e:
            return False, f"Lỗi kết nối: {e}"

    # ─── Captcha ─────────────────────────────────────────────────────────────

    def get_captcha_image(self) -> tuple[bool, bytes, str]:
        """Tải ảnh captcha."""
        if not self._captcha_url:
            ok, msg = self.init_login()
            if not ok:
                return False, b"", msg
        client = self._get_client()
        url = (
            self._captcha_url
            if not (self._captcha_url or "").startswith("/")
            else f"{self._base_url}{self._captcha_url}"
        )
        try:
            resp = client.get(url)
            if resp.status_code != 200:
                return False, b"", f"HTTP {resp.status_code}"
            if "image" not in resp.headers.get("Content-Type", ""):
                return False, b"", "Response không phải ảnh"
            return True, resp.content, ""
        except (httpx.HTTPError, ValueError) as e:
            return False, b"", f"Lỗi tải captcha: {e}"

    # Bảng map ký tự OCR hay nhầm → số tương ứng
    _OCR_CHAR_MAP: dict[str, str] = {
        "o": "0", "O": "0", "口": "0", "D": "0", "Q": "0",
        "l": "1", "I": "1", "i": "1", "|": "1", "1": "1",
        "z": "2", "Z": "2",
        "e": "3", "E": "3",
        "A": "4", "a": "4",
        "s": "5", "S": "5",
        "b": "6", "G": "6",
        "T": "7", "t": "7",
        "B": "8",
        "g": "9", "q": "9", "p": "9", "P": "9",
    }

    def _preprocess_image(self, image_bytes: bytes) -> bytes:
        """Tiền xử lý ảnh: grayscale + tăng contrast + sharpen để OCR chính xác hơn."""
        try:
            import io

            from PIL import Image, ImageEnhance, ImageFilter

            img = Image.open(io.BytesIO(image_bytes)).convert("L")
            w, h = img.size
            if w < 120:
                img = img.resize((w * 2, h * 2), Image.LANCZOS)
            img = ImageEnhance.Contrast(img).enhance(2.5)
            img = img.filter(ImageFilter.SHARPEN)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception:
            return image_bytes

    def _clean_ocr(self, raw: str) -> str:
        """Chuẩn hoá chuỗi OCR — map ký tự dễ nhầm, giữ lại alnum ASCII."""
        cleaned = ""
        for c in raw:
            if c.isdigit() and c.isascii():
                cleaned += c
            elif c in self._OCR_CHAR_MAP:
                cleaned += self._OCR_CHAR_MAP[c]
            elif c.isascii() and c.isalnum():
                cleaned += c
        return cleaned

    def solve_captcha(self, image_bytes: bytes) -> tuple[bool, str, str]:
        """Giải captcha: thử raw + preprocessed, chọn kết quả có nhiều digit hơn."""
        try:
            ocr = self._get_ocr()

            raw1 = ocr.classification(image_bytes)
            cleaned1 = self._clean_ocr(raw1)

            processed = self._preprocess_image(image_bytes)
            raw2 = ocr.classification(processed)
            cleaned2 = self._clean_ocr(raw2)

            # Ưu tiên kết quả có nhiều ký tự số hơn
            digits1 = sum(1 for c in cleaned1 if c.isdigit())
            digits2 = sum(1 for c in cleaned2 if c.isdigit())
            cleaned = cleaned1 if digits1 >= digits2 else cleaned2
            raw = raw1 if digits1 >= digits2 else raw2

            if not cleaned:
                return False, "", "OCR trả về rỗng"
            logger.info(
                "Captcha solved: %s -> %s (raw2=%s->%s)",
                raw1, cleaned1, raw2, cleaned2,
            )
            logger.info("Chosen: %s -> %s", raw, cleaned)
            return True, cleaned, ""
        except ImportError:
            return False, "", "ddddocr chưa cài. Chạy: pip install ddddocr"
        except Exception as e:
            logger.error("Captcha solve error: %s", e)
            return False, "", f"Lỗi giải captcha: {e}"

    # ─── Login ───────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_response_cookies(resp: httpx.Response) -> dict:
        """Trích Set-Cookie từ response headers — không phụ thuộc client jar."""
        cookies: dict = {}
        for raw in resp.headers.get_list("set-cookie"):
            # Chỉ lấy phần name=value (trước dấu ';')
            part = raw.split(";", 1)[0].strip()
            if "=" in part:
                k, v = part.split("=", 1)
                cookies[k.strip()] = v.strip()
        return cookies

    def login(self, username: str, password: str) -> tuple[bool, str, dict]:
        """Đăng nhập tự động: init → captcha → RSA encrypt → POST login.

        Mỗi lần thử tạo httpx.Client MỚI (clear cookie jar) để tránh
        cookies cũ từ lần thử trước gây xung đột.

        Returns:
            (success, message, cookies_dict)
        """
        for attempt in range(1, MAX_CAPTCHA_ATTEMPTS + 1):
            logger.info("Login attempt %d/%d", attempt, MAX_CAPTCHA_ATTEMPTS)

            # Tạo client mới mỗi lần thử → clear cookie jar hoàn toàn
            if self._client:
                self._client.close()
                self._client = None
            self._public_key = None
            self._captcha_url = None

            client = self._get_client()

            # Luôn lấy public_key + captcha_url mới cho mỗi lần thử
            ok, msg = self.init_login()
            if not ok:
                logger.warning("init_login failed (attempt %d): %s", attempt, msg)
                continue

            ok, image, err = self.get_captcha_image()
            if not ok:
                logger.warning("get_captcha failed (attempt %d): %s", attempt, err)
                continue

            ok, captcha_code, err = self.solve_captcha(image)
            if not ok:
                logger.warning("solve_captcha failed (attempt %d): %s", attempt, err)
                continue

            try:
                encrypted_password = self._rsa_encrypt(password, self._public_key)
            except Exception as e:
                logger.error("RSA encryption failed: %s", e)
                return False, f"Lỗi mã hóa mật khẩu: {e}", {}

            try:
                resp = client.post(
                    self._login_url,
                    json={
                        "username": username,
                        "password": encrypted_password,
                        "captcha": captcha_code,
                        "scene": "login",
                    },
                )
                result = self._parse_login_response(resp, attempt)
                if result["success"]:
                    # Thu thập cookies từ 2 nguồn:
                    # 1) Client jar (tích lũy từ init + captcha + login)
                    # 2) Set-Cookie headers của login response
                    jar_cookies = dict(client.cookies)
                    resp_cookies = self._extract_response_cookies(resp)
                    # Merge: response cookies ghi đè jar (mới hơn)
                    all_cookies = {**jar_cookies, **resp_cookies}
                    logger.info(
                        "Login OK: jar=%d cookies, resp=%d cookies, merged=%d cookies",
                        len(jar_cookies), len(resp_cookies), len(all_cookies),
                    )
                    logger.info(
                        "Cookie keys: %s", list(all_cookies.keys()),
                    )
                    return True, "Đăng nhập thành công", all_cookies
                if not result["retry"]:
                    return False, result["message"], {}
                logger.warning("Attempt %d: %s", attempt, result["message"])
            except (httpx.HTTPError, ValueError) as e:
                logger.error("Login request error: %s", e)
                return False, f"Lỗi kết nối: {e}", {}

        return False, f"Thất bại sau {MAX_CAPTCHA_ATTEMPTS} lần thử", {}

    def _parse_login_response(self, resp: httpx.Response, attempt: int) -> dict:
        try:
            data = resp.json()
            code = data.get("code", -1)
            msg = data.get("msg", "")
            if code == 1:
                return {"success": True, "message": msg or "OK", "retry": False}
            msg_lower = str(msg).lower()
            # Captcha sai → retry
            if any(
                kw in msg_lower
                for kw in (
                    "captcha", "xac nhan", "xác nhận",
                    "ma xac", "mã xác", "verify", "验证码",
                )
            ):
                return {"success": False, "message": msg, "retry": True}
            # Sai tài khoản/mật khẩu → không retry
            if any(
                kw in msg_lower
                for kw in (
                    "password", "mat khau", "mật khẩu", "密码", "pwd",
                    "tai khoan", "tài khoản", "account", "用户",
                    "khong ton tai", "không chính xác",
                )
            ):
                return {"success": False, "message": msg, "retry": False}
            return {"success": False, "message": msg or f"Lỗi (code={code})", "retry": True}
        except (ValueError, KeyError):
            return {"success": False, "message": f"HTTP {resp.status_code}", "retry": False}

    # ─── Cookie validation ───────────────────────────────────────────────────

    def check_cookies_live(self, cookies_dict: dict) -> tuple[bool, str]:
        """Kiểm tra cookie còn hiệu lực không (302 → login = hết hạn).

        Dùng client riêng biệt (không dính jar cũ) để check chính xác.
        """
        with httpx.Client(
            timeout=HTTP_TIMEOUT,
            headers=_HEADERS,
            follow_redirects=False,
        ) as check_client:
            try:
                resp = check_client.get(
                    f"{self._base_url}/",
                    cookies=cookies_dict,
                )
                logger.info(
                    "check_cookies_live: HTTP %d, Location=%s",
                    resp.status_code,
                    resp.headers.get("Location", "N/A"),
                )
                if resp.status_code == 302:
                    loc = resp.headers.get("Location", "").lower()
                    if "login" in loc:
                        return False, "Cookie đã hết hạn"
                if resp.status_code == 200:
                    return True, "Cookie còn hiệu lực"
                return False, f"HTTP {resp.status_code}"
            except httpx.TimeoutException:
                return False, "Timeout"
            except httpx.ConnectError:
                return False, "Không thể kết nối"
            except httpx.HTTPError as e:
                return False, f"Lỗi: {e}"

    def ensure_valid_cookies(
        self,
        username: str,
        password: str,
        current_cookies: dict,
    ) -> tuple[bool, str, dict]:
        """Đảm bảo cookie hợp lệ. Tự động re-login nếu hết hạn.

        Returns:
            (success, message, cookies_dict)
        """
        if current_cookies:
            is_valid, msg = self.check_cookies_live(current_cookies)
            if is_valid:
                return True, "Cookie còn hiệu lực", current_cookies
            logger.info("Cookies expired: %s — re-logging in", msg)
        # login() sẽ tự tạo client mới, clear jar
        return self.login(username, password)
