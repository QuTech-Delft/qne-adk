import unittest
from pathlib import Path
from unittest.mock import call, patch

from cli.managers.config_manager import ConfigManager
from cli.managers.roundset_manager import RoundSetManager
from cli.api.local_api import LocalApi
from cli.output_converter import OutputConverter
from cli.exceptions import ApplicationAlreadyExists, NoNetworkAvailable


class ApplicationValidate(unittest.TestCase):

    def setUp(self) -> None:
        self.config_manager = ConfigManager(config_dir=Path("path/to/application"))
        self.local_api = LocalApi(config_manager=self.config_manager)

        self.application = "test_application"
        self.roles = ["Testrole1", "Testrole2"]
        self.path = Path("path/to/application")
        self.config_files = ["application.json", "network.json", "result.json"]
        self.experiment_meta_local = {
            "backend": {
                "location": "local",
                "type": "local_netsquid"
             },
            "number_of_rounds": 1,
            "description": ""
        }
        self.error_dict = {"error": [], "warning": [], "info": []}

        self.experiment_data_local = {'meta': self.experiment_meta_local, 'asset': {}}

    def test_create_application(self):
        with patch.object(LocalApi, "_LocalApi__is_application_unique") as is_application_unique_mock, \
             patch.object(ConfigManager, "check_config_exists") as check_config_exists_mock, \
             patch.object(ConfigManager, "create_config") as create_config_mock, \
             patch.object(LocalApi, "_LocalApi__create_application_structure") as structure_mock:

            check_config_exists_mock.return_value = True
            is_application_unique_mock.return_value = True, self.path
            structure_mock.return_value = True
            self.local_api.create_application(self.application, self.roles, self.path)

            is_application_unique_mock.assert_called_once_with(self.application)
            structure_mock.assert_called_once_with(self.application, self.roles, self.path)

            # create_config should be called when check_config_exists returns false
            check_config_exists_mock.reset_mock()
            check_config_exists_mock.return_value = False
            self.local_api.create_application(self.application, self.roles, self.path)
            check_config_exists_mock.assert_called_once()
            create_config_mock.assert_called_once()

            # Raise ApplicationAlreadyExists when application is not unique
            is_application_unique_mock.return_value = False, None
            self.assertRaises(ApplicationAlreadyExists, self.local_api.create_application, self.application, self.roles,
                              self.path)

    def test__create_application_structure(self):
        with patch('cli.api.local_api.Path.mkdir') as mock_mkdir, \
             patch("cli.api.local_api.utils.get_network_nodes") as check_network_nodes_mock, \
             patch("cli.api.local_api.utils.get_dummy_application") as get_dummy_application_mock, \
             patch("cli.api.local_api.shutil.rmtree") as rmtree_mock, \
             patch("cli.api.local_api.utils.write_json_file") as write_json_file_mock, \
             patch("cli.api.local_api.utils.write_file") as write_file_mock, \
             patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=True) as application_unique_mock, \
             patch.object(ConfigManager, "check_config_exists") as check_config_exists_mock, \
             patch.object(ConfigManager, 'add_application') as config_manager_mock:

            check_config_exists_mock.return_value = True
            check_network_nodes_mock.return_value = {"dummy_network": ["network1", "network2", "network3"]}
            get_dummy_application_mock.return_value = {'application': [{'roles': ['dummy_role']}]}
            application_unique_mock.return_value = True, self.path
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

            # Raise exception when no network available
            check_network_nodes_mock.return_value = {}
            self.assertRaises(NoNetworkAvailable, self.local_api.create_application, self.application, self.roles,
                              self.path)
            rmtree_mock.assert_called_once()

    def test_is_application_unique(self):
        with patch.object(LocalApi, "_LocalApi__create_application_structure", return_value=True) as structure_mock, \
             patch.object(ConfigManager, "check_config_exists") as check_config_exists_mock, \
             patch.object(ConfigManager, "application_exists") as application_exists_mock:

            check_config_exists_mock.return_value = True
            application_exists_mock.return_value = True, self.path
            self.assertRaises(ApplicationAlreadyExists, self.local_api.create_application, self.application, self.roles,
                              self.path)
            application_exists_mock.assert_called_once_with(self.application)

            structure_mock.reset_mock()
            application_exists_mock.reset_mock()
            application_exists_mock.return_value = False, None
            self.local_api.create_application(self.application, self.roles, self.path)
            structure_mock.assert_called_once_with(self.application, self.roles, self.path)
            application_exists_mock.assert_called_once_with(self.application)

    def test_is_application_valid(self):
        with patch.object(LocalApi, "_LocalApi__is_structure_valid") as is_structure_valid_mock, \
             patch.object(LocalApi, "_LocalApi__is_application_unique") as is_application_unique_mock, \
             patch.object(LocalApi, "_LocalApi__is_config_valid") as is_config_valid_mock:

            # If application is not unique, is_config_valid() returns an error and warning
            is_application_unique_mock.return_value = False, None

            self.assertEqual(self.local_api.is_application_valid(application_name=self.application), self.error_dict)

            is_application_unique_mock.assert_called_once_with(self.application)
            is_structure_valid_mock.assert_called_once_with(self.application, self.error_dict)
            is_config_valid_mock.assert_called_once_with(self.application, self.error_dict)

            # If application is unique
            is_application_unique_mock.reset_mock()
            is_application_unique_mock.return_value = True, None
            self.assertEqual(self.local_api.is_application_valid(application_name=self.application),
                             {"error": ["Application does not exist"], "warning": [], "info": []})
            is_application_unique_mock.assert_called_once_with(self.application)

    def test__is_structure_valid(self):
        with patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=(False, None)), \
             patch.object(LocalApi, "_LocalApi__is_config_valid", return_value=True), \
             patch.object(ConfigManager, "get_application_path") as get_application_path_mock, \
             patch("cli.api.local_api.validate_json_file") as validate_json_file_mock, \
             patch("cli.api.local_api.read_json_file") as read_json_file_mock, \
             patch("cli.api.local_api.os.path.exists", return_value=True) as exists_mock, \
             patch("cli.api.local_api.os.path.isfile", return_value=True) as isfile_mock, \
             patch("cli.api.local_api.os.listdir") as listdir_mock:

            exists_mock.side_effect = [True, True, True, True]
            isfile_mock.side_effect = [True, True, True, True, True]
            get_application_path_mock.return_value = self.path
            listdir_mock.return_value = ["role1.py", "role2.py"]
            read_json_file_mock.return_value = [{"roles": ["role1", "role2"]}]
            validate_json_file_mock.return_value = (True, None)
            self.local_api.is_application_valid(application_name=self.application)
            exists_mock.call_count = 4
            isfile_mock.call_count = 4
            get_application_path_mock.assert_called_once()
            validate_json_file_mock.assert_called_once()
            listdir_mock.assert_called_once()

            # If the app_config_path, app_config_path / application.json does not exist and validate_json_file is False
            exists_mock.reset_mock()
            isfile_mock.reset_mock()
            get_application_path_mock.reset_mock()
            validate_json_file_mock.reset_mock()
            listdir_mock.reset_mock()
            validate_json_file_mock.reset_mock()
            exists_mock.side_effect = [False, True, True, True]
            isfile_mock.side_effect = [True, False, True, True, True]
            get_application_path_mock.return_value = self.path
            validate_json_file_mock.return_value = (False, None)
            self.local_api.is_application_valid(application_name=self.application)
            exists_mock.call_count = 3
            isfile_mock.call_count = 2
            get_application_path_mock.assert_called_once()
            validate_json_file_mock.assert_called_once()

    def test__is_config_valid(self):
        with patch.object(LocalApi, "_LocalApi__is_structure_valid") as is_structure_valid_mock,\
             patch.object(LocalApi, "_LocalApi__is_application_unique", return_value=(False, None)), \
             patch("cli.api.local_api.Path.is_file", return_value=True) as is_file_mock, \
             patch.object(ConfigManager, "get_application_path") as get_application_path_mock, \
             patch("cli.api.local_api.validate_json_file") as validate_json_file_mock, \
             patch("cli.api.local_api.validate_json_schema") as validate_json_schema_mock:

            # If is_file() is true and validate_json_file is true
            is_structure_valid_mock.return_value = self.error_dict
            validate_json_file_mock.return_value = True, None
            validate_json_schema_mock.return_value = True, None
            get_application_path_mock.return_value = self.path
            self.local_api.is_application_valid(application_name=self.application)
            get_application_path_mock.assert_called_once()
            is_file_mock.call_count = 3
            validate_json_file_mock.call_count = 3
            validate_json_schema_mock.call_count = 3

            # If validate_json_file is false
            is_file_mock.reset_mock()
            validate_json_file_mock.reset_mock()
            validate_json_schema_mock.reset_mock()
            get_application_path_mock.reset_mock()
            get_application_path_mock.return_value = self.path
            validate_json_file_mock.return_value = False
            self.local_api.is_application_valid(application_name=self.application)
            get_application_path_mock.assert_called_once()
            is_file_mock.call_count = 3
            validate_json_file_mock.call_count = 3

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
            create_exp_mock.assert_called_once_with(name='name', app_config={'foo': 'bar'}, asset_network={'c': 'd'},
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
            copy_input_mock.assert_called_once_with('app_name', Path('dummy') / 'test' / 'input')
            create_app_asset_mock.assert_called_once_with({'foo': 'bar'})

            self.experiment_data_local['meta']['description'] = 'test: experiment description'
            self.experiment_data_local['asset'] = {'network': {'a': 'b'}, 'application': [{'x': 2}]}

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
            validate_asset_mock.return_value = True, 'ok'
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

    def test_is_network_available(self):
        with patch("cli.api.local_api.get_network_slug") as get_network_slug_mock:
            get_network_slug_mock.return_value = 'network-slug-1'
            mock_app_config = {'application': [{'app': 'foo'}],
                               'network': {'networks': ['network-slug-2', 'network-slug-1']}}
            network_available = self.local_api.is_network_available('network name', mock_app_config)

            get_network_slug_mock.assert_called_once_with('network name')
            self.assertTrue(network_available)

            get_network_slug_mock.reset_mock()
            get_network_slug_mock.return_value = 'network-slug-unknown'
            network_available = self.local_api.is_network_available('network name 1', mock_app_config)

            get_network_slug_mock.assert_called_once_with('network name 1')
            self.assertFalse(network_available)

    def test_get_network_data(self):
        with patch("cli.api.local_api.get_network_nodes") as get_network_nodes_mock, \
         patch("cli.api.local_api.get_network_slug") as get_network_slug_mock, \
         patch("cli.api.local_api.get_channels_for_network") as get_channels_for_network_mock, \
         patch("cli.api.local_api.get_channel_info") as get_channel_info_mock, \
         patch("cli.api.local_api.get_node_info") as get_node_info_mock:
            channel_info_list = [{"slug": "c1-slug"},{"slug": "c2-slug"},{"slug": "c3-slug"}]
            node_info_list = [{"slug": "n1-slug"}, {"slug": "n2-slug"}, {"slug": "n3-slug"}]

            get_network_nodes_mock.return_value = {"network-slug-1": ["n1", "n2", "n3"]}
            get_network_slug_mock.return_value = 'network-slug-1'
            get_channels_for_network_mock.return_value = ['c1', 'c2', 'c3']
            get_channel_info_mock.side_effect = channel_info_list
            get_node_info_mock.side_effect = node_info_list

            data = self.local_api.get_network_data('Network 1')
            get_network_slug_mock.assert_called_once_with('Network 1')
            get_channels_for_network_mock.assert_called_once_with(network_slug='network-slug-1')
            get_channel_info_mock.assert_has_calls([call(channel_slug='c1'), call(channel_slug='c2'),
                                                    call(channel_slug='c3')])
            get_node_info_mock.assert_has_calls([call(node_slug='n1'), call(node_slug='n2'), call(node_slug='n3')])

            self.assertEqual(data['name'], 'Network 1')
            self.assertEqual(data['slug'], 'network-slug-1')
            self.assertEqual(data['channels'], channel_info_list)
            self.assertEqual(data['nodes'], node_info_list)

    def test_create_asset_network(self):
        with patch("cli.api.local_api.get_templates") as get_templates_mock, \
         patch.object(LocalApi, "_LocalApi__get_filled_template_parameter") as get_filled_parameter_mock:
            channel_info_list = [{"slug": "c1-slug", "parameters": ["c-param-1", "c-param-4"]},
                                 {"slug": "c2-slug", "parameters": ["c-param-3"]},
                                 {"slug": "c3-slug", "parameters": ["c-param-2"]}]
            node_info_list = [{"slug": "n1-slug", "node_parameters": ["n-param-1", "n-param-4"], "number_of_qubits": 2,
                                "qubit_parameters": ["q-param-1","q-param-2"]},
                              {"slug": "n2-slug", "node_parameters": ["n-param-3"], "number_of_qubits": 1,
                                "qubit_parameters": ["q-param-3"]},
                              {"slug": "n3-slug", "node_parameters": ["n-param-2"], "number_of_qubits": 1,
                                "qubit_parameters": ["q-param-4"]}]
            mock_network_data = {
                        "name": 'Network 1',
                        "slug": 'network-slug-1',
                        "channels": channel_info_list,
                        "nodes": node_info_list,
            }
            mock_app_config = {'application': [{'app': 'foo'}],
                               'network': {'networks': ['network-slug-2', 'network-slug-1'],
                                           'roles': ['role1', 'role2']}
                               }
            get_templates_return_value = {}
            get_templates_mock.return_value = get_templates_return_value
            filled_parameter_item = {
                "slug": 'param-name',
                "values": []
            }
            get_filled_parameter_mock.return_value = filled_parameter_item

            asset_network = self.local_api.create_asset_network(network_data=mock_network_data,
                                                                app_config=mock_app_config)

            # Check Roles data
            self.assertIn('roles', asset_network)
            self.assertIn('role1', asset_network['roles'])
            self.assertIn('role2', asset_network['roles'])

            # Check calls to get_filled_parameter_mock
            channel_calls_for_filled_parameter_mock = [call(param='c-param-1', templates=get_templates_return_value),
                                               call(param='c-param-4', templates=get_templates_return_value),
                                               call(param='c-param-3', templates=get_templates_return_value),
                                               call(param='c-param-2', templates=get_templates_return_value),]
            node_calls_for_filled_parameter_mock = [call(param='n-param-1', templates=get_templates_return_value),
                                               call(param='n-param-4', templates=get_templates_return_value),
                                               call(param='q-param-1', templates=get_templates_return_value),
                                               call(param='q-param-2', templates=get_templates_return_value),
                                               call(param='q-param-1', templates=get_templates_return_value),
                                               call(param='q-param-2', templates=get_templates_return_value),
                                               call(param='n-param-3', templates=get_templates_return_value),
                                               call(param='q-param-3', templates=get_templates_return_value),
                                               call(param='n-param-2', templates=get_templates_return_value),
                                               call(param='q-param-4', templates=get_templates_return_value),]
            get_filled_parameter_mock.assert_has_calls(channel_calls_for_filled_parameter_mock +
                                                       node_calls_for_filled_parameter_mock)

            # Check Channels data
            self.assertIn('channels', asset_network)
            for channel in asset_network['channels']:
                self.assertIn('parameters', channel)
                self.assertNotIn('filled_parameters', channel)

            # Check Nodes data
            self.assertIn('nodes', asset_network)
            for node in asset_network['nodes']:
                self.assertIn('node_parameters', node)
                self.assertIn('qubits', node)
                self.assertNotIn('number_of_qubits', node)
                self.assertNotIn('qubit_parameters', node)
                self.assertNotIn('filled_node_parameters', node)
