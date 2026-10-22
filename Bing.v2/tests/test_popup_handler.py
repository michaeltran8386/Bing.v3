import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from selenium.webdriver.common.by import By

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestPopupHandler(unittest.TestCase):
    def test_popup_handler_imports(self):
        import popup_handler
        self.assertTrue(hasattr(popup_handler, "handle_bing_prompts"))
        self.assertTrue(hasattr(popup_handler, "safe_click"))
        self.assertTrue(hasattr(popup_handler, "dismiss_overlays_js"))

    def test_dismiss_overlays_js_executes_script(self):
        import popup_handler
        mock_driver = MagicMock()
        popup_handler.dismiss_overlays_js(mock_driver)
        mock_driver.execute_script.assert_called()

    def test_safe_click_success(self):
        import popup_handler
        mock_driver = MagicMock()
        mock_element = MagicMock()
        result = popup_handler.safe_click(mock_driver, mock_element)
        self.assertTrue(result)
        mock_element.click.assert_called_once()

    def test_safe_click_intercepted_fallback(self):
        import popup_handler
        from selenium.common.exceptions import ElementClickInterceptedException

        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_element.click.side_effect = ElementClickInterceptedException("Intercepted")

        result = popup_handler.safe_click(mock_driver, mock_element)
        self.assertTrue(result)
        mock_driver.execute_script.assert_called()

    def test_handle_bing_prompts_css_short_circuit(self):
        """Kiểm tra khi tìm thấy và click nút accept đầu tiên, vòng lặp phải dừng ngay lập tức."""
        import popup_handler
        mock_driver = MagicMock()
        mock_button = MagicMock()
        mock_button.is_displayed.return_value = True

        def find_elements_side_effect(by, selector):
            if selector == "#bnp_btn_accept":
                return [mock_button]
            return []

        mock_driver.find_elements.side_effect = find_elements_side_effect

        handled = popup_handler.handle_bing_prompts(mock_driver)
        self.assertTrue(handled)
        mock_button.click.assert_called_once()
        # Xác nhận find_elements chỉ được gọi đúng 1 lần cho selector đầu tiên, không quét tiếp 18 selector sau
        self.assertEqual(mock_driver.find_elements.call_count, 1)

    def test_handle_bing_prompts_xpath_uses_normalize_space(self):
        """Kiểm tra câu lệnh XPath tìm kiếm nút bằng text phải dùng normalize-space(.) thay vì text()."""
        import popup_handler
        mock_driver = MagicMock()
        # Giả lập không tìm thấy bằng CSS
        mock_driver.find_elements.return_value = []

        popup_handler.handle_bing_prompts(mock_driver)

        # Lấy tất cả các query XPath đã gọi
        xpath_calls = [call[0][1] for call in mock_driver.find_elements.call_args_list if call[0][0] == By.XPATH]
        self.assertTrue(len(xpath_calls) > 0)
        for xpath in xpath_calls:
            self.assertIn("normalize-space(.)", xpath)
            self.assertNotIn("text()", xpath)

if __name__ == "__main__":
    unittest.main()
