# Backend API

REST API xây dựng với **FastAPI** + **PostgreSQL** + **Redis** + **JWT Authentication**.

## Cấu trúc thư mục

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Entry point - khởi tạo FastAPI app
│   ├── core/
│   │   ├── config.py            # Cấu hình ứng dụng (đọc từ .env)
│   │   ├── security.py          # JWT token, bcrypt password, authenticate, blacklist
│   │   └── dependencies.py      # Dependency injection (get_current_user, get_superuser)
│   ├── db/
│   │   ├── base.py              # SQLAlchemy Base model
│   │   └── session.py           # Async engine, session factory, Redis connection
│   ├── models/
│   │   ├── __init__.py          # Export tất cả models
│   │   ├── user.py              # User ORM model (soft delete)
│   │   └── token_blacklist.py   # Token blacklist model
│   ├── schemas/
│   │   ├── user.py              # Pydantic schemas (UserCreate, UserRead, UserUpdate)
│   │   └── token.py             # Token schemas (Token, TokenData)
│   ├── services/
│   │   └── user_service.py      # Business logic mở rộng
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Gom tất cả routes
│   │       └── endpoints/
│   │           ├── health.py    # Health check
│   │           ├── auth.py      # Đăng ký, đăng nhập, refresh, đăng xuất
│   │           └── users.py     # CRUD users (list, me, get, update, delete)
│   └── utils/                   # Tiện ích dùng chung
├── tests/
│   ├── conftest.py              # Pytest fixtures (async client)
│   └── api/                     # Test cho từng endpoint
├── migrations/
│   └── versions/                # Alembic migration files
├── .env.example                 # Mẫu biến môi trường
├── .gitignore
├── alembic.ini                  # Cấu hình Alembic migration
├── docker-compose.yml           # Docker services (app, PostgreSQL, Redis)
├── Dockerfile
├── requirements.txt             # Thư viện Python
└── README.md
```

## Yêu cầu hệ thống

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (tùy chọn)

## Cài đặt

### 1. Tạo môi trường ảo

```bash
cd Backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 2. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường

```bash
cp .env.example .env
# Sửa file .env theo cấu hình thực tế
```

### 4. Khởi tạo database

```bash
alembic upgrade head
```

### 5. Chạy ứng dụng

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Truy cập API docs tại: http://localhost:8000/docs

## Chạy với Docker

```bash
docker-compose up -d
```

Lệnh trên sẽ khởi chạy 3 services:
- **app** - FastAPI server tại port `8000`
- **db** - PostgreSQL tại port `5432`
- **redis** - Redis tại port `6379`

## Authentication Flow

### Dual Token System

Hệ thống sử dụng **2 loại token** theo pattern của boilerplate:

| Token | Lưu trữ | Thời hạn | Mục đích |
|-------|---------|----------|----------|
| Access Token | Client (Authorization header) | 60 phút | Xác thực request |
| Refresh Token | HTTPOnly Cookie | 30 ngày | Làm mới access token |

### Flow hoạt động

```
1. POST /auth/register  → Tạo tài khoản mới
2. POST /auth/login     → Nhận access_token + refresh_token (cookie)
3. GET  /users/me       → Gửi Bearer token → Nhận thông tin user
4. POST /auth/refresh   → Tự động đọc cookie → Nhận access_token mới
5. POST /auth/logout    → Blacklist cả 2 token + xóa cookie
```

### Token Blacklist

Khi logout, cả access token và refresh token đều được lưu vào bảng `token_blacklist`. Mỗi lần verify token, hệ thống kiểm tra blacklist trước khi decode.

### Password Hashing

Sử dụng **bcrypt** với automatic salt generation (cost factor 12).

## API Endpoints

### Auth (`/api/v1/auth`)

| Method | Endpoint    | Auth | Mô tả                              |
|--------|-------------|------|-------------------------------------|
| POST   | `/register` | No   | Đăng ký (name, username, email, password) |
| POST   | `/login`    | No   | Đăng nhập (OAuth2 form: username + password) |
| POST   | `/refresh`  | No   | Làm mới access token từ cookie     |
| POST   | `/logout`   | Yes  | Đăng xuất, blacklist tokens         |

### Users (`/api/v1/users`)

| Method | Endpoint      | Auth  | Mô tả                    |
|--------|---------------|-------|---------------------------|
| GET    | `/`           | No    | Danh sách users (phân trang) |
| GET    | `/me`         | Yes   | Thông tin user hiện tại   |
| GET    | `/{user_id}`  | No    | Chi tiết user theo ID     |
| PATCH  | `/{user_id}`  | Yes   | Cập nhật user (chủ sở hữu hoặc admin) |
| DELETE | `/{user_id}`  | Yes   | Soft delete (chủ sở hữu hoặc admin) |
| DELETE | `/hard/{user_id}` | Admin | Xóa vĩnh viễn (superuser only) |

### Health (`/api/v1/health`)

| Method | Endpoint | Mô tả       |
|--------|----------|-------------|
| GET    | `/`      | Health check |

## Tech Stack

| Thành phần     | Công nghệ                        |
|----------------|-----------------------------------|
| Framework      | FastAPI                           |
| ORM            | SQLAlchemy 2.0 (async)            |
| Database       | PostgreSQL + asyncpg              |
| Cache          | Redis                             |
| Authentication | JWT (PyJWT) + bcrypt              |
| Token Storage  | Access: Bearer header, Refresh: HTTPOnly cookie |
| Token Blacklist| PostgreSQL table                  |
| Migration      | Alembic                           |
| Validation     | Pydantic v2                       |
| Testing        | pytest + pytest-asyncio + httpx   |
| Deploy         | Docker + Docker Compose           |

## Testing

```bash
pytest
```

## Tính năng bảo mật

- Dual token (access + refresh) với thời hạn riêng biệt
- Refresh token lưu trong HTTPOnly cookie (chống XSS)
- Token blacklist khi logout (chống token reuse)
- Bcrypt password hashing với auto salt
- Soft delete user (giữ lại dữ liệu)
- Authorization: chỉ chủ sở hữu hoặc superuser mới được sửa/xóa
- Input validation qua Pydantic schemas
- CORS middleware cấu hình từ .env
