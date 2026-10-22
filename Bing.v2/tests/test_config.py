import os
import sys
import unittest

# Ensure Bing.v2 is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestConfig(unittest.TestCase):
    def test_config_constants_exist(self):
        import config
        self.assertGreater(config.PC_SEARCH_COUNT, 0)
        self.assertGreater(config.MOBILE_SEARCH_COUNT, 0)
        self.assertGreaterEqual(config.MIN_SEARCH_DELAY, 3)
        self.assertGreater(config.MAX_SEARCH_DELAY, config.MIN_SEARCH_DELAY)
        self.assertIn("EdgA", config.MOBILE_USER_AGENT)
        self.assertTrue(os.path.isabs(config.EDGE_PROFILE_DIR) or isinstance(config.EDGE_PROFILE_DIR, str))

    def test_quickedit_disable_function(self):
        import config
        self.assertTrue(hasattr(config, "disable_quickedit"))
        # Function should execute without raising exceptions
        result = config.disable_quickedit()
        self.assertIsInstance(result, bool)

    def test_user_guide_text(self):
        import config
        self.assertTrue(hasattr(config, "print_user_guide"))

if __name__ == "__main__":
    unittest.main()
