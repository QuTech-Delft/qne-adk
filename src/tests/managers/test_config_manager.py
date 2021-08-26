import json
from pathlib import Path
from unittest.mock import patch, mock_open
import unittest

from cli.exceptions import MalformedJsonFile
from cli.managers.config_manager import ConfigManager
from cli.settings import Settings


class TestConfigManager(unittest.TestCase):
    def test_get_applications(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))

        dummy_apps_config = "{" \
                                "\"app_1\" : {\"path\": \"/some/path/\"," \
                                              "\"application_id\": 1}," \
                                "\"app_2\" : {\"path\": \"/some/path/\"," \
                                              "\"application_id\": 2}" \
                            "}"

        with patch('cli.managers.config_manager.open', mock_open(read_data=dummy_apps_config)) as m ,\
             patch('pathlib.Path.is_file',return_value=True):
            apps = config_manager.get_applications()
            self.assertEqual(len(apps), 2)
            for app in apps:
                self.assertIn('name', app)

    def test_get_applications_no_config(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))

        with patch('cli.managers.config_manager.open', mock_open(read_data="{}")) as m ,\
             patch('pathlib.Path.is_file',return_value=False):
            apps = config_manager.get_applications()
            self.assertEqual(len(apps), 0)

    def test_get_applications_invalid_config(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        malformed_apps_config = "{" \
                            "\"app_1\"  {\"path\" \"/some/path/\"," \
                            "\"application_id\" 1}," \
                            "\"app_2\"  {\"path\" \"/some/path/\"," \
                            "\"application_id\" 2}" \
                            "}"

        with patch('cli.managers.config_manager.open', mock_open(read_data=malformed_apps_config)) as m ,\
             patch('pathlib.Path.is_file',return_value=True):

            self.assertRaises(MalformedJsonFile, config_manager.get_applications)

    def test_add_application(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        assert config_manager.add_application('app_name', 'path') is None

    def test_delete_application(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        assert config_manager.delete_application('app_name') is None

    def test_get_application(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        assert config_manager.get_application('app_name') is None

    def test_get_application_from_path(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        app_data = config_manager.get_application_from_path('path')
        self.assertEqual(app_data[0], 'key')
        self.assertDictEqual(app_data[1], {})

    def test_application_exists(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        assert config_manager.application_exists('app_name') is True

    def test_update_path(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        assert config_manager.update_path('app_name', 'path') is None
