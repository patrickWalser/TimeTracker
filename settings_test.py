import unittest
import os
import json
from settings import Settings


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.test_filename = 'test_settings.json'
        self.settings = Settings(filename=self.test_filename)

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_load_settings_file_exists(self):
        # Create a test settings file
        test_data = {"last_filename": "test_file.txt"}
        with open(self.test_filename, 'w') as file:
            json.dump(test_data, file)

        # Load settings from the file
        self.settings.load_settings()

        # Check if settings were loaded correctly
        self.assertEqual(self.settings.get("last_filename"), "test_file.txt")

    def test_load_settings_file_not_exists(self):
        # Ensure the test settings file does not exist
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

        # Load settings (should create a new file with default settings)
        self.settings.load_settings()

        # Check if default settings were saved
        self.assertTrue(os.path.exists(self.test_filename))
        self.assertEqual(self.settings.get("last_filename"), None)


if __name__ == '__main__':
    unittest.main()
