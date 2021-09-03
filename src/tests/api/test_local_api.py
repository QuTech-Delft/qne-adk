import unittest

from pathlib import Path
from unittest.mock import patch

from cli.managers.config_manager import ConfigManager
from cli.api.local_api import LocalApi


class ApplicationCreate(unittest.TestCase):

    def setUp(self) -> None:
        self.config_manager = ConfigManager(config_dir=Path("path/to/application"))
        self.local_api = LocalApi(config_manager=self.config_manager)

        self.application = "test_application"
        self.roles = ["Testrole1", "Testrole2"]
        self.path = Path("path/to/application")

    def test_create_application(self):
        with patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=True) as application_unique_mock, \
             patch.object(LocalApi, "_LocalApi__create_application_structure", return_value=True) as structure_mock:

            self.local_api.create_application(self.application, self.roles, self.path)

            application_unique_mock.assert_called_once_with(self.application)
            structure_mock.assert_called_once_with(self.application, self.roles, self.path)

    def test_create_file_structure(self):
        with patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=True) as application_unique_mock, \
             patch.object(ConfigManager, 'add_application', return_value=10) as config_manager_mock:

            self.local_api.create_application(self.application, self.roles, self.path)

            application_unique_mock.assert_called_once_with(self.application)
            config_manager_mock.assert_called_once_with(self.application, self.path)


    def test_is_application_unique(self):
        with patch.object(LocalApi, "_LocalApi__create_application_structure", return_value=True) as structure_mock, \
             patch.object(ConfigManager, "application_exists", return_value=True) as application_exists_mock:

            self.local_api.create_application(self.application, self.roles, self.path)
            structure_mock.assert_called_once_with(self.application, self.roles, self.path)
            application_exists_mock.assert_called_once_with(self.application)


    def test_is_application_valid(self):
        with patch.object(LocalApi, "_LocalApi__is_structure_valid", return_value=True) as is_structure_valid_mock, \
             patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=True) as \
             is_application_unique_mock, \
             patch.object(LocalApi, "_LocalApi__is_config_valid", return_value=True) as is_config_valid_mock:

            self.local_api.is_application_valid(application=self.application)
            is_structure_valid_mock.assert_called_once_with(self.application)
            is_application_unique_mock.assert_called_once_with(self.application)
            is_config_valid_mock.assert_called_once_with(self.application)

    def test__is_structure_valid(self):
            self.local_api.is_application_valid(application=self.application)

    def test__is_application_unique(self):
        with patch.object(LocalApi, "_LocalApi__is_structure_valid", return_value=True) as is_structure_valid_mock:
             self.local_api.is_application_valid(application=self.application)

    def test__is_config_valid(self):
        with patch.object(LocalApi, "_LocalApi__is_structure_valid", return_value=True) as is_structure_valid_mock,\
             patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=True) as \
             is_application_unique_mock:
             self.local_api.is_application_valid(application=self.application)



