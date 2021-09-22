import unittest
from pathlib import Path
from unittest.mock import patch

from cli.managers.config_manager import ConfigManager
from cli.managers.roundset_manager import RoundSetManager
from cli.api.local_api import LocalApi
from cli.output_converter import OutputConverter
from cli.exceptions import ApplicationAlreadyExists, NoNetworkAvailable


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
        with patch.object(LocalApi, "_LocalApi__is_application_unique") as is_application_unique_mock, \
             patch.object(LocalApi, "_LocalApi__create_application_structure") as structure_mock:

            is_application_unique_mock.return_value = True
            structure_mock.return_value = True
            self.local_api.create_application(self.application, self.roles, self.path)

            is_application_unique_mock.assert_called_once_with(self.application)
            structure_mock.assert_called_once_with(self.application, self.roles, self.path)

    def test__create_application_structure(self):
        with patch("cli.api.local_api.open") as open_mock, \
             patch('cli.api.local_api.Path.mkdir') as mock_mkdir, \
             patch("cli.api.local_api.utils.get_network_nodes") as check_network_nodes_mock, \
             patch("cli.api.local_api.utils.get_dummy_application") as get_dummy_application_mock, \
             patch("cli.api.local_api.shutil.rmtree") as rmtree_mock, \
             patch("cli.api.local_api.json.dump") as json_dump_mock, \
             patch("cli.api.local_api.utils.write_json_file") as write_json_file_mock, \
             patch("cli.api.local_api.utils.write_file") as write_file_mock, \
             patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=True) as application_unique_mock, \
             patch.object(ConfigManager, 'add_application', return_value=10) as config_manager_mock:

            check_network_nodes_mock.return_value = {"dummy_network": ["network1", "network2", "network3"]}
            get_dummy_application_mock.return_value = {'application': [{'roles': ['dummy_role']}]}
            self.local_api.create_application(self.application, self.roles, self.path)

            application_unique_mock.assert_called_once_with(self.application)
            config_manager_mock.assert_called_once_with(self.application, self.path)
            self.assertEqual(write_file_mock.call_count, 1 + len(self.roles))
            self.assertEqual(mock_mkdir.call_count, 2)
            write_json_file_mock.call_count = 3
            write_file_mock.call_count = 2
            check_network_nodes_mock.assert_called_once()
            get_dummy_application_mock.assert_called_once()
            application_unique_mock.assert_called_once_with(self.application)
            config_manager_mock.assert_called_once_with(self.application, self.path)
            json_dump_mock.call_count = 3

            # Raise exception when no network available
            check_network_nodes_mock.return_value = {}
            self.assertRaises(NoNetworkAvailable, self.local_api.create_application, self.application, self.roles,
                              self.path)
            rmtree_mock.assert_called_once()

    def test_is_application_unique(self):
        with patch.object(LocalApi, "_LocalApi__create_application_structure", return_value=True) as structure_mock, \
             patch.object(ConfigManager, "application_exists") as application_exists_mock:

            application_exists_mock.return_value = True
            self.assertRaises(ApplicationAlreadyExists, self.local_api.create_application, self.application, self.roles,
                                                                                          self.path)
            application_exists_mock.assert_called_once_with(self.application)

            structure_mock.reset_mock()
            application_exists_mock.reset_mock()
            application_exists_mock.return_value = False
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
        with patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=True) as \
             is_application_unique_mock:
            self.local_api.is_application_valid(application=self.application)
            is_application_unique_mock.assert_called_once_with(self.application)


    def test__is_config_valid(self):
        with patch.object(LocalApi, "_LocalApi__is_structure_valid", return_value=True),\
             patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=True):
            self.local_api.is_application_valid(application=self.application)

    def test_list_applications(self):
        with patch.object(ConfigManager, "get_applications") as get_applications_mock:
            self.local_api.list_applications()
            get_applications_mock.assert_called_once()

    def test_experiments_create(self):
        with patch.object(LocalApi, "get_network_data") as get_network_data_mock, \
             patch.object(LocalApi, "create_asset_network") as create_network_asset_mock, \
             patch.object(LocalApi, "create_experiment") as create_exp_mock:

            get_network_data_mock.return_value = {'a': 'b'}
            create_network_asset_mock.return_value = {'c': 'd'}
            self.local_api.experiments_create(name='name', app_config={'foo': 'bar'}, network_name='network_name',
                                                path=Path('dummy'), application='application')
            get_network_data_mock.assert_called_once_with(network_name='network_name')
            create_network_asset_mock.assert_called_once_with(network_data={'a': 'b'}, app_config={'foo': 'bar'})
            create_exp_mock.assert_called_once_with(name='name', app_config={'foo': 'bar'}, asset_network={'c':'d'},
                                                    path=Path('dummy'), application='application')

    def test_create_experiment(self):
        with patch("cli.api.local_api.write_json_file") as write_mock, \
             patch.object(LocalApi, "_LocalApi__copy_input_files_from_application") as copy_input_mock, \
             patch.object(LocalApi, "_LocalApi__create_asset_application") as create_app_asset_mock, \
             patch("cli.api.local_api.Path.is_dir") as is_dir_mock, \
             patch('cli.api.local_api.Path.mkdir') as mkdir_mock:

            is_dir_mock.return_value = False
            create_app_asset_mock.return_value = [{'x': 2}]

            self.local_api.create_experiment(name='test', app_config={'foo': 'bar'}, asset_network={'a': 'b'},
                                             path=Path('dummy'), application='app_name')

            is_dir_mock.assert_called_once()
            self.assertEqual(mkdir_mock.call_count, 2)
            copy_input_mock.assert_called_once_with('app_name', Path('dummy') / 'test' / 'input' )
            create_app_asset_mock.assert_called_once_with({'foo': 'bar'})

            self.experiment_data_local['meta']['description'] = 'test: experiment description'
            self.experiment_data_local['asset'] = {'network': {'a': 'b'}, 'application': [{'x': 2}] }

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
            get_application_mock.return_value = {'path': 'some-path'}
            config = self.local_api.get_application_config('test')
            get_application_mock.assert_called_once_with('test')
            self.assertEqual(read_mock.call_count, 2)
            self.assertDictEqual(config, {'application': [{'app': 'foo'}], 'network': {'network': 'bar'}})

    def test_validate_experiment(self):
        with patch("cli.api.local_api.Path.is_file") as is_file_mock, \
             patch.object(RoundSetManager, "validate_asset") as validate_asset_mock:

            is_file_mock.return_value = True
            validate_asset_mock.return_value= True, 'ok'
            is_valid, message = self.local_api.validate_experiment(Path('dummy'))
            is_file_mock.assert_called_once()
            validate_asset_mock.assert_called_once_with(Path('dummy'))
            self.assertEqual(is_valid, True)
            self.assertEqual(message, 'ok')

            is_file_mock.reset_mock()
            is_file_mock.return_value = False
            validate_asset_mock.reset_mock()
            is_valid, message = self.local_api.validate_experiment(Path('dummy'))
            is_file_mock.assert_called_once()
            self.assertEqual(is_valid, False)
            self.assertEqual(message, 'File experiment.json not found in the current working directory')
            validate_asset_mock.assert_not_called()

    def test_run_experiment(self):
        with patch.object(RoundSetManager, "prepare_input") as prepare_input_mock, \
             patch.object(RoundSetManager, "process") as process_mock, \
             patch.object(RoundSetManager, "terminate") as terminate_mock:

            self.local_api.run_experiment(Path('dummy'))
            prepare_input_mock.assert_called_once_with(Path('dummy'))
            process_mock.assert_called_once()
            terminate_mock.assert_called_once()

    def test_get_results(self):
        with patch.object(OutputConverter, "convert") as convert_mock, \
             patch.object(LocalApi, "get_experiment_rounds") as get_rounds_mock:

            get_rounds_mock.return_value = 3

            self.local_api.get_results(path=Path('dummy'), all_results=True)
            get_rounds_mock.assert_called_once_with(Path('dummy'))
            self.assertEqual(convert_mock.call_count, 3)

            get_rounds_mock.reset_mock()
            get_rounds_mock.return_value = 4
            convert_mock.reset_mock()

            self.local_api.get_results(path=Path('dummy'), all_results=False)
            get_rounds_mock.assert_called_once_with(Path('dummy'))
            convert_mock.assert_called_once_with(4, [])

