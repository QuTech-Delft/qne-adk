import unittest

from pathlib import Path
from unittest.mock import patch

from cli.managers.config_manager import ConfigManager
from cli.api.local_api import LocalApi

class TestLocalApi(unittest.TestCase):

    def setUp(self) -> None:
        self.config_manager = ConfigManager(config_dir=Path("path/to/application"))
        self.local_api = LocalApi(config_manager=self.config_manager)

        self.application = "test_application"
        self.roles = ["Testrole1", "Testrole2"]
        self.path = Path("path/to/application")

        self.experiment_meta_local = {
            "backend": {
                "location": "local",
                "type": "local_netsquid"
             },
            "number_of_rounds": 1,
            "description": ""
        }

        self.experiment_data_local = {'meta': self.experiment_meta_local, 'asset': {}}

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
        with patch.object(LocalApi, "_LocalApi__is_structure_valid", return_value=True):
            self.local_api.is_application_valid(application=self.application)

    def test__is_config_valid(self):
        with patch.object(LocalApi, "_LocalApi__is_structure_valid", return_value=True),\
             patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=True):
            self.local_api.is_application_valid(application=self.application)

    def test_list_applications(self):
        with patch.object(ConfigManager, "get_applications") as get_applications_mock:
            self.local_api.list_applications()
            get_applications_mock.assert_called_once()

    def test_create_experiment(self):
        with patch("cli.api.local_api.write_json_file") as write_mock, \
            patch.object(LocalApi, "_LocalApi__copy_input_files_from_application") as copy_input_mock, \
            patch.object(LocalApi, "_LocalApi__create_asset_application") as create_app_asset_mock, \
            patch.object(LocalApi, "_LocalApi__create_asset_network") as create_network_asset_mock, \
            patch("cli.api.local_api.Path.is_dir") as is_dir_mock, \
            patch('cli.api.local_api.Path.mkdir') as mkdir_mock:

            is_dir_mock.return_value = False
            create_app_asset_mock.return_value = [{'x': 2}]
            create_network_asset_mock.return_value = {'z': 'z1'}

            self.local_api.create_experiment('test', {'foo': 'bar'}, 'network_1', Path('dummy'), 'app_name')

            is_dir_mock.assert_called_once()
            self.assertEqual(mkdir_mock.call_count, 2)
            copy_input_mock.assert_called_once_with('app_name', Path('dummy') / 'test' / 'input' )
            create_app_asset_mock.assert_called_once_with({'foo': 'bar'})
            create_network_asset_mock.assert_called_once_with('network_1', {'foo': 'bar'})

            self.experiment_data_local['meta']['description'] = 'test: experiment description'
            self.experiment_data_local['asset'] = {'network': {'z': 'z1'}, 'application': [{'x': 2}] }

            write_mock.assert_called_once_with(Path('dummy') / 'test' / 'experiment.json', self.experiment_data_local)

    def test_create_experiment_directory_exists(self):
        with patch("cli.api.local_api.Path.is_dir") as is_dir_mock:

            is_dir_mock.return_value = True
            is_created, message = self.local_api.create_experiment('test', {'foo': 'bar'}, 'network_1',
                                                                   Path('dummy'), 'app_name')

            self.assertEqual(is_created, False)
            self.assertEqual(message, 'Experiment directory test already exists.')

    def test_get_application_config(self):
        with patch.object(ConfigManager, "get_application") as get_application_mock, \
            patch("cli.api.local_api.read_json_file") as read_mock:

            read_mock.side_effect = [[{'app': 'foo'}], {'network': 'bar'}]
            config = self.local_api.get_application_config('test')
            get_application_mock.assert_called_once_with('test')
            self.assertEqual(read_mock.call_count, 2)
            self.assertDictEqual(config, {'application': [{'app': 'foo'}], 'network': {'network': 'bar'}})
