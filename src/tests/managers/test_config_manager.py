from pathlib import Path
import unittest
from unittest.mock import patch
from cli.managers.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.path = Path("dummy")
        self.config_manager = ConfigManager(config_dir=self.path)
        self.application = 'test_application'
        dummy_apps_config_dict = {"app_1": {}, "app_2": {}}

        with patch('pathlib.Path.is_file',return_value=True), \
             patch('cli.managers.config_manager.read_json_file',return_value=dummy_apps_config_dict):
            apps = self.config_manager.get_applications()
            self.assertEqual(len(apps), 2)
            for app in apps:
                self.assertIn('name', app)

    def test_get_applications_no_config(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        with patch('pathlib.Path.is_file',return_value=False):
            apps = config_manager.get_applications()
            self.assertEqual(len(apps), 0)

    def test_add_application(self):
        with patch("cli.managers.config_manager.write_json_file") as write_json_file_mock, \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            self.config_manager.add_application(application=self.application, path=self.path)
            read_json_file_mock.assert_called_once()
            write_json_file_mock.assert_called_once()

    def test_get_application_from_path(self):
        self.config_manager.get_application_from_path(self.path)
        with patch("cli.managers.config_manager.write_json_file") as write_json_file_mock, \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            self.config_manager.add_application(application=self.application, path=self.path)
            read_json_file_mock.assert_called_once()
            write_json_file_mock.assert_called_once()

    def test_application_exists(self):
        with patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            # Return True when application equals key value
            read_json_file_mock.return_value = {"test_application": {"path": "path"}}
            self.assertTrue(self.config_manager.application_exists(application=self.application))
            read_json_file_mock.assert_called_once()

            # Return False when key is not in application
            read_json_file_mock.reset_mock()
            read_json_file_mock.return_value = {}
            self.assertEqual(self.config_manager.application_exists(application=self.application), (False, None))

    def test_check_config_exists(self):
        with patch("cli.managers.config_manager.Path.is_file") as mock_is_file:

            self.config_manager.check_config_exists()
            mock_is_file.assert_called_once()

    def test_create_config(self):
        with patch("cli.managers.config_manager.write_json_file") as write_json_file_mock:
            self.config_manager.create_config()
            write_json_file_mock.assert_called_once_with(self.config_manager.app_config_file, {})
