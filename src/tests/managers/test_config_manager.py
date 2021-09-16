from pathlib import Path
from unittest.mock import patch
import unittest
from unittest.mock import patch

from cli.managers.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.path = Path("path/to/application")
        self.config_manager = ConfigManager(config_dir=self.path)
        self.application = 'test_application'
        dummy_apps_config_dict = { "app_1" : {}, "app_2" : {} }

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

    def test_get_application_from_path(self):
        self.config_manager.get_application_from_path(self.path)
        with patch("cli.managers.config_manager.open", create=True) as mock_open, \
             patch("cli.managers.config_manager.json.load") as json_load_mock, \
             patch("cli.managers.config_manager.json.dump") as json_dump_mock:

            self.config_manager.add_application(application="application", path=Path('path/to/application'))
            mock_open.call_count = 2
            json_load_mock.assert_called_once()
            json_dump_mock.assert_called_once()

    def test_application_exists(self):
        with patch("cli.managers.config_manager.open") as mock_open, \
             patch("cli.managers.config_manager.json.load") as json_load_mock, \
             patch.object(ConfigManager, "_ConfigManager__check_and_create_config") as check_and_create_config_mock:

            # Return False because application equals key value
            check_and_create_config_mock.return_value = False
            json_load_mock.return_value = {"test_application": "test_application"}
            self.assertFalse(self.config_manager.application_exists(application=self.application))
            check_and_create_config_mock.assert_called_once()
            mock_open.assert_called_once()
            json_load_mock.assert_called_once()

            # Return True when __check_and_create_config returns True
            check_and_create_config_mock.return_value = True
            self.assertTrue(self.config_manager.application_exists(application=self.application))

            # Return True when key is not in application
            check_and_create_config_mock.return_value = False
            json_load_mock.return_value = {}
            self.assertTrue(self.config_manager.application_exists(application=self.application))

    def test__check_and_create_config(self):
        with patch("cli.managers.config_manager.open") as mock_open, \
             patch("cli.managers.config_manager.Path.exists") as mock_exists, \
             patch("cli.managers.config_manager.json.load") as json_load_mock, \
             patch("cli.managers.config_manager.json.dump") as json_dump_mock:

            mock_exists.return_value = False
            self.config_manager.application_exists(self.application)
            mock_exists.assert_called_once()
            mock_open.assert_called_once()
            json_dump_mock.assert_called_once()

            mock_exists.return_value = True
            self.config_manager.application_exists(self.application)
            json_load_mock.assert_called_once()
