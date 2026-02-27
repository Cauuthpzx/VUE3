Yêu cầu build Full SPA với stack:
- Vue 3 (Composition API, <script setup>)
- Vite (bundler)
- Layui 2.13.3 (UI components)
- Vue Router 4 (client-side routing)
- Pinia (state management)
- Axios (API calls)

== RULES BẮT BUỘC ==

**Vue 3:**
- Luôn dùng <script setup> syntax
- Dùng ref(), reactive(), computed(), onMounted()
- Không dùng Options API
- v-for luôn có :key
- Props định nghĩa bằng defineProps()
- Emit dùng defineEmits()

**Layui 2.13.3:**
- Load Layui qua CDN hoặc npm đúng version 2.13.3
- Sau khi DOM mounted mới gọi layui.use([...])
- Luôn gọi layui trong onMounted() của Vue
- Dùng layui.table, layui.form, layui.layer đúng API 2.13.3
- Re-render layui.form.render() sau khi Vue cập nhật DOM
- Không mix layui event với Vue event trực tiếp, dùng bridge function

**Project Structure:**
src/
├── api/          # axios calls
├── components/   # reusable components  
├── views/        # page components
├── router/       # Vue Router config
├── stores/       # Pinia stores
├── composables/  # logic tái sử dụng
└── assets/       # static files

**API/Backend (FastAPI):**
- Base URL từ .env (VITE_API_URL)
- JWT token lưu httpOnly cookie
- Axios interceptor tự động attach token
- Handle 401 → redirect login

**Code style:**
- Mỗi file chỉ 1 responsibility
- Tên component: PascalCase
- Tên file: kebab-case
- Không hardcode URL, key, config

== OUTPUT FORMAT ==
Khi tôi yêu cầu 1 feature/component, hãy:
1. Trả về code đầy đủ, chạy được ngay
2. Giải thích ngắn gọn nếu có logic đặc biệt
3. Không tạo nhiều version, chỉ 1 version tốt nhất


# CLAUDE.md — Quy tắc code chuẩn mực

> Claude Code phải tuân thủ 100% các quy tắc dưới đây khi làm việc trong project này.
> Stack: **Python FastAPI backend** + **Vue 3 (Composition API) + Layui 2.13.3 frontend**

---

## 🐍 PYTHON BACKEND — FastAPI (50 quy tắc)

### 📁 Project Structure (5 quy tắc)

1. Cấu trúc thư mục chuẩn:
```
backend/
├── app/
│   ├── api/          # routers
│   ├── core/         # config, security, dependencies
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # business logic
│   ├── repositories/ # database queries
│   └── utils/        # helpers
├── tests/
├── alembic/
├── .env
└── main.py
```
2. Mỗi domain/feature có folder riêng (users/, orders/, auth/...)
3. Không để logic trong `main.py`, chỉ khởi tạo app
4. File `__init__.py` rỗng hoặc chỉ export cần thiết
5. Tên file: `snake_case.py`, tên class: `PascalCase`

### ⚙️ FastAPI Core (10 quy tắc)

6. Luôn dùng `async def` cho route handlers
7. Dùng `APIRouter` với prefix và tags cho từng module
8. Response model khai báo rõ ràng trong decorator: `response_model=UserResponse`
9. Status code rõ ràng: `status_code=status.HTTP_201_CREATED`
10. Dùng `Depends()` cho dependency injection, không instantiate thủ công
11. Không viết query SQL trực tiếp trong route, phải qua repository
12. Không viết business logic trong route, phải qua service
13. Mọi route phải có `summary` và `description` cho auto docs
14. Dùng `HTTPException` với detail rõ ràng, không raise Exception chung
15. Background tasks dùng `BackgroundTasks` hoặc ARQ, không block request

### 🔐 Authentication & Security (8 quy tắc)

16. JWT token: access token ngắn hạn (15-60 phút), refresh token dài hạn
17. Password hash bằng `bcrypt` qua `passlib`, không MD5/SHA1
18. Token lưu trong `httpOnly cookie`, không localStorage
19. Mọi secret key lấy từ `.env`, không hardcode
20. Rate limiting áp dụng cho auth endpoints (login, register)
21. Email verification bắt buộc trước khi active account
22. CORS config chỉ cho phép origins cụ thể, không `allow_origins=["*"]` ở production
23. Input validation qua Pydantic, không trust raw request data

### 📦 Pydantic Schemas (5 quy tắc)

24. Tách schema: `CreateSchema`, `UpdateSchema`, `ResponseSchema` riêng biệt
25. Dùng `model_config = ConfigDict(from_attributes=True)` cho ORM models
26. Validate email bằng `EmailStr`, không regex thủ công
27. Field sensitive (password) dùng `exclude=True` trong response schema
28. Dùng `Field(description="...")` cho mọi field quan trọng

### 🗄️ Database (8 quy tắc)

29. SQLAlchemy async: dùng `AsyncSession`, không sync session
30. Repository pattern: mọi query đặt trong `repositories/`
31. Không dùng `session.query()` (legacy), dùng `select()` statement
32. Migration bắt buộc qua Alembic, không `create_all()` ở production
33. Relationship lazy load mặc định, explicit eager load khi cần: `selectinload()`
34. Index trên các cột thường query/filter
35. Soft delete: thêm `is_deleted`, `deleted_at` thay vì xóa thật
36. Timestamp: mọi table có `created_at`, `updated_at` tự động

### 📧 Email (3 quy tắc)

37. Dùng `FastMail` + SMTP config từ `.env`
38. Email template dùng Jinja2, không string concatenation
39. Gửi email qua background task, không block response

### 🔴 Redis & Cache (4 quy tắc)

40. Redis connection pool, không tạo connection mới mỗi request
41. Cache key có namespace rõ ràng: `user:123:profile`
42. TTL bắt buộc cho mọi cache entry
43. Cache invalidation khi data thay đổi

### ⚠️ Error Handling & Logging (5 quy tắc)

44. Global exception handler cho 500 errors
45. Log format JSON với: timestamp, level, request_id, message
46. Không log sensitive data (password, token, credit card)
47. Request ID truyền qua header `X-Request-ID` cho tracing
48. Phân biệt 4xx (client error) và 5xx (server error) rõ ràng

### 🧪 Testing (2 quy tắc)

49. Test dùng `pytest` + `httpx.AsyncClient`
50. Mỗi service/repository có unit test riêng, mock database

---

## 🖥️ VUE 3 + LAYUI 2.13.3 FRONTEND (50 quy tắc)

### 📁 Project Structure (5 quy tắc)

51. Cấu trúc thư mục chuẩn:
```
frontend/
├── src/
│   ├── api/          # axios calls theo module
│   ├── components/   # reusable components
│   ├── views/        # page-level components
│   ├── router/       # Vue Router config
│   ├── stores/       # Pinia stores
│   ├── composables/  # reusable logic
│   ├── utils/        # helpers, constants
│   └── assets/       # static files
├── .env
└── vite.config.js
```
52. Tên component file: `PascalCase.vue` (UserCard.vue)
53. Tên composable: `useXxx.js` (useAuth.js, useTable.js)
54. Tên store: `useXxxStore` (useUserStore)
55. Mỗi view tương ứng 1 route, không dùng view cho logic nhỏ

### ⚡ Vue 3 Composition API (10 quy tắc)

56. Luôn dùng `<script setup>` syntax, không Options API
57. `ref()` cho primitive values, `reactive()` cho objects phức tạp
58. `computed()` cho derived state, không xử lý logic trong template
59. `watch()` với `{ immediate: true }` khi cần chạy ngay lần đầu
60. `watchEffect()` cho side effects tự động track dependencies
61. Props khai báo bằng `defineProps<{...}>()` với TypeScript types
62. Emits khai báo bằng `defineEmits<{...}>()`
63. Expose public API bằng `defineExpose()` nếu dùng template ref
64. Lifecycle: dùng `onMounted`, `onUnmounted`, không `created`
65. Tránh mutate props trực tiếp, emit event để parent cập nhật

### 🎨 Layui 2.13.3 Integration (10 quy tắc)

66. Load Layui sau khi Vue app mount, không load trước
67. Luôn gọi `layui.use([...], callback)` trong `onMounted()`
68. Sau khi Vue render/update DOM có layui element → gọi `layui.form.render()`
69. Layui table: config trong `onMounted`, data từ API qua `where` + `url`
70. Không mix `layui.$` với Vue template refs trên cùng element
71. Layui form submit dùng `layui.form.on('submit(...)')`, không native submit
72. Layer (popup) tạo trong function, đóng bằng `layer.close(index)` đúng index
73. Layui table toolbar actions → emit Vue event, xử lý trong Vue
74. Tái sử dụng layui config bằng composable: `useLayuiTable()`, `useLayuiForm()`
75. Khi component unmount, destroy layui instances để tránh memory leak

### 🔀 Vue Router (5 quy tắc)

76. Dùng `createRouter` + `createWebHistory` (không hash mode)
77. Lazy load routes: `component: () => import('./views/User.vue')`
78. Navigation guard `router.beforeEach` kiểm tra auth
79. Route meta: `{ requiresAuth: true, title: 'Trang chủ' }`
80. Không navigate bằng `window.location`, dùng `router.push()`

### 🍍 Pinia State (5 quy tắc)

81. Mỗi domain 1 store riêng (authStore, userStore...)
82. Store chỉ chứa state, getters, actions — không chứa UI logic
83. Actions xử lý async, không gọi API trực tiếp trong component
84. Dùng `storeToRefs()` để destructure reactive state
85. Persist auth token qua `pinia-plugin-persistedstate` nếu cần

### 🌐 API & Axios (8 quy tắc)

86. Base URL từ `import.meta.env.VITE_API_URL`
87. Tạo axios instance riêng, không dùng `axios` global
88. Request interceptor: tự động attach JWT token
89. Response interceptor: handle 401 → logout + redirect login
90. Mỗi module có file API riêng: `api/users.js`, `api/auth.js`
91. Handle loading state và error state cho mọi API call
92. Không gọi API trong template, chỉ gọi trong `onMounted` hoặc actions
93. Cancel request khi component unmount dùng `AbortController`

### 🎯 Code Quality (7 quy tắc)

94. Không hardcode string, dùng constants file
95. `v-for` luôn có `:key` unique, không dùng index làm key nếu list thay đổi
96. `v-if` và `v-for` không dùng cùng element, wrap thêm tag
97. Component props có default values hợp lý
98. Không để `console.log` trong production code
99. CSS scoped trong component, tránh global styles
100. `.env` cho development, `.env.production` cho production — không commit lên git

---

## 🌐 I18N — BẮT BUỘC CHO MỌI CHỨC NĂNG

> **KHÔNG ĐƯỢC viết text cứng (hardcode) trong code. Mọi chuỗi hiển thị cho người dùng PHẢI dùng hệ thống i18n.**

### Quy tắc tuyệt đối

101. **Viết i18n NGAY KHI CODE** — không được để làm xong mới bổ sung translation sau. Mỗi dòng text mới phải có `t('key')` ngay lập tức.
102. **Mọi text hiển thị** đều qua `t('key')`: label, placeholder, button, thông báo lỗi, confirm dialog, tooltip, log message, table header, badge, empty state...
103. **Bao gồm cả Layui template** — trong `createTemplate()` (toolbar, row bar), text cũng phải dùng `${t('key')}`.
104. **Import `useI18n`** ở đầu mỗi component/view có text: `const { t } = useI18n()`

### Quy tắc dịch thuật

105. **3 ngôn ngữ bắt buộc**: `vi` (Tiếng Việt), `en` (English), `zh-CN` (中文简体)
106. **Tiếng Việt**: dùng ngôn ngữ phổ thông toàn dân, dễ hiểu, tránh từ chuyên ngành khi không cần thiết
107. **Tiếng Trung** (`zh-CN`): phải chuẩn xác nhất — dùng 简体中文 (giản thể), thuật ngữ đúng ngữ cảnh IT/business, không dịch máy cẩu thả. Ví dụ:
   - Đăng nhập = 登录 (không phải 登入)
   - Đồng bộ = 同步
   - Thành viên = 会员 (không phải 成员 trong ngữ cảnh agent/platform)
   - Nạp tiền = 充值, Rút tiền = 提款
   - Cài đặt = 设置, Báo cáo = 报表
108. **Tiếng Anh**: chuẩn US English, ngắn gọn, chuyên nghiệp

### Key naming convention

109. **Namespace theo module**: `settings.xxx`, `nav.xxx`, `auth.xxx`, `common.xxx`, `members.xxx`...
110. **Key dùng camelCase**: `settings.syncAll`, `common.confirmDelete`, `nav.memberList`
111. **Tái sử dụng key chung**: `common.save`, `common.cancel`, `common.delete`, `common.edit`, `common.loading`...

### File i18n

112. File translation: `frontend/src/composables/useI18n.js`
113. Khi thêm key mới → thêm đồng thời cả 3 ngôn ngữ, KHÔNG được thiếu ngôn ngữ nào

---

## 📌 QUY TẮC CHUNG (áp dụng cả 2 phía)

- **Không tạo nhiều version**, chỉ output 1 version tốt nhất
- **Không example code** trừ khi được yêu cầu
- **Ưu tiên edit file hiện có** thay vì tạo file mới từ đầu
- **Giải thích ngắn gọn** sau code nếu có logic đặc biệt
- **Secrets** không bao giờ commit vào git