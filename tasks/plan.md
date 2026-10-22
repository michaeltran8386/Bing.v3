# Implementation Plan: Bing Automation Tool v2 Optimization & Bugfixes

## Overview
Nâng cấp và khắc phục toàn diện 3 vấn đề trọng tâm trong công cụ tự động tìm kiếm Bing (Microsoft Rewards Automation) theo yêu cầu tại `PRD.txt`:
1. **Xử lý triệt để popup/modal bản quyền & dữ liệu**: "Cung cấp data để phục vụ tốt hơn...", banner cookie/GDPR làm đơ hoặc nghẽn luồng click search.
2. **Cải tiến Setup & Trải nghiệm giao diện (UI) khởi động**: Khắc phục lỗi kẹt bảng điều khiển (do Windows QuickEdit Mode khiến tiến trình tạm dừng cho tới khi nhấn Enter), tối ưu kiểm tra thư viện không cài đè lặp lại, và hiển thị thanh tiến trình trực quan cùng hướng dẫn sử dụng.
3. **Sửa lỗi tìm kiếm Mobile không cập nhật điểm Rewards**: Lưu trữ phiên đăng nhập tài khoản (Persistent Edge Profile), giả lập chuẩn Edge Mobile (EdgA với Client Hints & Touch Events qua CDP/MobileEmulation), và tối ưu quy trình tìm kiếm để kích hoạt điểm thưởng ổn định.

## Architecture Decisions
- **Persistent User Data Profile (`edge_profile/`)**: Lưu trữ cookie và trạng thái đăng nhập tài khoản Microsoft. Người dùng chỉ cần đăng nhập một lần, các lần chạy sau (cả PC và Mobile) sẽ tự động nhận diện tài khoản để cộng điểm.
- **Chống treo Console (Windows QuickEdit Mode Fix)**: Vô hiệu hóa QuickEdit mode thông qua lệnh cấu hình console PowerShell/Win32 API ngay khi khởi chạy `run.bat` và Python, ngăn chuột nhấp vào console làm dừng luồng thực thi.
- **Smart Dependency Check**: Kiểm tra thư viện Python trước khi gọi `pip install`, loại bỏ độ trễ và hiện tượng đơ mạng lúc setup.
- **CDP Mobile Emulation + Edge Android User-Agent (`EdgA`)**: Sử dụng Chrome DevTools Protocol (`Network.setUserAgentOverride` kèm Client Hints `Sec-CH-UA-Mobile: ?1` và `Emulation.setDeviceMetricsOverride` hỗ trợ Touch) để Microsoft Rewards nhận diện chính xác là lượt tìm kiếm từ thiết bị di động Edge.
- **Tách module hóa sạch sẽ**: Tách cấu hình (`config.py`), bộ xử lý popup (`popup_handler.py`), và logic chính (`bing_auto.py`) để dễ bảo trì và mở rộng.

---

## Task List

### Phase 1: Foundation & Setup UX (Giải quyết Vấn đề 2)

#### Task 1: Khắc phục lỗi kẹt console (QuickEdit Mode) & Tối ưu script setup `run.bat`
- **Description:** Sửa file `run.bat` để tắt tính năng QuickEdit mode của Windows Console (nguyên nhân chính khiến tool bị kẹt đợi nhấn Enter khi người dùng lỡ bấm chuột vào cửa sổ), đồng thời tối ưu việc kiểm tra virtualenv và thư viện trước khi chạy `pip install`.
- **Acceptance criteria:**
  - `run.bat` vô hiệu hóa QuickEdit mode khi mở cmd.
  - Bỏ qua bước `pip install` nếu các gói (`selenium`, `webdriver-manager`, `faker`) đã được cài đặt trong `venv`.
  - Không còn tình trạng bị dừng/kẹt tiến trình khi click chuột vào màn hình console.
- **Verification:**
  - Chạy `run.bat` kiểm tra tốc độ khởi động khi thư viện đã có sẵn.
  - Click chuột vào cửa sổ console và xác nhận script không bị tạm dừng.
- **Dependencies:** None
- **Files likely touched:**
  - `Bing.v2/run.bat`
- **Estimated scope:** Small (1 file)

#### Task 2: Xây dựng UI thanh tiến trình Setup & Bộ hướng dẫn người dùng
- **Description:** Thêm giao diện thông báo tiến trình khởi động trực quan (ASCII/Color Progress indicator) và hiển thị bảng hướng dẫn sử dụng rõ ràng (cách đăng nhập tài khoản lần đầu, hướng dẫn cấu hình số lượng từ khóa, phím tắt an toàn).
- **Acceptance criteria:**
  - Hiển thị các bước setup rõ ràng: [1/4] Kiểm tra Python -> [2/4] Môi trường venv -> [3/4] Kiểm tra thư viện -> [4/4] Khởi động tool.
  - Bảng hướng dẫn sử dụng tiếng Việt chi tiết, thân thiện, không làm rối màn hình.
- **Verification:**
  - Chạy thử từ cmd xem hiển thị màu sắc ANSI, tiến trình từng bước và thông báo hướng dẫn.
- **Dependencies:** Task 1
- **Files likely touched:**
  - `Bing.v2/run.bat`
  - `Bing.v2/bing_auto.py`
  - `Bing.v2/config.py` (tạo mới)
- **Estimated scope:** Medium (2-3 files)

### Checkpoint: Foundation & Setup
- [ ] Script `run.bat` chạy mượt mà, không giật lag.
- [ ] Thử click chuột vào màn hình không bị dừng đợi nhấn Enter.
- [ ] Giao diện hiển thị rõ ràng, hướng dẫn đầy đủ.

---

### Phase 2: Popup & Consent Dialog Handler (Giải quyết Vấn đề 1)

#### Task 3: Xây dựng module tự động phát hiện và đóng popup Bing (`popup_handler.py`)
- **Description:** Xây dựng module chuyên biệt để nhận diện và tự động nhấn chấp nhận/đóng các popup "Cung cấp data để phục vụ tốt hơn...", cookie consent (GDPR), thông báo phần thưởng, hoặc các modal che khuất màn hình Bing.
- **Acceptance criteria:**
  - Tự động quét và nhấp các nút consent: "Chấp nhận", "Đồng ý", "Xác nhận", "Có", "Accept", "Agree", "Maybe later", "Không phải bây giờ".
  - Có cơ chế dự phòng: nếu nút bị che hoặc không bấm được, dùng JavaScript DOM (`click()` hoặc gỡ bỏ lớp overlay `b_modal`/backdrop) để giải phóng màn hình.
  - Không làm gián đoạn luồng tìm kiếm nếu không có popup xuất hiện.
- **Verification:**
  - Kiểm thử trực tiếp với các kịch bản có và không có popup xuất hiện trên Bing.
- **Dependencies:** Task 2
- **Files likely touched:**
  - `Bing.v2/popup_handler.py` (tạo mới)
- **Estimated scope:** Small (1-2 files)

#### Task 4: Tích hợp `popup_handler` vào vòng lặp tìm kiếm an toàn (Safe Search Loop)
- **Description:** Cập nhật hàm `perform_search_session` trong `bing_auto.py` để chủ động gọi `popup_handler` trước khi thao tác thanh tìm kiếm, đồng thời bọc thao tác nhập liệu với fallback click JS nhằm chống `ElementClickInterceptedException`.
- **Acceptance criteria:**
  - Mỗi lượt tìm kiếm tự động kiểm tra và dọn sạch popup cản trở.
  - Thao tác click vào ô `#sb_form_q` không bị văng lỗi hoặc treo timeout 15 giây khi gặp dialog.
  - Xử lý mượt mà cả trên giao diện máy tính và giao diện điện thoại.
- **Verification:**
  - Chạy thử 5 lượt tìm kiếm liên tục, xác nhận không có ngoại lệ `ElementClickInterceptedException`.
- **Dependencies:** Task 3
- **Files likely touched:**
  - `Bing.v2/bing_auto.py`
  - `Bing.v2/popup_handler.py`
- **Estimated scope:** Small (1-2 files)

### Checkpoint: Popup Handling
- [ ] Truy cập Bing không bị đơ hoặc kẹt bởi dialog "Cung cấp data...".
- [ ] Luồng tìm kiếm tự động vượt qua mọi lớp che phủ một cách trơn tru.

---

### Phase 3: Persistent Profile & Mobile Rewards Point Fix (Giải quyết Vấn đề 3)

#### Task 5: Triển khai Profile lưu trữ người dùng (Persistent Edge Profile)
- **Description:** Bổ sung cấu hình `--user-data-dir` cho Selenium EdgeDriver dẫn tới thư mục profile cục bộ cố định (`edge_profile/`). Người dùng chỉ cần đăng nhập tài khoản Microsoft 1 lần duy nhất, các phiên tìm kiếm sau sẽ tự động kế thừa phiên đăng nhập để tính điểm Microsoft Rewards.
- **Acceptance criteria:**
  - Driver sử dụng thư mục dữ liệu người dùng độc lập trong project hoặc tùy biến.
  - Cookies và phiên đăng nhập được duy trì nguyên vẹn sau khi tắt browser và chạy lại.
  - Hỗ trợ chế độ "Đăng nhập lần đầu" (mở browser cho người dùng đăng nhập tài khoản Microsoft nếu chưa có session).
- **Verification:**
  - Đăng nhập tài khoản Microsoft trên profile, tắt tool mở lại xác nhận vẫn giữ trạng thái đăng nhập.
- **Dependencies:** Task 2
- **Files likely touched:**
  - `Bing.v2/bing_auto.py`
  - `Bing.v2/config.py`
- **Estimated scope:** Medium (2-3 files)

#### Task 6: Cải tiến giả lập Edge Mobile (CDP + EdgA) & Logic kích hoạt điểm Rewards
- **Description:** Khắc phục lỗi Mobile không cộng điểm bằng cách:
  1. Sử dụng User-Agent chuẩn Edge Android (`EdgA`) kèm đầy đủ Client Hints (`Sec-CH-UA-Mobile: ?1`, platform `Android`) và kích hoạt touch events qua Chrome DevTools Protocol (CDP).
  2. Tối ưu luồng tìm kiếm mobile: gửi truy vấn, đợi phần tử kết quả tìm kiếm (`#b_results`) render hoàn tất (đây là điều kiện kích hoạt ping tính điểm của Microsoft Rewards), mô phỏng cuộn trang nhẹ và giãn cách thời gian tìm kiếm hợp lý (cooldown 6-10s).
- **Acceptance criteria:**
  - Edge chuyển đổi chuẩn sang chế độ Mobile với đầy đủ User-Agent `EdgA` và Touch Simulation.
  - Giữ nguyên phiên đăng nhập từ Profile ở Task 5 để Bing nhận diện người dùng trên Mobile.
  - Trang kết quả tìm kiếm mobile hiển thị đúng cấu trúc và tích lũy điểm trên Microsoft Rewards.
- **Verification:**
  - Chạy session Mobile và kiểm tra trên trang Rewards xem điểm Mobile Search có tăng lên.
- **Dependencies:** Task 4, Task 5
- **Files likely touched:**
  - `Bing.v2/bing_auto.py`
  - `Bing.v2/config.py`
- **Estimated scope:** Medium (2 files)

### Checkpoint: Mobile & Rewards Verification
- [ ] Chạy phiên Desktop và Mobile hoàn tất mà không mất session đăng nhập.
- [ ] Điểm số trên Microsoft Rewards cập nhật chính xác cho cả PC và Mobile.

---

### Phase 4: Polish, Testing & Tài liệu hoàn thiện

#### Task 7: Đồng bộ cấu trúc thư mục, xử lý ngoại lệ và hoàn thiện tài liệu hướng dẫn
- **Description:** Dọn dẹp mã nguồn, tối ưu hóa các tham số thời gian nghỉ chống bot, xử lý ngoại lệ Edge Driver khi đang mở, cập nhật file `requirements.txt` (nếu có bổ sung thư viện), đồng bộ sang thư mục chính và viết tài liệu hướng dẫn sử dụng tiếng Việt chi tiết (`HDSD.md` / `README.md`).
- **Acceptance criteria:**
  - Mã nguồn sạch sẽ, có chú thích tiếng Việt rõ ràng.
  - File hướng dẫn sử dụng chi tiết cách đăng nhập lần đầu, cách chạy, cách xử lý khi gặp sự cố.
  - Công cụ chạy ổn định từ đầu đến cuối không cần can thiệp thủ công.
- **Verification:**
  - Chạy trọn vẹn quy trình mẫu (Setup -> PC Search -> Mobile Search -> Finish) qua `run.bat`.
- **Dependencies:** Task 1 đến Task 6
- **Files likely touched:**
  - `Bing.v2/bing_auto.py`
  - `Bing.v2/config.py`
  - `Bing.v2/README.md`
  - `PRD.txt`
- **Estimated scope:** Medium (3-4 files)

### Checkpoint: Final Polish
- [ ] Toàn bộ 3 mục trong `PRD.txt` đã được giải quyết trọn vẹn và xác minh.
- [ ] Sẵn sàng bàn giao cho người dùng sử dụng hàng ngày.

---

## Risks and Mitigations
| Nguy cơ (Risk) | Mức độ | Biện pháp giảm thiểu (Mitigation) |
|---|---|---|
| Microsoft Rewards áp dụng cooldown tìm kiếm (giới hạn 3-4 tìm kiếm / 15 phút trên một số tài khoản) | Trung bình | Cho phép cấu hình linh hoạt số lượng tìm kiếm và khoảng thời gian trễ ngẫu nhiên (`random.uniform(7, 12)`) trong `config.py`. |
| Trình duyệt Edge đã mở sẵn làm khóa thư mục `edge_profile` | Cao | Kiểm tra và nhắc nhở người dùng đóng Edge trước khi chạy, hoặc dùng profile tách biệt dành riêng cho tool. |
| Bing thay đổi cấu trúc DOM/Class của popup consent | Thấp | Kết hợp đa dạng selector (ID, CSS, XPath theo text tiếng Việt & tiếng Anh) cùng giải pháp can thiệp JS loại bỏ overlay. |

## Open Questions & Lưu ý cho Người Dùng
- **Tài khoản**: Người dùng cần đăng nhập tài khoản Microsoft vào trình duyệt của tool trong lần chạy đầu tiên để điểm thưởng có thể ghi nhận.
- **Đồng bộ mã**: Thư mục gốc có cả `Bing.v2` và `Sample`, các cải tiến sẽ được thực hiện trực tiếp vào `Bing.v2` (thư mục chạy chính).
