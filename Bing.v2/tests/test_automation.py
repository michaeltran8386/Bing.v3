import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestAutomation(unittest.TestCase):
    @unittest.skipIf(sys.platform != "win32", "Edge default path check is Windows-specific")
    def test_find_edge_path(self):
        import bing_auto
        path = bing_auto.find_edge_path()
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))

    def test_generate_faker_keywords(self):
        import bing_auto
        kws = bing_auto.generate_faker_keywords(10, filename="test_keywords.txt")
        self.assertEqual(len(kws), 10)
        self.assertTrue(os.path.exists("test_keywords.txt"))
        if os.path.exists("test_keywords.txt"):
            os.remove("test_keywords.txt")

    def test_switch_to_mobile_cdp(self):
        import bing_auto
        mock_driver = MagicMock()
        bing_auto.enable_mobile_emulation(mock_driver)
        self.assertEqual(mock_driver.execute_cdp_cmd.call_count, 3)

    def test_switch_to_pc_cdp(self):
        import bing_auto
        mock_driver = MagicMock()
        bing_auto.disable_mobile_emulation(mock_driver)
        self.assertEqual(mock_driver.execute_cdp_cmd.call_count, 3)

if __name__ == "__main__":
    unittest.main()
