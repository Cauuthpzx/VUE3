# Tài liệu Views & Fields Reference

> Tài liệu chi tiết tất cả các trang (views), cột bảng (columns), bộ lọc tìm kiếm (search filters),
> và API fields tương ứng cho toàn bộ hệ thống MaxHUB Agent Management.
> **Cập nhật theo dữ liệu gốc từ site ee88.**

---

## Mục lục

1. [Members - Quản lí hội viên](#1-members---quản-lí-hội-viên)
2. [Invites - Mã giới thiệu](#2-invites---mã-giới-thiệu)
3. [Report Lottery - Báo cáo xổ số](#3-report-lottery---báo-cáo-xổ-số)
4. [Report Funds - Báo cáo tài chính](#4-report-funds---báo-cáo-tài-chính)
5. [Report Provider - Báo cáo nhà cung cấp game](#5-report-provider---báo-cáo-nhà-cung-cấp-game)
6. [Deposits - Nạp rút tiền](#6-deposits---nạp-rút-tiền)
7. [Withdrawals - Lịch sử rút tiền](#7-withdrawals---lịch-sử-rút-tiền)
8. [Bets - Đơn cược xổ số](#8-bets---đơn-cược-xổ-số)
9. [BetThirdParty - Đơn cược bên thứ 3](#9-betthirdparty---đơn-cược-bên-thứ-3)
10. [Tiers - Cấp bậc](#10-tiers---cấp-bậc)
11. [Rebate - Tỷ lệ hoàn trả](#11-rebate---tỷ-lệ-hoàn-trả)
12. [SettingsSync - Đồng bộ Agent](#12-settingssync---đồng-bộ-agent)
13. [SettingsAccount - Quản lý tài khoản](#13-settingsaccount---quản-lý-tài-khoản)
14. [Tools - Công cụ](#14-tools---công-cụ)
15. [Mapping trang gốc ↔ MaxHUB](#15-mapping-trang-gốc--maxhub)

---

## 1. Members - Quản lí hội viên

**Route:** `/members`
**File:** `frontend/src/views/members/MembersView.vue`
**Trang gốc:** `/agent/user.html`
**Layui Table ID:** `membersTable`
**Phân trang:** Có (10, 50, 100, 200)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | `username` | Hội viên | 150 | left | Tên đăng nhập hội viên |
| 2 | `type_format` | Loại hình hội viên | 100 | — | Loại tài khoản (formatted) |
| 3 | `parent_user` | Tài khoản đại lý | 150 | — | Username đại lý cấp trên |
| 4 | `money` | Số dư | 150 | — | Số dư tài khoản |
| 5 | `deposit_count` | Lần nạp | 100 | — | Tổng số lần nạp |
| 6 | `withdrawal_count` | Lần rút | 100 | — | Tổng số lần rút |
| 7 | `deposit_amount` | Tổng tiền nạp | 100 | — | Tổng tiền đã nạp |
| 8 | `withdrawal_amount` | Tổng tiền rút | 100 | — | Tổng tiền đã rút |
| 9 | `login_time` | Lần đăng nhập cuối | 160 | — | Thời gian đăng nhập gần nhất |
| 10 | `register_time` | Thời gian đăng ký | 160 | — | Thời gian đăng ký tài khoản |
| 11 | `status_format` | Trạng thái | 100 | — | 0=Chưa đánh giá, 1=Bình thường, 2=Đóng băng, 3=Khóa |
| 12 | — | Thao tác | 130 | right | toolbar: Cài đặt hoàn trả |

### Row Actions (toolbar: `#membersRowBar`)
- **rebate** — Cài đặt hoàn trả

### Search Filters

| Field | Label | Type | Options |
|-------|-------|------|---------|
| `username` | Hội viên | text | — |
| `first_deposit_time` | Thời gian nạp đầu | date-range | — |
| `status` | Trạng thái | select | `""`: Tất cả, `0`: Chưa đánh giá, `1`: Bình thường, `2`: Đóng băng, `3`: Khóa |
| `sort_field` | Sắp xếp theo | select | `""`: Mặc định, `money`: Số dư, `login_time`: Đăng nhập cuối, `register_time`: Ngày đăng ký, `deposit_money`: Tổng nạp, `withdrawal_money`: Tổng rút |
| `sort_direction` | Sắp xếp theo hướng | select | `asc`: Tăng dần, `desc`: Giảm dần |

### Toolbar Actions
- **add** — Thêm hội viên
- **addAgent** — Đại lý mới thêm

---

## 2. Invites - Mã giới thiệu

**Route:** `/invites`
**File:** `frontend/src/views/members/InvitesView.vue`
**Trang gốc:** `/agent/inviteList.html`
**Layui Table ID:** `invitesTable`
**Phân trang:** Có (10, 50, 100, 200)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | `invite_code` | Mã giới thiệu | — | — | Mã giới thiệu |
| 2 | `user_type` | Loại hình giới thiệu | — | — | Loại người dùng |
| 3 | `reg_count` | Tổng số đã đăng ký | — | — | Số lượt đăng ký qua mã |
| 4 | `scope_reg_count` | Số lượng người dùng đã đăng ký | — | — | Phạm vi đăng ký |
| 5 | `recharge_count` | Số người nạp tiền | — | — | Số lượt nạp tiền |
| 6 | `first_recharge_count` | Nạp đầu trong ngày | — | — | Số người nạp lần đầu |
| 7 | `register_recharge_count` | Nạp đầu trong ngày đăng kí | — | — | Đăng ký kèm nạp tiền |
| 8 | `remark` | Ghi chú | — | — | edit: 'text' |
| 9 | `create_time` | Thời gian thêm vào | — | — | Thời gian tạo mã |
| 10 | — | Thao tác | minWidth: 360 | right | Row actions toolbar |

### Row Actions (toolbar: `#invitesRowBar`)
- **copy** — Copy đường link
- **setting** — Xem cài đặt
- **qr** — Mã QR
- **edit** — Chỉnh sửa

### Search Filters

| Field | Label | Type | Options |
|-------|-------|------|---------|
| `create_time` | Thời gian thêm vào | date-range | — |
| `user_register_time` | Thời gian hội viên đăng nhập | date-range | — |
| `invite_code` | Mã giới thiệu | text | — |

### Toolbar Actions
- **add** — Thêm mã giới thiệu

---

## 3. Report Lottery - Báo cáo xổ số

**Route:** `/report-lottery`
**File:** `frontend/src/views/reports/ReportLotteryView.vue`
**Trang gốc:** `/agent/reportLottery.html`
**Layui Table ID:** `reportLotteryTable`
**Phân trang:** Có (10, 50, 100, 200)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | `username` | Tên tài khoản | 150 | left | — |
| 2 | `user_parent_format` | Thuộc đại lý | 150 | — | — |
| 3 | `bet_count` | Số lần cược | minWidth: 150 | — | — |
| 4 | `bet_amount` | Tiền cược | minWidth: 150 | — | — |
| 5 | `valid_amount` | Tiền cược hợp lệ (trừ cược hoà) | minWidth: 160 | — | — |
| 6 | `rebate_amount` | Hoàn trả | minWidth: 150 | — | — |
| 7 | `result` | Thắng thua | minWidth: 150 | — | — |
| 8 | `win_lose` | Kết quả thắng thua (không gồm hoàn trả) | minWidth: 180 | — | — |
| 9 | `prize` | Tiền trúng | minWidth: 150 | — | — |
| 10 | `lottery_name` | Tên loại xổ | 160 | right | — |

### Search Filters

| Field | Label | Type | Options |
|-------|-------|------|---------|
| `username` | Tên tài khoản | text | — |
| `lottery_id` | Loại xổ số | select | `""`: Tất cả (dynamic từ API) |
| `date_range` | Ngày | date-range | — |

### Toolbar Actions
- **refresh** — Làm mới bảng

---

## 4. Report Funds - Báo cáo tài chính

**Route:** `/report-funds`
**File:** `frontend/src/views/reports/ReportFundsView.vue`
**Trang gốc:** `/agent/reportFunds.html`
**Layui Table ID:** `reportFundsTable`
**Phân trang:** Có (10, 50, 100, 200)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | `username` | Tên tài khoản | 150 | left | — |
| 2 | `user_parent_format` | Thuộc đại lý | 150 | — | — |
| 3 | `deposit_count` | Số lần nạp | 160 | — | — |
| 4 | `deposit_amount` | Số tiền nạp | minWidth: 150 | — | sort: true |
| 5 | `withdrawal_count` | Số lần rút | minWidth: 150 | — | — |
| 6 | `withdrawal_amount` | Số tiền rút | minWidth: 160 | — | — |
| 7 | `charge_fee` | Phí dịch vụ | minWidth: 150 | — | — |
| 8 | `agent_commission` | Hoa hồng đại lý | minWidth: 150 | — | — |
| 9 | `promotion` | Ưu đãi | minWidth: 150 | — | — |
| 10 | `third_rebate` | Hoàn trả bên thứ 3 | minWidth: 150 | — | — |
| 11 | `third_activity_amount` | Tiền thưởng từ bên thứ 3 | minWidth: 150 | — | — |
| 12 | `date` | Thời gian | minWidth: 160 | right | — |

### Search Filters

| Field | Label | Type | Options |
|-------|-------|------|---------|
| `username` | Tên tài khoản | text | — |
| `date_range` | Ngày | date-range | — |

### Toolbar Actions
- **refresh** — Làm mới bảng

---

## 5. Report Provider - Báo cáo nhà cung cấp game

**Route:** `/report-provider`
**File:** `frontend/src/views/reports/ReportProviderView.vue`
**Trang gốc:** `/agent/reportThirdGame.html`
**Layui Table ID:** `reportProviderTable`
**Phân trang:** Có (10, 50, 100, 200)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | `username` | Tên tài khoản | — | — | — |
| 2 | `platform_id_name` | Nhà cung cấp game | — | — | — |
| 3 | `t_bet_times` | Số lần cược | — | — | — |
| 4 | `t_bet_amount` | Tiền cược | — | — | — |
| 5 | `t_turnover` | Tiền cược hợp lệ | — | — | — |
| 6 | `t_prize` | Tiền thưởng | — | — | — |
| 7 | `t_win_lose` | Thắng thua | — | — | — |

### Search Filters

| Field | Label | Type | Options |
|-------|-------|------|---------|
| `username` | Tên tài khoản | text | — |
| `platform_id` | Nhà cung cấp game | select | `""`: Tất cả (dynamic từ API) |
| `date_range` | Ngày | date-range | — |

### Toolbar Actions
- **refresh** — Làm mới bảng

---

## 6. Deposits - Nạp rút tiền

**Route:** `/deposits`
**File:** `frontend/src/views/finance/DepositsView.vue`
**Trang gốc:** `/agent/depositAndWithdrawal.html`
**Layui Table ID:** `depositsTable`
**Phân trang:** Có (10, 50, 100, 200)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | `username` | Tên tài khoản | — | — | — |
| 2 | `user_parent_format` | Thuộc đại lý | — | — | — |
| 3 | `amount` | Số tiền | — | — | — |
| 4 | `type` | Loại hình giao dịch | — | — | — |
| 5 | `status` | Trạng thái giao dịch | — | — | — |
| 6 | `create_time` | Thời gian tạo đơn | — | — | — |

### Search Filters

| Field | Label | Type | Options |
|-------|-------|------|---------|
| `username` | Tên tài khoản | text | — |
| `type` | Loại hình giao dịch | select | `""`: Tất cả, `1`: Nạp tiền, `2`: Rút tiền |
| `status` | Trạng thái giao dịch | select | `""`: Tất cả, `0`: Chờ xử lí, `1`: Hoàn tất, `2`: Đang xử lí, `3`: Trạng thái không thành công |
| `date_range` | Ngày | date-range | — |

### Toolbar Actions
- **refresh** — Làm mới bảng

---

## 7. Withdrawals - Lịch sử rút tiền

**Route:** `/withdrawals`
**File:** `frontend/src/views/finance/WithdrawalsView.vue`
**Trang gốc:** `/agent/withdrawalsRecord.html`
**Layui Table ID:** `withdrawalsTable`
**Phân trang:** Có (10, 50, 100, 200)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | `serial_no` | Mã giao dịch | 180 | left | — |
| 2 | `create_time` | Thời gian tạo đơn | 160 | — | — |
| 3 | `username` | Tên tài khoản | — | — | — |
| 4 | `user_parent_format` | Thuộc đại lý | — | — | — |
| 5 | `amount` | Số tiền | — | — | — |
| 6 | `user_fee` | Phí hội viên | — | — | — |
| 7 | `true_amount` | Số tiền thực tế | — | — | — |
| 8 | `status_format` | Trạng thái giao dịch | — | — | — |

### Search Filters

| Field | Label | Type | Options |
|-------|-------|------|---------|
| `username` | Tên tài khoản | text | — |
| `serial_no` | Mã giao dịch | text | — |
| `status` | Trạng thái giao dịch | select | `""`: Tất cả, `0`: Chờ xử lí, `1`: Hoàn tất, `2`: Đang xử lí, `3`: Trạng thái không thành công |
| `date_range` | Ngày | date-range | — |

### Toolbar Actions
- **refresh** — Làm mới bảng

---

## 8. Bets - Đơn cược xổ số

**Route:** `/bets`
**File:** `frontend/src/views/bets/BetsView.vue`
**Trang gốc:** `/agent/bet.html`
**Layui Table ID:** `betsTable`
**Phân trang:** Có (10, 50, 100, 200)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | `serial_no` | Mã giao dịch | 200 | left | — |
| 2 | `username` | Tên người dùng | 150 | — | — |
| 3 | `create_time` | Thời gian cược | 160 | — | — |
| 4 | `lottery_name` | Trò chơi | minWidth: 150 | — | — |
| 5 | `play_type_name` | Loại trò chơi | minWidth: 150 | — | — |
| 6 | `play_name` | Cách chơi | minWidth: 150 | — | — |
| 7 | `issue` | Kỳ | minWidth: 150 | — | — |
| 8 | `content` | Thông tin cược | minWidth: 150 | — | — |
| 9 | `money` | Tiền cược | minWidth: 150 | — | — |
| 10 | `rebate_amount` | Tiền hoàn trả | minWidth: 150 | — | — |
| 11 | `result` | Thắng thua | minWidth: 150 | — | — |
| 12 | `status_text` | Trạng thái | 100 | right | — |

### Status values
| Value | Label |
|-------|-------|
| `-9` | Chưa thanh toán |
| `1` | Thắng |
| `-1` | Thua |
| `2` | Hòa |
| `3` | Hủy (người dùng) |
| `4` | Hủy (hệ thống) |
| `5` | Đơn cược bất thường |
| `6` | Chưa thanh toán (khôi phục thủ công) |

### Search Filters

| Field | Label | Type | Options |
|-------|-------|------|---------|
| `username` | Tên người dùng | text | — |
| `serial_no` | Mã giao dịch | text | — |
| `lottery_id` | Trò chơi | select | `""`: Tất cả (dynamic từ API) |
| `status` | Trạng thái | select | Xem bảng status values ở trên |
| `date_range` | Ngày | date-range | — |

### Toolbar Actions
- **refresh** — Làm mới bảng

---

## 9. BetThirdParty - Đơn cược bên thứ 3

**Route:** `/bet-third-party`
**File:** `frontend/src/views/bets/BetThirdPartyView.vue`
**Trang gốc:** `/agent/betOrder.html`
**Layui Table ID:** `betThirdPartyTable`
**Phân trang:** Có (10, 50, 100, 200)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | `serial_no` | Mã giao dịch | 250 | left | — |
| 2 | `platform_id_name` | Nhà cung cấp game bên thứ 3 | 150 | — | — |
| 3 | `platform_username` | Tên tài khoản thuộc nhà cái | 150 | — | — |
| 4 | `c_name` | Loại hình trò chơi | 150 | — | — |
| 5 | `game_name` | Tên trò chơi bên thứ 3 | 150 | — | — |
| 6 | `bet_amount` | Tiền cược | 150 | — | — |
| 7 | `turnover` | Tiền cược hợp lệ | 150 | — | — |
| 8 | `prize` | Tiền thưởng | 150 | — | — |
| 9 | `win_lose` | Thắng thua | 150 | — | — |
| 10 | `bet_time` | Thời gian cược | 160 | right | — |

### Search Filters

| Field | Label | Type | Options |
|-------|-------|------|---------|
| `username` | Tên tài khoản | text | — |
| `serial_no` | Mã giao dịch | text | — |
| `platform_username` | Tên tài khoản thuộc nhà cái | text | — |
| `date_range` | Ngày | date-range | — |

### Toolbar Actions
- **refresh** — Làm mới bảng

---

## 10. Tiers - Cấp bậc

**Route:** `/tiers`
**File:** `frontend/src/views/tiers/TiersView.vue`
**Trang gốc:** Không có trang tương ứng trực tiếp (MaxHUB custom)
**Layui Table ID:** `tiersTable`
**Phân trang:** Không (page: false)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | — | STT | 60 | — | numbers |
| 2 | `name` | Tên cấp bậc | minWidth: 200 | — | — |
| 3 | `created_at` | Ngày tạo | 200 | — | — |

### Toolbar Actions
- **add** — Thêm cấp bậc mới
- **refresh** — Làm mới bảng

---

## 11. Rebate - Tỷ lệ hoàn trả

**Route:** `/rebate`
**File:** `frontend/src/views/rebate/RebateView.vue`
**Trang gốc:** `/agent/getRebateOddsPanel.html`
**Ghi chú:** Trang gốc dùng Vue 2 app với dynamic columns load từ API (`/agent/getLottery`, `/agent/getRebateOddsPanel`). Bảng headers (tableHead) và body (tableBody) đến từ API responses. Có series selector và lottery selector dropdowns.

### Columns (dynamic)
Columns được generate động từ API, không hardcode. Thông thường gồm:

| # | Field | Title | Ghi chú |
|---|-------|-------|---------|
| 1 | `odds_11` | Loại chơi | Tên loại chơi |
| 2-11 | `odds_N` | Cấp N | Tỷ lệ hoàn trả cho từng cấp bậc |

---

## 12. SettingsSync - Đồng bộ Agent

**Route:** `/settings-sync`
**File:** `frontend/src/views/settings/SettingsSyncView.vue`
**Trang gốc:** Không có (MaxHUB custom)
**Layui Table ID:** `syncTable`
**Phân trang:** Không (page: false)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | — | STT | 60 | — | numbers |
| 2 | `owner` | Chủ sở hữu | 140 | — | — |
| 3 | `username` | Username | 140 | — | — |
| 4 | `cookie_set` | Cookie | 80 | — | templet: check/cross |
| 5 | `is_active` | Trạng thái | 100 | — | templet: check/cross |
| 6 | `last_login_at` | Đăng nhập cuối | 160 | — | — |

### Toolbar Actions
- **add** — Thêm mới Agent
- **refresh** — Làm mới bảng

---

## 13. SettingsAccount - Quản lý tài khoản

**Route:** `/settings-account`
**File:** `frontend/src/views/settings/SettingsAccountView.vue`
**Trang gốc:** Không có (MaxHUB custom)
**Layui Table ID:** `accountTable`
**Phân trang:** Không (page: false)

### Columns

| # | Field | Title | Width | Fixed | Ghi chú |
|---|-------|-------|-------|-------|---------|
| 1 | — | STT | 60 | — | numbers |
| 2 | `name` | Tên | 140 | — | — |
| 3 | `username` | Username | 140 | — | — |
| 4 | `email` | Email | 200 | — | — |
| 5 | `role` | Vai trò | 120 | — | templet: color-coded |
| 6 | `is_active` | Trạng thái | 100 | — | templet: Hoạt động/Khóa |
| 7 | `created_at` | Ngày tạo | 160 | — | — |
| 8 | — | Thao tác | 220 | — | toolbar |

### Row Actions (toolbar: `#accountRowBar`)
- **edit** — Sửa tài khoản
- **perm** — Phân quyền
- **del** — Xóa tài khoản (có confirm)

### Toolbar Actions
- **add** — Thêm tài khoản mới
- **refresh** — Làm mới bảng

---

## 14. Tools - Công cụ

### 14.1 Đổi mật khẩu đăng nhập
**Route:** `/change-login-pw`
**File:** `frontend/src/views/tools/ChangeLoginPwView.vue`
**Trang gốc:** `/agent/editPassword.html`

### 14.2 Đổi mật khẩu giao dịch
**Route:** `/change-trade-pw`
**File:** `frontend/src/views/tools/ChangeTradePwView.vue`
**Trang gốc:** `/agent/editFundPassword.html`

### 14.3 Cài đặt hệ thống
**Route:** `/settings-system`
**File:** `frontend/src/views/settings/SettingsSystemView.vue`

---

## 15. Mapping trang gốc ↔ MaxHUB

| Trang gốc (ee88) | Route MaxHUB | View File | Ghi chú |
|-------------------|-------------|-----------|---------|
| `/agent/user.html` | `/members` | MembersView.vue | Quản lí hội viên thuộc cấp |
| `/agent/inviteList.html` | `/invites` | InvitesView.vue | Mã giới thiệu |
| `/agent/reportLottery.html` | `/report-lottery` | ReportLotteryView.vue | Báo cáo xổ số |
| `/agent/reportFunds.html` | `/report-funds` | ReportFundsView.vue | Báo cáo tài chính |
| `/agent/reportThirdGame.html` | `/report-provider` | ReportProviderView.vue | Báo cáo nhà cung cấp game |
| `/agent/depositAndWithdrawal.html` | `/deposits` | DepositsView.vue | Nạp rút tiền |
| `/agent/withdrawalsRecord.html` | `/withdrawals` | WithdrawalsView.vue | Lịch sử rút tiền |
| `/agent/bet.html` | `/bets` | BetsView.vue | Đơn cược xổ số |
| `/agent/betOrder.html` | `/bet-third-party` | BetThirdPartyView.vue | Đơn cược bên thứ 3 |
| `/agent/getRebateOddsPanel.html` | `/rebate` | RebateView.vue | Tỷ lệ hoàn trả |
| `/agent/editPassword.html` | `/change-login-pw` | ChangeLoginPwView.vue | Đổi MK đăng nhập |
| `/agent/editFundPassword.html` | `/change-trade-pw` | ChangeTradePwView.vue | Đổi MK giao dịch |
| — | `/tiers` | TiersView.vue | MaxHUB custom |
| — | `/settings-sync` | SettingsSyncView.vue | MaxHUB custom |
| — | `/settings-account` | SettingsAccountView.vue | MaxHUB custom |
| — | `/settings-system` | SettingsSystemView.vue | MaxHUB custom |

---

## Ghi chú kỹ thuật

### Layui Table Config chung
```javascript
{
  skin: 'grid',
  even: true,
  size: 'sm',
  text: { none: 'Không có dữ liệu' },
  defaultToolbar: ['filter', 'exports', 'print'],
  page: { limit: 10, limits: [10, 50, 100, 200] }  // hoặc page: false
}
```

### Field naming conventions
- `*_format` — Suffix `_format` = đã format sẵn phía server (VD: `status_format`, `type_format`, `user_parent_format`)
- `*_count` — Suffix `_count` = aggregate count
- `*_amount` — Suffix `_amount` = aggregate sum tiền
- `create_time` / `created_at` — Thời gian tạo (ee88 dùng `create_time`, MaxHUB custom dùng `created_at`)

### Composable pattern
```javascript
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
const { createTemplate } = useLayuiTemplate()
// Templates tự động cleanup khi component unmount
```

### Date range
```javascript
import { initDateRange } from '@/composables/useLayuiDate'
initDateRange('input[name="date_range"]')
```
