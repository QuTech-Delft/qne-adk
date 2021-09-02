from pathlib import Path
from unittest.mock import patch
import unittest

from cli.managers.config_manager import ConfigManager
from cli.settings import Settings


class TestConfigManager(unittest.TestCase):
    def test_get_applications(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        dummy_apps_config_dict = { "app_1" : {}, "app_2" : {} }

        with patch('pathlib.Path.is_file',return_value=True), \
             patch('cli.managers.config_manager.read_json_file',return_value=dummy_apps_config_dict):
            apps = config_manager.get_applications()
            self.assertEqual(len(apps), 2)
            for app in apps:
                self.assertIn('name', app)

    def test_get_applications_no_config(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))

        with patch('pathlib.Path.is_file',return_value=False):
            apps = config_manager.get_applications()
            self.assertEqual(len(apps), 0)
