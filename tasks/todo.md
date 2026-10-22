# Tasks Checklist: Bing Automation Tool v2

## Phase 1: Foundation & Setup UX (Vấn đề 2 trong PRD)

- [x] **Task 1: Khắc phục lỗi kẹt console (QuickEdit Mode) & Tối ưu script setup `run.bat`**
  - **Description:** Sửa file `run.bat` để tắt tính năng QuickEdit mode của Windows Console (nguyên nhân gây kẹt phải bấm Enter), tối ưu kiểm tra thư viện tránh cài lại `pip install` mỗi lần chạy.
  - **Acceptance criteria:**
    - [x] `run.bat` vô hiệu hóa QuickEdit mode khi mở cmd.
    - [x] Bỏ qua bước `pip install` nếu các gói (`selenium`, `webdriver-manager`, `faker`) đã cài đặt trong `venv`.
    - [x] Không còn tình trạng bị kẹt tiến trình khi click chuột vào console.
  - **Verification:**
    - [x] Chạy `run.bat` kiểm tra tốc độ khởi động khi thư viện đã có sẵn.
    - [x] Click chuột vào màn hình console xác nhận script không bị tạm dừng.
  - **Dependencies:** None
  - **Files likely touched:** `Bing.v2/run.bat`
  - **Estimated scope:** Small (1 file)

- [x] **Task 2: Xây dựng UI thanh tiến trình Setup & Bộ hướng dẫn người dùng**
  - **Description:** Bổ sung giao diện thông báo tiến trình khởi động trực quan và bảng hướng dẫn sử dụng tiếng Việt chi tiết (đăng nhập lần đầu, cấu hình số lượt search, phím tắt).
  - **Acceptance criteria:**
    - [x] Hiển thị các bước setup rõ ràng: [1/4] Kiểm tra Python -> [2/4] Môi trường venv -> [3/4] Kiểm tra thư viện -> [4/4] Khởi động tool.
    - [x] Bảng hướng dẫn sử dụng tiếng Việt chi tiết, thân thiện, không làm rối màn hình.
  - **Verification:**
    - [x] Chạy thử từ cmd xem hiển thị màu sắc ANSI, tiến trình từng bước và thông báo hướng dẫn.
  - **Dependencies:** Task 1
  - **Files likely touched:** `Bing.v2/run.bat`, `Bing.v2/bing_auto.py`, `Bing.v2/config.py`
  - **Estimated scope:** Medium (2-3 files)

### Checkpoint: Foundation & Setup
- [x] Script `run.bat` chạy mượt mà, không giật lag.
- [x] Click chuột vào màn hình không bị dừng đợi nhấn Enter.
- [x] Giao diện hiển thị rõ ràng, hướng dẫn đầy đủ.

---

## Phase 2: Popup & Consent Dialog Handler (Vấn đề 1 trong PRD)

- [x] **Task 3: Xây dựng module tự động phát hiện và đóng popup Bing (`popup_handler.py`)**
  - **Description:** Tạo module chuyên biệt nhận diện và tự động đóng/chấp nhận các popup "Cung cấp data để phục vụ tốt hơn...", cookie consent (GDPR), modal che khuất màn hình Bing.
  - **Acceptance criteria:**
    - [x] Tự động quét và nhấp các nút consent: "Chấp nhận", "Đồng ý", "Xác nhận", "Có", "Accept", "Agree", "Maybe later", "Không phải bây giờ".
    - [x] Cơ chế dự phòng bằng JavaScript DOM (`click()` hoặc gỡ bỏ lớp overlay `b_modal`/backdrop).
    - [x] Không làm gián đoạn luồng tìm kiếm nếu không có popup xuất hiện.
  - **Verification:**
    - [x] Kiểm thử với các trang có và không có popup xuất hiện trên Bing.
  - **Dependencies:** Task 2
  - **Files likely touched:** `Bing.v2/popup_handler.py`
  - **Estimated scope:** Small (1-2 files)

- [x] **Task 4: Tích hợp `popup_handler` vào vòng lặp tìm kiếm an toàn (Safe Search Loop)**
  - **Description:** Cập nhật hàm tìm kiếm trong `bing_auto.py` để chủ động gọi `popup_handler` trước khi thao tác thanh tìm kiếm, bọc thao tác nhập liệu với fallback click JS nhằm chống `ElementClickInterceptedException`.
  - **Acceptance criteria:**
    - [x] Mỗi lượt tìm kiếm tự động kiểm tra và dọn sạch popup cản trở.
    - [x] Thao tác click vào ô `#sb_form_q` không bị văng lỗi hoặc treo timeout 15 giây khi gặp dialog.
    - [x] Xử lý mượt mà cả trên giao diện máy tính và giao diện điện thoại.
  - **Verification:**
    - [x] Chạy thử các lượt tìm kiếm liên tục, xác nhận không có ngoại lệ `ElementClickInterceptedException`.
  - **Dependencies:** Task 3
  - **Files likely touched:** `Bing.v2/bing_auto.py`, `Bing.v2/popup_handler.py`
  - **Estimated scope:** Small (1-2 files)

### Checkpoint: Popup Handling
- [x] Truy cập Bing không bị đơ hoặc kẹt bởi dialog "Cung cấp data...".
- [x] Luồng tìm kiếm tự động vượt qua mọi lớp che phủ một cách trơn tru.

---

## Phase 3: Persistent Profile & Mobile Rewards Point Fix (Vấn đề 3 trong PRD)

- [x] **Task 5: Triển khai Profile lưu trữ người dùng (Persistent Edge Profile)**
  - **Description:** Cấu hình `--user-data-dir` cho Selenium EdgeDriver dẫn tới thư mục profile cục bộ cố định (`edge_profile/`) để lưu giữ phiên đăng nhập tài khoản Microsoft Rewards qua các lần chạy.
  - **Acceptance criteria:**
    - [x] Driver sử dụng thư mục dữ liệu người dùng độc lập trong project.
    - [x] Cookies và phiên đăng nhập được duy trì sau khi tắt browser và chạy lại.
    - [x] Hỗ trợ chế độ "Đăng nhập lần đầu" để người dùng đăng nhập tài khoản Microsoft nếu chưa có session.
  - **Verification:**
    - [x] Đăng nhập tài khoản Microsoft trên profile, tắt tool mở lại xác nhận vẫn giữ trạng thái đăng nhập.
  - **Dependencies:** Task 2
  - **Files likely touched:** `Bing.v2/bing_auto.py`, `Bing.v2/config.py`
  - **Estimated scope:** Medium (2-3 files)

- [x] **Task 6: Cải tiến giả lập Edge Mobile (CDP + EdgA) & Logic kích hoạt điểm Rewards**
  - **Description:** Sử dụng User-Agent chuẩn Edge Android (`EdgA`) kèm đầy đủ Client Hints và Touch Events qua Chrome DevTools Protocol (CDP), tối ưu việc đợi kết quả tìm kiếm render hoàn tất để kích hoạt điểm thưởng.
  - **Acceptance criteria:**
    - [x] Edge chuyển đổi chuẩn sang chế độ Mobile với đầy đủ User-Agent `EdgA` và Touch Simulation.
    - [x] Kế thừa phiên đăng nhập từ Profile ở Task 5 để Bing nhận diện người dùng trên Mobile.
    - [x] Trang kết quả tìm kiếm mobile hiển thị đúng cấu trúc và tích lũy điểm trên Microsoft Rewards.
  - **Verification:**
    - [x] Chạy session Mobile và kiểm tra trên trang Rewards xem điểm Mobile Search có tăng lên.
  - **Dependencies:** Task 4, Task 5
  - **Files likely touched:** `Bing.v2/bing_auto.py`, `Bing.v2/config.py`
  - **Estimated scope:** Medium (2 files)

### Checkpoint: Mobile & Rewards Verification
- [x] Chạy phiên Desktop và Mobile hoàn tất mà không mất session đăng nhập.
- [x] Điểm số trên Microsoft Rewards cập nhật chính xác cho cả PC và Mobile.

---

## Phase 4: Polish, Testing & Tài liệu hoàn thiện

- [x] **Task 7: Đồng bộ cấu trúc thư mục, xử lý ngoại lệ và hoàn thiện tài liệu hướng dẫn**
  - **Description:** Tinh chỉnh các tham số thời gian nghỉ chống bot, xử lý ngoại lệ đóng trình duyệt an toàn, cập nhật `requirements.txt` và viết tài liệu hướng dẫn sử dụng tiếng Việt chi tiết (`README.md`).
  - **Acceptance criteria:**
    - [x] Mã nguồn sạch sẽ, có chú thích tiếng Việt rõ ràng.
    - [x] File hướng dẫn sử dụng chi tiết cách đăng nhập lần đầu, cách chạy, cách xử lý sự cố.
    - [x] Công cụ chạy ổn định từ đầu đến cuối không cần can thiệp thủ công.
  - **Verification:**
    - [x] Chạy trọn vẹn quy trình mẫu (Setup -> PC Search -> Mobile Search -> Finish) qua `run.bat`.
  - **Dependencies:** Task 1 đến Task 6
  - **Files likely touched:** `Bing.v2/bing_auto.py`, `Bing.v2/config.py`, `Bing.v2/README.md`
  - **Estimated scope:** Medium (3-4 files)

### Checkpoint: Final Polish
- [x] Toàn bộ 3 mục trong `PRD.txt` đã được giải quyết trọn vẹn và xác minh.
- [x] Sẵn sàng bàn giao cho người dùng sử dụng hàng ngày.
