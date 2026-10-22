import os
import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import bing_auto
from popup_handler import handle_bing_prompts, safe_click

class TestE2ELiveSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        edge_path = bing_auto.find_edge_path()
        options = webdriver.EdgeOptions()
        if edge_path:
            options.binary_location = edge_path
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        cls.driver = webdriver.Edge(options=options)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()

    def test_live_desktop_bing_search(self):
        self.driver.get("https://www.bing.com")
        handle_bing_prompts(self.driver)

        # Ensure search box is found and accessible
        search_box = self.driver.find_element(By.NAME, "q")
        self.assertIsNotNone(search_box)
        safe_click(self.driver, search_box)
        search_box.send_keys("Python automation test")
        search_box.send_keys(Keys.ENTER)

        # Wait for results
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "b_results"))
        )
        results = self.driver.find_elements(By.ID, "b_results")
        self.assertTrue(len(results) > 0)

    def test_live_mobile_emulation_search(self):
        # Switch to mobile via CDP
        bing_auto.enable_mobile_emulation(self.driver)
        self.driver.get("https://www.bing.com")
        bing_auto.wait_page_loaded(self.driver)
        time.sleep(2)
        handle_bing_prompts(self.driver)

        # Verify user-agent via JavaScript
        ua = self.driver.execute_script("return navigator.userAgent;")
        self.assertIn("EdgA", ua)

        # Perform mobile search
        search_box = self.driver.find_element(By.NAME, "q")
        safe_click(self.driver, search_box)
        search_box.send_keys("Edge Mobile test")
        search_box.send_keys(Keys.ENTER)
        time.sleep(1)
        if "test" not in self.driver.current_url.lower():
            try:
                search_box.submit()
            except Exception:
                try:
                    go_btn = self.driver.find_element(By.CSS_SELECTOR, "#sb_form_go, button[type='submit'], label[for='sb_form_go']")
                    safe_click(self.driver, go_btn)
                except Exception:
                    pass

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "b_results"))
        )
        results = self.driver.find_elements(By.ID, "b_results")
        self.assertTrue(len(results) > 0)

if __name__ == "__main__":
    unittest.main()
