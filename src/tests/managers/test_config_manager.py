import unittest
import os
from pathlib import Path
from unittest.mock import patch

from cli.managers.config_manager import ConfigManager
from cli.exceptions import ApplicationDoesNotExist, DirectoryIsFile


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.path = Path("dummy")
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

    def test_constructor(self):
        with patch("cli.managers.config_manager.os.path.isfile") as mock_is_file, \
             patch("cli.managers.config_manager.os.path.isdir") as mock_is_dir, \
             patch("cli.managers.config_manager.Path.mkdir") as mock_mkdir, \
             patch.object(ConfigManager, "check_config_exists") as check_config_exists_mock, \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config") as cleanup_config_mock, \
             patch("cli.managers.config_manager.write_json_file") as write_json_file_mock:
            # check for situation .qne is a file
            mock_is_file.return_value = True
            self.assertRaises(DirectoryIsFile, ConfigManager, self.path)

            # check for situation .qne doesn't exist, it is created and config is created
            mock_is_file.return_value = False
            mock_is_dir.return_value = False
            check_config_exists_mock.return_value = False
            config_manager = ConfigManager(self.path)
            mock_mkdir.assert_called_once_with(parents=True)
            write_json_file_mock.assert_called_once_with(config_manager.applications_config, {})

            # check for situation .qne does exist, config is cleaned
            mock_is_file.return_value = False
            mock_is_dir.return_value = True
            check_config_exists_mock.return_value = True
            ConfigManager(self.path)
            cleanup_config_mock.assert_called_once()

    def test__cleanup_config(self):
        with patch("cli.managers.config_manager.os.path.isfile") as mock_is_file, \
             patch("cli.managers.config_manager.os.path.isdir") as mock_is_dir, \
             patch.object(ConfigManager, "get_application_path") as mock_get_application_path, \
             patch.object(ConfigManager, "check_config_exists") as check_config_exists_mock, \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock, \
             patch("cli.managers.config_manager.write_json_file") as write_json_file_mock:

            read_json_file_mock.return_value = {self.application: {"path": str(self.path)}}
            mock_get_application_path.return_value = False

            mock_is_file.return_value = False
            mock_is_dir.return_value = True
            check_config_exists_mock.return_value = True
            config_manager = ConfigManager(self.path)
            read_json_file_mock.assert_called_with(config_manager.applications_config)
            write_json_file_mock.assert_called_once_with(config_manager.applications_config, {})

    def test_get_applications(self):
        with patch('cli.managers.config_manager.os.path.isfile', return_value=False), \
             patch('cli.managers.config_manager.os.path.isdir', return_value=True), \
             patch.object(ConfigManager, "check_config_exists", return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config"), \
             patch('cli.managers.config_manager.read_json_file',return_value=self.dummy_apps_config_dict), \
             patch("cli.managers.config_manager.write_json_file"):
            config_manager = ConfigManager(self.path)
            apps = config_manager.get_applications()
            self.assertEqual(len(apps), 2)
            for app in apps:
                self.assertIn('name', app)

    def test_add_application(self):
        with patch('cli.managers.config_manager.os.path.isfile', return_value=False), \
             patch('cli.managers.config_manager.os.path.isdir', return_value=True), \
             patch.object(ConfigManager, "check_config_exists", return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config"), \
             patch("cli.managers.config_manager.write_json_file") as write_json_file_mock, \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            read_json_file_mock.return_value = self.mock_read_json
            config_manager = ConfigManager(self.path)
            config_manager.add_application(application_name=self.caps_application, path=self.path)
            read_json_file_mock.assert_called_once()
            self.mock_read_json.update({"test_app": {"path": str(self.path / "test_app")}})
            write_json_file_mock.assert_called_once_with(self.path / "applications.json", self.mock_read_json)

    def test_application_exists(self):
        with patch('cli.managers.config_manager.os.path.isfile', return_value=False), \
             patch('cli.managers.config_manager.os.path.isdir', return_value=True), \
             patch.object(ConfigManager, "check_config_exists", return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config"), \
             patch("cli.managers.config_manager.os.path.exists", return_value=True), \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            # Return True when application equals key value
            read_json_file_mock.return_value = {"test_application": {"path": "path"}}
            config_manager = ConfigManager(self.path)
            self.assertEqual(config_manager.application_exists(application_name=self.application), (True, 'path'))
            read_json_file_mock.assert_called_with(config_manager.applications_config)

            # Return False when key is not in application
            read_json_file_mock.reset_mock()
            read_json_file_mock.return_value = {}
            self.assertEqual(config_manager.application_exists(application_name=self.application), (False, None))
            read_json_file_mock.assert_called_once_with(config_manager.applications_config)

            # Check case sensitivity of application name
            read_json_file_mock.return_value = {"test_application": {"path": "path"},
                                                "another_application": {"path": "path"}}
            self.assertEqual(config_manager.application_exists(application_name="ANOTHER_appLicaTION"),
                             (True, 'path'))

    def test_check_config_exists(self):
        with patch('cli.managers.config_manager.os.path.isfile', return_value=False), \
             patch('cli.managers.config_manager.os.path.isdir', return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config"), \
             patch("cli.managers.config_manager.Path.is_file") as mock_is_file:

            mock_is_file.return_value = True
            config_manager = ConfigManager(self.path)
            self.assertTrue(config_manager.check_config_exists())
            mock_is_file.assert_called()

            # check_config_exists return False when config file doesn't exist
            mock_is_file.reset_mock()
            mock_is_file.return_value = False
            self.assertFalse(config_manager.check_config_exists())
            mock_is_file.assert_called_once()

    def test_get_application_from_path(self):
        with patch('cli.managers.config_manager.os.path.isfile', return_value=False), \
             patch('cli.managers.config_manager.os.path.isdir', return_value=True), \
             patch.object(ConfigManager, "check_config_exists", return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config"), \
             patch("cli.managers.config_manager.os.path.exists", return_value=True), \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            config_manager = ConfigManager(self.path)
            read_json_file_mock.return_value = {self.application: {"path": os.path.join(str(self.path), '')}}

            app_name, _ = config_manager.get_application_from_path(self.path)
            self.assertEqual(app_name, self.application)

            read_json_file_mock.assert_called_with(config_manager.applications_config)

            # Raise ApplicationDoesntExist() when the application path doesn't match any of the paths
            read_json_file_mock.reset_mock()
            read_json_file_mock.return_value = {"application2": {"path": os.path.join('no', 'matching', 'path', '')}}

            self.assertRaises(ApplicationDoesNotExist, config_manager.get_application_from_path, self.path)

            read_json_file_mock.assert_called_with(config_manager.applications_config)

    def test_get_application_path(self):
        with patch('cli.managers.config_manager.os.path.isfile', return_value=False), \
             patch('cli.managers.config_manager.os.path.isdir', return_value=True), \
             patch.object(ConfigManager, "check_config_exists", return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config"), \
             patch.object(ConfigManager, "get_application") as get_application_mock:

            config_manager = ConfigManager(self.path)
            self.assertIsNone(config_manager.get_application_path(self.application))
            get_application_mock.assert_called_once_with(self.application)

    def test_get_application_path_existing_path(self):
        with patch('cli.managers.config_manager.os.path.isfile', return_value=False), \
             patch('cli.managers.config_manager.os.path.isdir', return_value=True), \
             patch.object(ConfigManager, "check_config_exists", return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config"), \
             patch("cli.managers.config_manager.os.path.exists", return_value=True), \
             patch.object(ConfigManager, "get_application") as get_application_mock:

            config_manager = ConfigManager(self.path)
            get_application_mock.return_value = {"path": os.path.join(str(self.path), ''), "name": self.application}
            self.assertEqual(config_manager.get_application_path(self.application),
                             os.path.join(str(self.path), ''))
            get_application_mock.assert_called_once_with(self.application)

    def test_application_file_non_existing_exception(self):
        with patch("cli.managers.config_manager.os.path.isfile", return_value=False), \
             patch('cli.managers.config_manager.os.path.isdir', return_value=True), \
             patch.object(ConfigManager, "check_config_exists", return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config"), \
             patch("cli.managers.config_manager.read_json_file") as read_json_file_mock:

            config_manager = ConfigManager(self.path)
            read_json_file_mock.return_value = {"application": {"path": "dummy"}}
            self.assertRaises(ApplicationDoesNotExist, config_manager.get_application_from_path,
                              Path("path/to/application"))
            read_json_file_mock.assert_called_with(config_manager.applications_config)

    def test_get_application(self):
        with patch("cli.managers.config_manager.os.path.isfile", return_value=False), \
             patch('cli.managers.config_manager.os.path.isdir', return_value=True), \
             patch.object(ConfigManager, "check_config_exists", return_value=True), \
             patch.object(ConfigManager, "_ConfigManager__cleanup_config"), \
             patch.object(ConfigManager, "get_applications") as mock_get_all_applications:

            config_manager = ConfigManager(self.path)
            mock_get_all_applications.return_value = [self.app_1, self.app_2]
            app_details = config_manager.get_application('app_1')
            self.assertDictEqual(app_details, self.app_1)

            # Check case sensitivity of application name
            app_details = config_manager.get_application('APP_2')
            self.assertDictEqual(app_details, self.app_2)

            app_details = config_manager.get_application('app1-non-existent')
            self.assertIsNone(app_details)
