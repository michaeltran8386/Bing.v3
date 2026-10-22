import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException
)

# Danh sách selector CSS các nút đóng / chấp nhận của Bing
CONSENT_SELECTORS = [
    "#bnp_btn_accept",
    "#bnp_close_link",
    "#id_bnp_btn_accept",
    "button.bnp_btn_accept",
    "button[id*='accept']",
    "button[id*='Accept']",
    "a[id*='accept']",
    "button[aria-label*='Accept']",
    "button[aria-label*='Đồng ý']",
    "button[aria-label*='Chấp nhận']",
    "#b_notificationContainer button",
    "#bnp_container a",
    "#bnp_container button",
    ".bnp_btn_reject",
    "button[id*='reject']",
    "button[id*='Reject']",
    "button[id*='close']",
    "button[aria-label*='Close']",
    "button[aria-label*='Đóng']",
]

# Các từ khóa text thường xuất hiện trên nút popup Bing tiếng Việt và tiếng Anh
CONSENT_TEXT_KEYWORDS = [
    "chấp nhận",
    "đồng ý",
    "xác nhận",
    "tiếp tục",
    "có",
    "accept",
    "agree",
    "got it",
    "maybe later",
    "không phải bây giờ",
    "not now",
    "i agree",
    "đóng"
]


def dismiss_overlays_js(driver) -> bool:
    """
    Ẩn hoặc gỡ bỏ các lớp phủ (overlay/modal/backdrop) trên Bing
    nếu chúng đang che khuất màn hình và ngăn cản click chuột.
    """
    js_code = """
    var dismissed = false;
    var overlaySelectors = [
        '.bnp_overlay_wrapper',
        '.bnp_cookie_banner',
        '#bnp_cookie_banner',
        '#bnp_container',
        '.b_modal',
        '#b_modal',
        '#b_notificationContainer',
        '.bnp_modal',
        '.modal-backdrop',
        'div[role="dialog"]',
        '#id_hbfo'
    ];
    for (var i = 0; i < overlaySelectors.length; i++) {
        var elements = document.querySelectorAll(overlaySelectors[i]);
        elements.forEach(function(el) {
            try {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.style.opacity = '0';
                el.style.pointerEvents = 'none';
                dismissed = true;
            } catch(e) {}
        });
    }
    return dismissed;
    """
    try:
        return bool(driver.execute_script(js_code))
    except Exception:
        return False


def handle_bing_prompts(driver) -> bool:
    """
    Tự động phát hiện và nhấp chấp nhận / đóng các thông báo hoặc dialog
    'Cung cấp data để phục vụ tốt hơn...', cookie GDPR, banner trên Bing.
    """
    # 0. Kiểm tra nhanh bằng JS: nếu không có bất kỳ container popup nào thì thoát ngay (tốc độ < 2ms)
    try:
        has_prompt = driver.execute_script(
            "var el = document.querySelector('#bnp_container, .b_modal, #b_modal, [role=\"dialog\"], #b_notificationContainer, .bnp_btn_accept, [id*=\"accept\"]');"
            "return !!(el && (el.offsetWidth > 0 || el.offsetHeight > 0 || window.getComputedStyle(el).display !== 'none'));"
        )
        if has_prompt is False:
            return False
    except Exception:
        pass

    handled = False

    # 1. Quét theo các CSS Selector phổ biến
    for selector in CONSENT_SELECTORS:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for btn in buttons:
                if btn.is_displayed():
                    try:
                        btn.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", btn)
                    handled = True
                    time.sleep(0.5)
                    break
            if handled:
                break
        except Exception:
            continue

    # 2. Quét theo Text tiếng Việt & tiếng Anh nếu chưa bấm được nút
    if not handled:
        for kw in CONSENT_TEXT_KEYWORDS:
            xpath = (
                f"//button[contains(translate(normalize-space(.), "
                f"'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯĂÂÊÔƠƯ', "
                f"'abcdefghijklmnopqrstuvwxyzàáâãèéêìíòóôõùúăđĩũơưăâêôơư'), '{kw}')] "
                f"| //a[contains(translate(normalize-space(.), "
                f"'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯĂÂÊÔƠƯ', "
                f"'abcdefghijklmnopqrstuvwxyzàáâãèéêìíòóôõùúăđĩũơưăâêôơư'), '{kw}')]"
            )
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    if el.is_displayed():
                        try:
                            el.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", el)
                        handled = True
                        time.sleep(0.5)
                        break
                if handled:
                    break
            except Exception:
                continue

    # 3. Luôn đảm bảo không có overlay nào còn cản trở
    dismiss_overlays_js(driver)
    return handled


def safe_click(driver, element) -> bool:
    """
    Thực hiện click an toàn vào một phần tử.
    Nếu bị chặn bởi dialog/popup, tự động xử lý popup và dùng JS click fallback.
    """
    try:
        element.click()
        return True
    except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
        handle_bing_prompts(driver)
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception:
            return False
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception:
            return False
