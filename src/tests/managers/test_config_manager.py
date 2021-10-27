import unittest
import os
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
        self.app_1 = {'name': 'app_1', 'path': "some-path-1"}
        self.app_2 = {'name': 'app_2', 'path': "some-path-2"}
        self.caps_application = 'TEST_APP'
        self.mock_read_json = {
              "app_1": {
                "path": "/home/abc/applications/app_1/"
              },
              "app_2": {
                "path": "/home/xyz/applications/app_2/"
              }
        }

    def test_get_applications(self):
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

            read_json_file_mock.return_value = self.mock_read_json

            self.config_manager.add_application(application_name=self.caps_application, path=self.path)
            read_json_file_mock.assert_called_once()
            self.mock_read_json.update({"test_app" : {"path": str(self.path / "test_app")}})
            write_json_file_mock.assert_called_once_with(self.path / "applications.json", self.mock_read_json)

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

            # Check case sensitivity of application name
            read_json_file_mock.return_value = {"test_application": {"path": "path"},
                                                "another_application": {"path": "path"}}
            self.assertTrue(self.config_manager.application_exists(application_name="ANOTHER_appLicaTION"))

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

    def test_get_application_from_path(self):
        with patch.object(ConfigManager, "check_config_exists") as check_config_exists_mock, \
             patch.object(ConfigManager, "create_config") as create_config_mock, \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            read_json_file_mock.return_value = {self.application: {"path": os.path.join(str(self.path), '')}}
            check_config_exists_mock.return_value = True

            self.config_manager.get_application_from_path(self.path)

            check_config_exists_mock.assert_called_once()
            read_json_file_mock.assert_called_once_with(self.config_manager.applications_config)

            # Raise ApplicationDoesntExist() when the application path doesn't match any of the paths
            read_json_file_mock.reset_mock()
            check_config_exists_mock.reset_mock()
            read_json_file_mock.return_value = {"application2": {"path": os.path.join('no', 'matching', 'path', '')}}

            self.assertRaises(ApplicationDoesNotExist, self.config_manager.get_application_from_path, self.path)

            check_config_exists_mock.assert_called_once()
            read_json_file_mock.assert_called_once_with(self.config_manager.applications_config)

            # Check_config_exists() returns True
            read_json_file_mock.reset_mock()
            check_config_exists_mock.reset_mock()
            read_json_file_mock.return_value = {self.application: {"path": os.path.join(str(self.path), '')}}
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

    def test_get_application(self):
        with patch.object(ConfigManager, "get_applications") as mock_get_all_applications:
            mock_get_all_applications.return_value = [self.app_1, self.app_2]
            app_details = self.config_manager.get_application('app_1')
            self.assertDictEqual(app_details, self.app_1)

            # Check case sensitivity of application name
            app_details = self.config_manager.get_application('APP_2')
            self.assertDictEqual(app_details, self.app_2)

            app_details = self.config_manager.get_application('app1-non-existent')
            self.assertIsNone(app_details)
