import unittest
from pathlib import Path
from unittest.mock import patch

from cli.managers.config_manager import ConfigManager
from cli.exceptions import ApplicationDoesNotExist, NoConfigFileExists


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.path = Path("dummy")
        self.config_manager = ConfigManager(config_dir=self.path)
        self.application = 'test_application'
        self.dummy_apps_config_dict = {"app_1": {}, "app_2": {}}

        with patch('pathlib.Path.is_file', return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config") as cleanup_config_mock, \
             patch('cli.managers.config_manager.read_json_file',return_value=self.dummy_apps_config_dict):
            apps = self.config_manager.get_applications()
            self.assertEqual(len(apps), 2)
            cleanup_config_mock.assert_called_once()
            for app in apps:
                self.assertIn('name', app)

    def test_add_application(self):
        with patch("cli.managers.config_manager.write_json_file") as write_json_file_mock, \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            self.config_manager.add_application(application_name=self.application, path=self.path)
            read_json_file_mock.assert_called_once()
            write_json_file_mock.assert_called_once()

    def test_application_exists(self):
        with patch("cli.managers.config_manager.read_json_file") as read_json_file_mock, \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config") as cleanup_config_mock:

            # Return True when application equals key value
            cleanup_config_mock.return_value = True
            read_json_file_mock.return_value = {"test_application": {"path": "path"}}
            self.assertTrue(self.config_manager.application_exists(application_name=self.application))
            read_json_file_mock.assert_called_once_with(self.config_manager.applications_config)
            cleanup_config_mock.assert_called_once()

            # Return False when key is not in application
            cleanup_config_mock.reset_mock()
            read_json_file_mock.reset_mock()
            read_json_file_mock.return_value = {}
            self.assertEqual(self.config_manager.application_exists(application_name=self.application), (False, None))
            read_json_file_mock.assert_called_once_with(self.config_manager.applications_config)
            cleanup_config_mock.assert_called_once()

    def test_check_config_exists(self):
        with patch("cli.managers.config_manager.Path.is_file") as mock_is_file:

            mock_is_file.return_value = True
            self.assertTrue(self.config_manager.check_config_exists())
            mock_is_file.assert_called_once()

            # Raise NoConfigFileExists exception when mock_is_file is False
            mock_is_file.reset_mock()
            mock_is_file.return_value = False
            self.assertFalse(self.config_manager.check_config_exists())
            mock_is_file.assert_called_once()

    def test_create_config(self):
        with patch("cli.managers.config_manager.write_json_file") as write_json_file_mock:
            self.config_manager.create_config()
            write_json_file_mock.assert_called_once_with(self.config_manager.applications_config, {})

    def test_get_application(self):
        with patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:
            self.config_manager.get_application(self.application)
            read_json_file_mock.assert_called_once()

    def test_get_application_from_path(self):
        with patch.object(ConfigManager, "check_config_exists") as check_config_exists_mock, \
             patch.object(ConfigManager, "create_config") as create_config_mock, \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            read_json_file_mock.return_value = {self.application: {"path": str(self.path) + "/"}}
            check_config_exists_mock.return_value = True

            self.config_manager.get_application_from_path(self.path)

            check_config_exists_mock.assert_called_once()
            read_json_file_mock.assert_called_once_with(self.config_manager.applications_config)

            # Raise ApplicationDoesntExist() when the application path doesn't match any of the paths
            read_json_file_mock.reset_mock()
            check_config_exists_mock.reset_mock()
            read_json_file_mock.return_value = {"application2": {"path": "no/matching/path/"}}

            self.assertRaises(ApplicationDoesNotExist, self.config_manager.get_application_from_path, self.path)

            check_config_exists_mock.assert_called_once()
            read_json_file_mock.assert_called_once_with(self.config_manager.applications_config)

            # Check_config_exists() returns True
            read_json_file_mock.reset_mock()
            check_config_exists_mock.reset_mock()
            read_json_file_mock.return_value = {self.application: {"path": str(self.path) + "/"}}
            check_config_exists_mock.return_value = False
            self.config_manager.get_application_from_path(self.path)
            check_config_exists_mock.assert_called_once()
            create_config_mock.assert_called_once()
            read_json_file_mock.assert_called_once_with(self.config_manager.applications_config)

    def test_get_application_path(self):
        with patch.object(ConfigManager, "get_application") as get_application_mock:

            self.config_manager.get_application_path(self.application)
            get_application_mock.assert_called_once_with(self.application)

    def test_application_file_non_existing_exception(self):
        with patch("cli.managers.config_manager.os.path.isfile", return_value=False), \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock, \
             patch.object(ConfigManager, "check_config_exists") as check_config_exists_mock:

            check_config_exists_mock.return_value = True
            read_json_file_mock.return_value = {"application": {"path": "dummy"}}
            self.assertRaises(ApplicationDoesNotExist, self.config_manager.get_application_from_path,
                              Path("path/to/application"))
            check_config_exists_mock.assert_called_once()
            read_json_file_mock.assert_called_once_with(self.config_manager.applications_config)

    def test__cleanup_config(self):
        with patch.object(ConfigManager, "check_config_exists") as check_config_exists_mock, \
             patch("cli.managers.config_manager.os.path.exists") as exists_mock, \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock, \
             patch("cli.managers.config_manager.write_json_file") as write_json_file_mock:

            read_json_file_mock.return_value = {self.application: {"path": str(self.path)}}
            exists_mock.return_value = False

            self.assertEqual(self.config_manager.application_exists(self.application), (False, None))

            check_config_exists_mock.return_value = True
            read_json_file_mock.assert_called_with(self.config_manager.applications_config)
            write_json_file_mock.assert_called_once_with(self.config_manager.applications_config, {})

            # Raise NoConfigFileExists() when check_config_exists() returns false
            check_config_exists_mock.reset_mock()
            check_config_exists_mock.return_value = False
            self.assertRaises(NoConfigFileExists, self.config_manager.application_exists, self.application)
