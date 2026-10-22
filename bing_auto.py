import time
import random
import os
import sys
import shutil
import urllib.parse
import re
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

import config
from popup_handler import handle_bing_prompts, safe_click, dismiss_overlays_js

# Cấu hình UTF-8 cho console để in tiếng Việt chuẩn xác trên Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


# ================= UTILS & CONSOLE =================
def setup_console():
    """Thiết lập môi trường console: tắt QuickEdit mode và in header."""
    config.disable_quickedit()


def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    bing_art = r"""
  ██████╗ ██╗███╗   ██╗ ██████╗ 
  ██╔══██╗██║████╗  ██║██╔════╝ 
  ██████╔╝██║██╔██╗ ██║██║  ███╗
  ██╔══██╗██║██║╚██╗██║██║   ██║
  ██████╔╝██║██║ ╚████║╚██████╔╝
  ╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ """
    print(f"{config.CYAN}{config.BOLD}{bing_art}{config.RESET}")
    print(
        f"{config.BOLD}{config.WHITE} Phiên bản: {config.YELLOW}v2.1 (Anti-Freeze & Mobile Rewards Fix){config.RESET} | "
        f"{config.BOLD}{config.WHITE}Tốc độ: {config.GREEN}80 WPM{config.RESET}\n"
    )
    config.print_user_guide()


def wait_page_loaded(driver, timeout=15):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception:
        pass


def find_edge_path():
    path = shutil.which("msedge")
    if path:
        return path

    default_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe")
    ]

    for p in default_paths:
        if os.path.exists(p):
            return p

    return None


def type_human_like(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(config.MIN_TYPE_DELAY, config.MAX_TYPE_DELAY))


# ================= KEYWORDS =================
def generate_faker_keywords(n=50, filename=None):
    if filename is None:
        filename = os.path.join(config.BASE_DIR, "keywords.txt")
    print(f"{config.YELLOW}[*] Đang tạo {n} từ khóa tìm kiếm tự nhiên...{config.RESET}")
    fake = Faker()
    keywords = set()

    while len(keywords) < n:
        choice = random.randint(1, 3)
        if choice == 1:
            kw = fake.sentence(nb_words=3).replace(".", "")
        elif choice == 2:
            kw = f"{fake.word()} {fake.job()}"
        else:
            kw = f"{fake.company()} research"

        kw = kw.replace("\n", " ").strip()
        keywords.add(kw)

    keywords_list = list(keywords)

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(keywords_list))

        print(f"{config.GREEN}[OK] Đã lưu {len(keywords_list)} từ khóa vào {filename}{config.RESET}\n")
        return keywords_list

    except Exception as e:
        print(f"{config.RED}[!] Lỗi ghi file keywords: {e}{config.RESET}")
        return []


# ================= EMULATION (CDP) =================
def enable_mobile_emulation(driver):
    """
    Kích hoạt giả lập Microsoft Edge trên Android thông qua Chrome DevTools Protocol.
    Đảm bảo đầy đủ Client Hints, Touch Events và Viewport để Bing Rewards ghi nhận điểm Mobile.
    """
    # 1. Ghi đè User-Agent và Client Hints
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": config.MOBILE_USER_AGENT,
        "acceptLanguage": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "platform": "Linux armv81",
        "userAgentMetadata": {
            "brands": [
                {"brand": "Not/A)Brand", "version": "8"},
                {"brand": "Chromium", "version": "124"},
                {"brand": "Microsoft Edge", "version": "124"}
            ],
            "fullVersion": "124.0.0.0",
            "platform": "Android",
            "platformVersion": "14.0.0",
            "architecture": "arm",
            "model": "SM-S928B",
            "mobile": True,
            "bitness": "64"
        }
    })

    # 2. Ghi đè thông số màn hình di động
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "width": config.MOBILE_DEVICE_METRICS["width"],
        "height": config.MOBILE_DEVICE_METRICS["height"],
        "deviceScaleFactor": config.MOBILE_DEVICE_METRICS["deviceScaleFactor"],
        "mobile": True,
        "screenOrientation": {"type": "portraitPrimary", "angle": 0}
    })

    # 3. Kích hoạt cảm ứng chạm (Touch)
    driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {
        "enabled": True,
        "maxTouchPoints": 5
    })


def disable_mobile_emulation(driver):
    """Khôi phục trạng thái trình duyệt Desktop chuẩn."""
    driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
    driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {"enabled": False})
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ""})


# ================= DRIVER SETUP (PERSISTENT PROFILE) =================
def get_driver(edge_path):
    """
    Khởi tạo EdgeDriver với Persistent Profile để lưu giữ phiên đăng nhập Microsoft Rewards.
    """
    options = webdriver.EdgeOptions()
    options.binary_location = edge_path

    # Đường dẫn Profile cố định
    profile_path = config.EDGE_PROFILE_DIR
    os.makedirs(profile_path, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--profile-directory=Default")

    # Tối ưu chống phát hiện bot & loại bỏ banner không mong muốn
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_experimental_option(
        'excludeSwitches', ['enable-logging', 'enable-automation']
    )
    options.add_experimental_option('useAutomationExtension', False)

    try:
        service = EdgeService(EdgeChromiumDriverManager().install())
    except Exception as e:
        print(f"{config.YELLOW}[!] Không tải được EdgeDriver tự động ({e}), dùng EdgeDriver hệ thống...{config.RESET}")
        service = EdgeService()

    try:
        driver = webdriver.Edge(service=service, options=options)
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"\n{config.RED}[ERROR] Không thể khởi động Microsoft Edge!{config.RESET}")
        print(f"{config.YELLOW}[GỢI Ý KHẮC PHỤC]:{config.RESET}")
        print(f"  1. Hãy đóng tất cả các cửa sổ Microsoft Edge đang mở trên máy tính.")
        print(f"  2. Đảm bảo Edge không bị tiến trình nền nào khóa thư mục profile.")
        print(f"  Chi tiết lỗi: {e}\n")
        raise e


def check_login_status(driver):
    """Kiểm tra và nhắc nhở đăng nhập tài khoản Microsoft Rewards."""
    try:
        driver.get("https://www.bing.com")
        wait_page_loaded(driver)
        handle_bing_prompts(driver)

        # Kiểm tra icon profile hoặc nút đăng nhập
        sign_in_elements = driver.find_elements(By.ID, "id_s")
        if sign_in_elements and sign_in_elements[0].is_displayed():
            print(f"\n{config.YELLOW}[LƯU Ý QUAN TRỌNG]: Bạn chưa đăng nhập tài khoản Microsoft trên profile này!{config.RESET}")
            print(f"{config.CYAN}Vui lòng đăng nhập trên cửa sổ trình duyệt Edge vừa mở.{config.RESET}")
            print(f"{config.CYAN}Tool sẽ tạm dừng 30 giây để bạn đăng nhập...{config.RESET}")
            for sec in range(30, 0, -5):
                print(f"  Đang chờ đăng nhập: {sec}s còn lại...")
                time.sleep(5)
            print(f"{config.GREEN}[OK] Tiếp tục quy trình tìm kiếm.{config.RESET}\n")
        else:
            print(f"{config.GREEN}[OK] Đã nhận diện phiên làm việc tài khoản Microsoft.{config.RESET}\n")
    except Exception:
        pass


def get_rewards_breakdown(driver, retries=2):
    """
    Truy vấn trực tiếp trang rewards.bing.com và mở modal Points breakdown
    để lấy chính xác số điểm PC Search và Mobile Search hiện tại.
    """
    for attempt in range(retries):
        try:
            # Tạm tắt mobile emulation để modal Points breakdown hiển thị đầy đủ
            try:
                disable_mobile_emulation(driver)
            except Exception:
                pass

            driver.get("https://rewards.bing.com/earn")
            wait_page_loaded(driver, timeout=8)
            handle_bing_prompts(driver)

            try:
                link = WebDriverWait(driver, 6).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Points breakdown')]"))
                )
                driver.execute_script("arguments[0].click();", link)
            except Exception:
                driver.execute_script("window.scrollBy(0, 200);")
                time.sleep(1)
                links = driver.find_elements(By.XPATH, "//*[contains(text(), 'Points breakdown')]")
                if not links:
                    continue
                driver.execute_script("arguments[0].click();", links[0])

            time.sleep(2.5)

            text = driver.execute_script("""
                var modal = document.querySelector('[role=\"dialog\"], .modal, mee-rewards-points-breakdown-modal');
                return modal ? modal.innerText : '';
            """)

            data = {"desktop": None, "mobile": None, "today": None}
            m_today = re.search(r"Today's points\s*\n\s*(\d+)", text, re.I)
            if m_today:
                data["today"] = int(m_today.group(1))

            m_pc = re.search(r"Desktop Bing search\s*\n\s*(\d+)\s*/\s*(\d+)", text, re.I)
            if m_pc:
                data["desktop"] = (int(m_pc.group(1)), int(m_pc.group(2)))

            m_mob = re.search(r"Mobile Bing search\s*\n\s*(\d+)\s*/\s*(\d+)", text, re.I)
            if m_mob:
                data["mobile"] = (int(m_mob.group(1)), int(m_mob.group(2)))

            if data["desktop"] is not None or data["mobile"] is not None:
                return data
        except Exception:
            time.sleep(1.5)
            continue

    return None


# ================= SEARCH SESSION =================
def perform_search_session(driver, keywords, mode_name, is_mobile=False):
    wait = WebDriverWait(driver, 12)
    print(f"\n{config.MAGENTA}===================================================={config.RESET}")
    print(f"{config.MAGENTA}>>> BẮT ĐẦU PHIÊN TÌM KIẾM: {config.BOLD}{mode_name}{config.RESET}")
    print(f"{config.MAGENTA}===================================================={config.RESET}")

    if is_mobile:
        enable_mobile_emulation(driver)
        print(f"{config.CYAN}[*] Đã kích hoạt giả lập Edge Android (EdgA) + Touch Emulation.{config.RESET}")
    else:
        disable_mobile_emulation(driver)
        print(f"{config.CYAN}[*] Đã thiết lập chế độ Desktop tiêu chuẩn.{config.RESET}")

    try:
        driver.get("https://www.bing.com")
        wait_page_loaded(driver)
        handle_bing_prompts(driver)

        total_words = len(keywords)
        for i, word in enumerate(keywords, start=1):
            config.print_progress(i, total_words, f"[{mode_name}] {word}")

            try:
                # Đảm bảo cuộn về đỉnh trang để search box luôn hiển thị trên Mobile Viewport
                try:
                    driver.execute_script("window.scrollTo({top: 0, behavior: 'instant'});")
                    time.sleep(0.3)
                except Exception:
                    pass

                # Xử lý dọn dẹp popup trước mỗi lượt gõ
                handle_bing_prompts(driver)

                # Tìm kiếm ô nhập liệu (loại bỏ nút submit)
                search_box = None
                for selector in ["#sb_form_q", "textarea[name='q']", "input[name='q']"]:
                    try:
                        box = driver.find_element(By.CSS_SELECTOR, selector)
                        if box.is_displayed():
                            search_box = box
                            break
                    except Exception:
                        continue

                if not search_box:
                    search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))

                # Ghi nhận phần tử kết quả hiện tại trước khi submit để kiểm tra staleness
                existing_results = driver.find_elements(By.ID, "b_results")

                # Click an toàn và xóa từ khóa cũ
                safe_click(driver, search_box)
                search_box.clear()
                try:
                    search_box.send_keys(Keys.CONTROL + "a")
                    search_box.send_keys(Keys.BACKSPACE)
                except Exception:
                    pass

                # Gõ phím mô phỏng người thật
                type_human_like(search_box, word)
                search_box.send_keys(Keys.ENTER)

                # Kiểm tra chuyển trang an toàn (tránh đè lệnh submit gây hỏng request)
                time.sleep(1.2)
                curr_url_unquoted = urllib.parse.unquote_plus(driver.current_url).lower()
                if "q=" not in driver.current_url or word.lower() not in curr_url_unquoted:
                    try:
                        search_box.submit()
                    except Exception:
                        try:
                            go_btn = driver.find_element(By.CSS_SELECTOR, "#sb_form_go, button[type='submit'], label[for='sb_form_go']")
                            safe_click(driver, go_btn)
                        except Exception:
                            pass

                # Đợi trang kết quả cũ chuyển sang trang mới (staleness check)
                if existing_results:
                    try:
                        WebDriverWait(driver, 5).until(EC.staleness_of(existing_results[0]))
                    except Exception:
                        pass

                # Đợi trang kết quả tìm kiếm (#b_results) tải xong
                # Đây là điều kiện tiên quyết để Microsoft Rewards ghi nhận điểm
                try:
                    wait.until(EC.presence_of_element_located((By.ID, "b_results")))
                except Exception:
                    wait_page_loaded(driver, timeout=6)

                # Cuộn trang 2 chiều để kích hoạt đầy đủ telemetry beacon của Microsoft Rewards
                try:
                    scroll_y = random.randint(280, 480)
                    driver.execute_script(f"window.scrollBy(0, {scroll_y});")
                    time.sleep(random.uniform(1.5, 2.5))
                    scroll_back = random.randint(60, 160)
                    driver.execute_script(f"window.scrollBy(0, -{scroll_back});")
                    time.sleep(0.5)
                    driver.execute_script("window.scrollTo({top: 0, behavior: 'instant'});")
                except Exception:
                    pass

                # Nghỉ ngẫu nhiên giữa các lượt tìm kiếm để Bing ghi nhận điểm
                delay = round(random.uniform(config.MIN_SEARCH_DELAY, config.MAX_SEARCH_DELAY), 1)
                time.sleep(delay)

            except Exception as e:
                print(f"{config.RED}[!] Lỗi khi search '{word}': {e}{config.RESET}")
                try:
                    driver.get("https://www.bing.com")
                    wait_page_loaded(driver)
                    handle_bing_prompts(driver)
                except Exception:
                    pass

    except Exception as e:
        print(f"{config.RED}[!] Lỗi phiên {mode_name}: {e}{config.RESET}")

    finally:
        print(f"{config.GREEN}[OK] Hoàn thành phiên {mode_name}.{config.RESET}\n")


# ================= COOLDOWN & INTERACTION =================
def wait_cooldown(seconds=config.COOLDOWN_SECONDS):
    """
    Đếm ngược thời gian nghỉ cooldown 15 phút.
    Cho phép bấm phím [Enter] hoặc [Space] để bỏ qua chờ hoặc [Ctrl+C] để dừng an toàn.
    """
    print(f"\n{config.YELLOW}╔══════════════════════════════════════════════════════════════════════╗{config.RESET}")
    print(f"{config.YELLOW}║            {config.BOLD}KÍCH HOẠT THỜI GIAN NGHỈ COOLDOWN 15 PHÚT AN TOÀN{config.RESET}{config.YELLOW}         ║{config.RESET}")
    print(f"{config.YELLOW}╠══════════════════════════════════════════════════════════════════════╣{config.RESET}")
    print(f"{config.YELLOW}║  Microsoft Rewards giới hạn chỉ tính điểm cho 3-4 lượt search/15p.    ║{config.RESET}")
    print(f"{config.YELLOW}║  Tool đang tạm nghỉ an toàn để tránh bị phạt 0 điểm.                 ║{config.RESET}")
    print(f"{config.YELLOW}║  {config.WHITE}[Mẹo]: Bạn có thể thu nhỏ cửa sổ này để làm việc khác.{config.RESET}{config.YELLOW}             ║{config.RESET}")
    print(f"{config.YELLOW}║         (Bấm phím [Enter] để bỏ qua chờ | [Ctrl+C] để dừng)           ║{config.RESET}")
    print(f"{config.YELLOW}╚══════════════════════════════════════════════════════════════════════╝{config.RESET}\n")

    for remaining in range(seconds, 0, -1):
        mins = remaining // 60
        secs = remaining % 60
        bar_len = 15
        prog = (seconds - remaining) / seconds
        filled = int(bar_len * prog)
        bar = "█" * filled + "░" * (bar_len - filled)
        sys.stdout.write(f"\r  {config.CYAN}[COOLDOWN]{config.RESET} {bar} {config.BOLD}{config.YELLOW}{mins:02d}:{secs:02d}{config.RESET} còn lại... ")
        sys.stdout.flush()

        if sys.platform == "win32":
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in [b'\r', b'\n', b' ']:
                    print(f"\n{config.GREEN}[INFO] Người dùng đã chủ động bỏ qua thời gian chờ cooldown.{config.RESET}\n")
                    return True
        time.sleep(1)

    print(f"\n{config.GREEN}[OK] Đã hoàn thành 15 phút giãn cách! Tiếp tục đợt tìm kiếm tiếp theo...{config.RESET}\n")
    return True


def choose_run_mode():
    """
    Cho phép chọn chế độ chạy hoặc tự động chọn Auto-Pilot sau 5 giây nếu không nhập.
    """
    for arg in sys.argv[1:]:
        if arg in ["--auto", "-a"]:
            return "auto"
        elif arg in ["--single", "-s"]:
            return "single"
        elif arg in ["--fast", "--all", "-f"]:
            return "fast"

    print(f"\n{config.CYAN}╔══════════════════════════════════════════════════════════════════════╗{config.RESET}")
    print(f"{config.CYAN}║                    {config.BOLD}{config.WHITE}CHỌN CHẾ ĐỘ TÌM KIẾM BING REWARDS{config.RESET}{config.CYAN}                 ║{config.RESET}")
    print(f"{config.CYAN}╠══════════════════════════════════════════════════════════════════════╣{config.RESET}")
    print(f"{config.CYAN}║  {config.BOLD}{config.GREEN}[1] Tự động hoàn toàn (Auto-Cooldown) [KHUYÊN DÙNG]{config.RESET}{config.CYAN}                 ║{config.RESET}")
    print(f"{config.CYAN}║      - Tìm 4 lượt (12đ) -> Chờ 15p -> Tự lặp lại đến khi FULL 150đ   ║{config.RESET}")
    print(f"{config.CYAN}║      - An toàn 100%, khắc phục triệt để lỗi 0/60 Mobile do cooldown  ║{config.RESET}")
    print(f"{config.CYAN}║                                                                      ║{config.RESET}")
    print(f"{config.CYAN}║  {config.YELLOW}[2] Chạy 1 đợt an toàn (4 lượt / 12 điểm) rồi dừng{config.RESET}{config.CYAN}                  ║{config.RESET}")
    print(f"{config.CYAN}║                                                                      ║{config.RESET}")
    print(f"{config.CYAN}║  {config.RED}[3] Chạy một mạch tất cả (Không nghỉ 15 phút){config.RESET}{config.CYAN}                          ║{config.RESET}")
    print(f"{config.CYAN}╚══════════════════════════════════════════════════════════════════════╝{config.RESET}")

    timeout = 5
    print(f"\n{config.YELLOW}[*] Tự động chọn chế độ [1] sau {timeout} giây nếu không bấm phím...{config.RESET}")

    if sys.platform == "win32":
        import msvcrt
        start_t = time.time()
        while time.time() - start_t < timeout:
            rem = int(timeout - (time.time() - start_t)) + 1
            sys.stdout.write(f"\r  Nhập lựa chọn [1, 2, 3] (mặc định [1] sau {rem}s): ")
            sys.stdout.flush()
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                try:
                    ch_str = ch.decode().strip()
                except Exception:
                    ch_str = ""
                print(ch_str)
                if ch_str == "2":
                    return "single"
                elif ch_str == "3":
                    return "fast"
                else:
                    return "auto"
            time.sleep(0.2)
        print(" 1 (Mặc định: Auto-Cooldown)")
        return "auto"

    return "auto"


# ================= MAIN =================
def run_tool():
    setup_console()
    print_header()

    edge_path = find_edge_path()
    if not edge_path:
        print(f"{config.RED}[!] Không tìm thấy Microsoft Edge trên hệ thống.{config.RESET}")
        return

    mode = choose_run_mode()

    driver = None
    try:
        print(f"\n{config.YELLOW}[*] Đang khởi động Microsoft Edge với Profile lưu trữ...{config.RESET}")
        driver = get_driver(edge_path)

        # Kiểm tra trạng thái đăng nhập
        check_login_status(driver)

        batch_idx = 1
        while True:
            # Lấy thống kê điểm số thực tế từ Microsoft Rewards
            print(f"\n{config.CYAN}[*] Đang kiểm tra chi tiết điểm Microsoft Rewards (Đợt {batch_idx})...{config.RESET}")
            breakdown = get_rewards_breakdown(driver)

            pc_cur, pc_max = 0, config.PC_SEARCH_COUNT * 3
            mob_cur, mob_max = 0, config.MOBILE_SEARCH_COUNT * 3

            if breakdown:
                print(f"\n{config.CYAN}╔══════════════════════════════════════════════════════════════════════╗{config.RESET}")
                print(f"{config.CYAN}║            {config.BOLD}{config.WHITE}THỐNG KÊ ĐIỂM MICROSOFT REWARDS HIỆN TẠI{config.RESET}{config.CYAN}                  ║{config.RESET}")
                print(f"{config.CYAN}╠══════════════════════════════════════════════════════════════════════╣{config.RESET}")
                if breakdown["today"] is not None:
                    print(f"{config.CYAN}║  {config.YELLOW}Tổng điểm hôm nay:{config.RESET}    {config.BOLD}{breakdown['today']} điểm{config.RESET}")
                if breakdown["desktop"]:
                    pc_cur, pc_max = breakdown["desktop"]
                    status = f"{config.GREEN}[ĐÃ ĐẠT TỐI ĐA]{config.RESET}" if pc_cur >= pc_max else f"{config.YELLOW}[CẦN SEARCH]{config.RESET}"
                    print(f"{config.CYAN}║  {config.YELLOW}Desktop Bing search:{config.RESET}  {config.BOLD}{pc_cur}/{pc_max}{config.RESET} điểm {status}")
                if breakdown["mobile"]:
                    mob_cur, mob_max = breakdown["mobile"]
                    status = f"{config.GREEN}[ĐÃ ĐẠT TỐI ĐA]{config.RESET}" if mob_cur >= mob_max else f"{config.YELLOW}[CẦN SEARCH]{config.RESET}"
                    print(f"{config.CYAN}║  {config.YELLOW}Mobile Bing search:{config.RESET}   {config.BOLD}{mob_cur}/{mob_max}{config.RESET} điểm {status}")
                print(f"{config.CYAN}╚══════════════════════════════════════════════════════════════════════╝{config.RESET}\n")

            pc_needed = max(0, (pc_max - pc_cur) // 3)
            mobile_needed = max(0, (mob_max - mob_cur) // 3)

            # Nếu cả 2 đều đã hoàn thành tối đa
            if pc_needed == 0 and mobile_needed == 0:
                print(f"{config.GREEN}{config.BOLD}[THÀNH CÔNG] Bạn đã đạt tối đa 100% điểm Microsoft Rewards hôm nay!{config.RESET}")
                break

            # Xác định giới hạn lượt tìm kiếm cho đợt này
            if mode in ["auto", "single"]:
                batch_limit = config.BATCH_SEARCH_COUNT
            else:
                batch_limit = 999

            executed_searches = 0

            # 1. Ưu tiên PC nếu còn thiếu
            if pc_needed > 0:
                count_this_batch = min(batch_limit, pc_needed)
                print(f"{config.YELLOW}[*] Đợt {batch_idx}: Thực hiện {count_this_batch} lượt tìm kiếm PC...{config.RESET}")
                pc_kws = generate_faker_keywords(count_this_batch)
                perform_search_session(driver, pc_kws, "PC_DESKTOP", is_mobile=False)
                executed_searches += count_this_batch
                batch_limit -= count_this_batch

            # 2. Thực hiện Mobile nếu còn quota trong batch và còn thiếu điểm mobile
            if mobile_needed > 0 and batch_limit > 0:
                count_this_batch = min(batch_limit, mobile_needed)
                print(f"{config.YELLOW}[*] Đợt {batch_idx}: Thực hiện {count_this_batch} lượt tìm kiếm Mobile...{config.RESET}")
                mob_kws = generate_faker_keywords(count_this_batch)
                perform_search_session(driver, mob_kws, "MOBILE_EDGE_ANDROID", is_mobile=True)
                executed_searches += count_this_batch

            # Nếu chọn chế độ Single-Batch: dừng sau 1 đợt an toàn
            if mode == "single":
                print(f"{config.GREEN}[INFO] Đã hoàn thành 1 đợt an toàn ({executed_searches} searches). Dừng tiến trình.{config.RESET}")
                break

            # Kiểm tra lại điểm số sau đợt vừa chạy
            post_bd = get_rewards_breakdown(driver)
            if post_bd:
                p_c, p_m = post_bd.get("desktop", (0, 0)) or (0, 0)
                m_c, m_m = post_bd.get("mobile", (0, 0)) or (0, 0)
                if p_c >= p_m and m_c >= m_m:
                    print(f"\n{config.GREEN}{config.BOLD}[THÀNH CÔNG] ĐÃ ĐẠT TỐI ĐA ĐIỂM HÔM NAY: Desktop {p_c}/{p_m} | Mobile {m_c}/{m_m}!{config.RESET}")
                    break

            # Nếu là chế độ auto (Auto-Cooldown) và vẫn còn điểm cần cày
            if mode == "auto":
                batch_idx += 1
                wait_cooldown(config.COOLDOWN_SECONDS)
            elif mode == "fast":
                # Chế độ fast đã chạy hết toàn bộ các lượt cần thiết
                break

        print(f"\n{config.BOLD}{config.GREEN}[HOÀN TẤT] KẾT THÚC QUY TRÌNH TỰ ĐỘNG.{config.RESET}")

    except Exception as e:
        print(f"{config.RED}[ERROR] Tiến trình gặp lỗi: {e}{config.RESET}")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

        try:
            kw_clean_path = os.path.join(config.BASE_DIR, 'keywords.txt')
            with open(kw_clean_path, 'w', encoding='utf-8') as f:
                pass
            print(f"{config.GREEN}[OK] Đã làm sạch file keywords.txt{config.RESET}")
        except Exception:
            pass


if __name__ == "__main__":
    run_tool()
