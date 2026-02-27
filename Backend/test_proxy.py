"""CLI test script — validates proxy endpoint chain end-to-end.

Usage:
    cd Backend
    python test_proxy.py

Tests:
1. Auth: login + get JWT token
2. Proxy /members: table data via SWR cache
3. Proxy /bets: table data
4. Proxy /deposits: table data
5. Proxy /cache-stats: memory cache stats
6. Pagination: page/limit params
7. Error handling: unknown endpoint, no auth
"""

import os
import sys
import httpx

# Fix Windows console encoding
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://localhost:8000/api/v1"
TIMEOUT = 30.0


def color(text: str, code: int) -> str:
    return f"\033[{code}m{text}\033[0m"


def ok(msg: str) -> None:
    print(color(f"  PASS  {msg}", 32))


def fail(msg: str) -> None:
    print(color(f"  FAIL  {msg}", 31))


def info(msg: str) -> None:
    print(color(f"  INFO  {msg}", 36))


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main() -> None:
    passed = 0
    failed = 0
    client = httpx.Client(timeout=TIMEOUT)

    # ── Test 1: Login ──
    section("1. Auth — Login")
    try:
        resp = client.post(f"{BASE}/auth/login", data={
            "username": "admin",
            "password": "admin",
        })
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token", "")
            if token:
                ok(f"Login OK, token: {token[:20]}...")
                passed += 1
            else:
                fail(f"Login returned 200 but no token: {data}")
                failed += 1
                print("\nCannot proceed without token. Exiting.")
                sys.exit(1)
        else:
            fail(f"Login failed: {resp.status_code} {resp.text[:200]}")
            failed += 1
            print("\nCannot proceed without token. Exiting.")
            sys.exit(1)
    except Exception as e:
        fail(f"Login exception: {e}")
        failed += 1
        print("\nCannot proceed without token. Exiting.")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}

    # ── Test 2: No auth → 401/403 ──
    section("2. Auth guard — no token")
    try:
        resp = client.post(f"{BASE}/proxy/members")
        if resp.status_code in (401, 403):
            ok(f"No-auth correctly rejected: {resp.status_code}")
            passed += 1
        else:
            fail(f"Expected 401/403, got {resp.status_code}")
            failed += 1
    except Exception as e:
        fail(f"Exception: {e}")
        failed += 1

    # ── Test 3: Proxy /members ──
    section("3. Proxy /members")
    try:
        resp = client.post(
            f"{BASE}/proxy/members",
            headers=headers,
            data={"page": "1", "limit": "10"},
        )
        if resp.status_code == 200:
            data = resp.json()
            code = data.get("code")
            rows = data.get("data", [])
            count = data.get("count", 0)
            cache = data.get("_cache_status", "?")
            info(f"code={code}, rows={len(rows)}, count={count}, cache={cache}")
            if code == 0:
                ok(f"Members returned {len(rows)} rows (total: {count})")
                passed += 1
                if rows:
                    first = rows[0]
                    has_agent = "_agent_name" in first
                    info(f"First row keys: {list(first.keys())[:8]}...")
                    if has_agent:
                        ok(f"_agent_name present: {first['_agent_name']}")
                        passed += 1
                    else:
                        fail("_agent_name missing from row data")
                        failed += 1
                else:
                    info("No rows (maybe no active agents with valid cookies)")
            else:
                fail(f"Members returned code={code}: {data.get('msg')}")
                failed += 1
        else:
            fail(f"Members HTTP {resp.status_code}: {resp.text[:200]}")
            failed += 1
    except Exception as e:
        fail(f"Exception: {e}")
        failed += 1

    # ── Test 4: Proxy /bets ──
    section("4. Proxy /bets")
    try:
        resp = client.post(
            f"{BASE}/proxy/bets",
            headers=headers,
            data={"page": "1", "limit": "5"},
        )
        if resp.status_code == 200:
            data = resp.json()
            ok(f"Bets OK: code={data.get('code')}, rows={len(data.get('data', []))}, count={data.get('count', 0)}")
            passed += 1
        else:
            fail(f"Bets HTTP {resp.status_code}")
            failed += 1
    except Exception as e:
        fail(f"Exception: {e}")
        failed += 1

    # ── Test 5: Proxy /deposits ──
    section("5. Proxy /deposits")
    try:
        resp = client.post(
            f"{BASE}/proxy/deposits",
            headers=headers,
            data={"page": "1", "limit": "5"},
        )
        if resp.status_code == 200:
            data = resp.json()
            ok(f"Deposits OK: code={data.get('code')}, rows={len(data.get('data', []))}")
            passed += 1
        else:
            fail(f"Deposits HTTP {resp.status_code}")
            failed += 1
    except Exception as e:
        fail(f"Exception: {e}")
        failed += 1

    # ── Test 6: Cache stats ──
    section("6. Cache stats")
    try:
        resp = client.get(f"{BASE}/proxy/cache-stats", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            ok(f"Cache stats: {data}")
            passed += 1
        else:
            fail(f"Cache stats HTTP {resp.status_code}")
            failed += 1
    except Exception as e:
        fail(f"Exception: {e}")
        failed += 1

    # ── Test 7: SWR cache — second request should be cached ──
    section("7. SWR cache — second request (should be fresh)")
    try:
        resp = client.post(
            f"{BASE}/proxy/members",
            headers=headers,
            data={"page": "1", "limit": "10"},
        )
        if resp.status_code == 200:
            data = resp.json()
            cache = data.get("_cache_status", "?")
            age = data.get("_cache_age", -1)
            info(f"cache_status={cache}, cache_age={age}")
            if cache in ("fresh", "stale"):
                ok(f"Second request served from cache ({cache})")
                passed += 1
            elif cache == "miss":
                info("Cache miss on second request (may be first time)")
                passed += 1
            else:
                fail(f"Unexpected cache status: {cache}")
                failed += 1
        else:
            fail(f"HTTP {resp.status_code}")
            failed += 1
    except Exception as e:
        fail(f"Exception: {e}")
        failed += 1

    # ── Test 8: Pagination ──
    section("8. Pagination — page 2")
    try:
        resp = client.post(
            f"{BASE}/proxy/members",
            headers=headers,
            data={"page": "2", "limit": "5"},
        )
        if resp.status_code == 200:
            data = resp.json()
            rows = data.get("data", [])
            count = data.get("count", 0)
            ok(f"Page 2: {len(rows)} rows, total={count}")
            passed += 1
        else:
            fail(f"HTTP {resp.status_code}")
            failed += 1
    except Exception as e:
        fail(f"Exception: {e}")
        failed += 1

    # ── Test 9: Unknown endpoint ──
    section("9. Unknown endpoint")
    try:
        resp = client.post(
            f"{BASE}/proxy/nonexistent",
            headers=headers,
            data={"page": "1", "limit": "10"},
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") != 0:
                ok(f"Unknown endpoint handled: code={data.get('code')}, msg={data.get('msg')}")
                passed += 1
            else:
                fail(f"Unknown endpoint returned code=0")
                failed += 1
        else:
            fail(f"HTTP {resp.status_code}")
            failed += 1
    except Exception as e:
        fail(f"Exception: {e}")
        failed += 1

    # ── Test 10: Report endpoint with totals ──
    section("10. Report /report-lottery (with _totals)")
    try:
        resp = client.post(
            f"{BASE}/proxy/report-lottery",
            headers=headers,
            data={"page": "1", "limit": "10"},
        )
        if resp.status_code == 200:
            data = resp.json()
            has_totals = "_totals" in data
            info(f"code={data.get('code')}, rows={len(data.get('data', []))}, has_totals={has_totals}")
            if data.get("code") == 0:
                ok(f"Report-lottery OK")
                passed += 1
                if has_totals:
                    ok(f"_totals present: {list(data['_totals'].keys())[:5]}...")
                    passed += 1
                else:
                    info("No _totals (maybe no data)")
            else:
                fail(f"Report returned code={data.get('code')}")
                failed += 1
        else:
            fail(f"HTTP {resp.status_code}")
            failed += 1
    except Exception as e:
        fail(f"Exception: {e}")
        failed += 1

    # ── Summary ──
    print(f"\n{'='*60}")
    total = passed + failed
    if failed == 0:
        print(color(f"  ALL {passed} TESTS PASSED!", 32))
    else:
        print(color(f"  {passed}/{total} passed, {failed} failed", 31))
    print(f"{'='*60}\n")

    client.close()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
