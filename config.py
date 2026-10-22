import os
import sys

# ================= CONFIGURATION =================
# Số lượt tìm kiếm (Microsoft Rewards: 30 PC = 90 điểm, 20 Mobile = 60 điểm)
PC_SEARCH_COUNT = 30
MOBILE_SEARCH_COUNT = 20

# Số lượt tìm kiếm trong 1 đợt an toàn (chống vi phạm giới hạn cooldown 15 phút của Microsoft)
BATCH_SEARCH_COUNT = 4
COOLDOWN_SECONDS = 915  # 15 phút 15 giây

# Thời gian nghỉ giữa các lần tìm kiếm (giây) - tránh bị anti-bot của Bing chặn
MIN_SEARCH_DELAY = 7.0
MAX_SEARCH_DELAY = 12.0

# Thời gian gõ phím mô phỏng người thật
MIN_TYPE_DELAY = 0.01
MAX_TYPE_DELAY = 0.03

# Thư mục lưu trữ Profile của Edge để giữ phiên đăng nhập tài khoản Microsoft
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
EDGE_PROFILE_DIR = os.path.join(BASE_DIR, "edge_profile")

# Cấu hình giả lập chuẩn Edge Android để Bing Rewards tính điểm Mobile
MOBILE_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Mobile Safari/537.36 EdgA/124.0.0.0"
)

MOBILE_DEVICE_METRICS = {
    "width": 390,
    "height": 844,
    "deviceScaleFactor": 3,
    "mobile": True,
    "touch": True
}

# ================= MÀU SẮC CONSOLE =================
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


# ================= HÀM HỆ THỐNG / CONSOLE =================
def disable_quickedit() -> bool:
    """
    Vô hiệu hóa QuickEdit Mode trên Windows Console.
    Khi bật QuickEdit, nếu người dùng lỡ bấm chuột vào cửa sổ CMD,
    toàn bộ tiến trình sẽ bị đóng băng (kẹt) cho tới khi nhấn phím Enter.
    """
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        hStdin = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE = -10
        if hStdin == 0 or hStdin == -1:
            return False

        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(hStdin, ctypes.byref(mode)):
            # 0x0040 = ENABLE_QUICK_EDIT_MODE
            # 0x0080 = ENABLE_EXTENDED_FLAGS (cần thiết khi thay đổi QuickEdit)
            new_mode = (mode.value & ~0x0040) | 0x0080
            return bool(kernel32.SetConsoleMode(hStdin, new_mode))
    except Exception:
        pass
    return False


def print_progress(step: int, total: int, title: str):
    """Hiển thị thanh tiến trình cài đặt / khởi động theo phong cách hiện đại."""
    pct = int((step / total) * 100)
    bar_len = 20
    filled = int(bar_len * step / total)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"{CYAN}[{step}/{total}]{RESET} {bar} {YELLOW}{pct:>3}%{RESET} - {WHITE}{BOLD}{title}{RESET}")


def print_user_guide():
    """Hiển thị bảng hướng dẫn sử dụng và lưu ý quan trọng."""
    guide = f"""
{BLUE}╔══════════════════════════════════════════════════════════════════════════════╗
║                          {BOLD}{WHITE}HƯỚNG DẪN SỬ DỤNG BING REWARDS TOOL{RESET}{BLUE}                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ {YELLOW}1. ĐĂNG NHẬP LẦN ĐẦU:{RESET}                                                        ║
║    - Trình duyệt sẽ mở với Profile lưu trữ tại thư mục {CYAN}edge_profile/{RESET}{BLUE}.          ║
║    - Hãy đăng nhập tài khoản Microsoft của bạn một lần duy nhất.             ║
║    - Sau đó, mọi phiên chạy PC & Mobile sẽ tự động nhận điểm thưởng.         ║
║                                                                              ║
║ {YELLOW}2. CHỐNG TREO / ĐƠ MÀN HÌNH:{RESET}                                                 ║
║    - Tính năng QuickEdit Mode đã được tắt tự động để tránh bị dừng khi bấm    ║
║      chuột vào cửa sổ màu đen CMD.                                           ║
║    - Tự động bỏ qua và chấp nhận popup 'Cung cấp data...' từ Bing.           ║
║                                                                              ║
║ {YELLOW}3. CƠ CHẾ TÍNH ĐIỂM MOBILE:{RESET}                                                  ║
║    - Giả lập Edge Android (EdgA) chuẩn và đợi kết quả tải xong trước khi      ║
║      tìm kiếm từ khóa tiếp theo để Bing ghi nhận điểm đầy đủ.                ║
╚══════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(guide)
