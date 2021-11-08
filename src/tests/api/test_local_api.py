import unittest
from pathlib import Path
from unittest.mock import call, patch, MagicMock

from cli.managers.roundset_manager import RoundSetManager
from cli.api.local_api import LocalApi
from cli.output_converter import OutputConverter
from cli.exceptions import ApplicationAlreadyExists, JsonFileNotFound, NoNetworkAvailable, PackageNotComplete


class ApplicationValidate(unittest.TestCase):

    def setUp(self) -> None:
        self.config_manager = MagicMock(config_dir=Path("path/to/application"))
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

        self.mock_app_config = {'application': [
            {
                "title": "Qubit state of Sender",
                "slug": "qubit_state_sender",
                "description": "description",
                "values": [
                    {
                        "name": "phi",
                        "default_value": 0.0,
                        "minimum_value": -1.0,
                        "maximum_value": 1.0,
                        "scale_value": "pi"
                    },
                    {
                        "name": "theta",
                        "default_value": 0.0,
                        "minimum_value": 0.0,
                        "maximum_value": 1.0,
                        "scale_value": 2.0
                    }
                ],
                "input_type": "qubit",
                "roles": [
                    "Sender"
                ]
            }
        ],
            'network': {}
        }

        self.channel_info_list = [{"slug": "c1-slug", "parameters": ["param-1", "param-2"]},
                             {"slug": "c2-slug", "parameters": ["param-1"]},
                             {"slug": "c3-slug", "parameters": ["param-2"]}]

        self.node_info_list = [{"slug": "n1-slug", "node_parameters": ["param-1", "param-2"], "number_of_qubits": 2,
                           "qubit_parameters": ["param-1", "param-2"]},
                          {"slug": "n2-slug", "node_parameters": ["param-2"], "number_of_qubits": 1,
                           "qubit_parameters": ["param-1"]},
                          {"slug": "n3-slug", "node_parameters": ["param-1"], "number_of_qubits": 1,
                           "qubit_parameters": ["param-2"]}]

        self.mock_network_data = {
          "networks": {
            "network1": {
                "name": "Network 1",
                "slug": "network1",
                "channels": [
                    "n1-n2",
                    "n2-n3"
                ]
            }
          }
        }
        self.mock_channel_data = {
          "channels": [
            {
              "slug": "n1-n2",
              "node1": "n1",
              "node2": "n2",
              "parameters": [
                    "param-1"
                ]
            },
           {
              "slug": "n2-n3",
              "node1": "n2",
              "node2": "n3",
              "parameters": [
                  "param-2"
              ]
           }
          ]
        }
        self.mock_node_data = {
          "nodes": [
            {
              "name": "N1",
              "slug": "n1",
              "coordinates": {
                "latitude": 52.3667,
                "longitude": 4.8945
              },
              "node_parameters": [
                "gate-fidelity"
              ],
              "number_of_qubits": 3,
              "qubit_parameters": [
                "relaxation-time",
                "dephasing-time"
              ]
            }
          ]
        }
        self.mock_template_data = {
          "templates": [
            {
              "title": "Parameter One",
              "slug": "param-1",
              "values": [
                {
                  "name": "fidelity",
                  "default_value": 1.0,
                  "minimum_value": 0.5,
                  "maximum_value": 1.0,
                  "unit": "unit-name",
                  "scale_value": 1.0
                }
              ],
              "input_type": "fidelity_slider"
            },
            {
              "title": "Parameter 2",
              "slug": "param-2",
              "values": [
                  {
                      "name": "t1",
                      "default_value": 0,
                      "minimum_value": 0,
                      "maximum_value": 1000,
                      "unit": "milliseconds",
                      "scale_value": 12.0
                  }
              ],
              "input_type": "time"
            }
          ]
        }

    def test_constructor(self):
        with patch("cli.api.local_api.utils.read_json_file") as read_json_file_mock:
            read_json_file_mock.side_effect = JsonFileNotFound("networks/networks.json")
            self.assertRaises(PackageNotComplete, LocalApi, self.config_manager)

    def test_create_application(self):
        with patch.object(self.config_manager, "application_exists") as application_exists_mock, \
             patch.object(LocalApi, "_LocalApi__create_application_structure") as structure_mock:

            application_exists_mock.return_value = False, self.path
            structure_mock.return_value = True
            self.local_api.create_application(self.application, self.roles, self.path)

            application_exists_mock.assert_called_once_with(self.application)
            structure_mock.assert_called_once_with(self.application, self.roles, self.path)

            # Raise ApplicationAlreadyExists when application is not unique
            application_exists_mock.return_value = True, None
            self.assertRaises(ApplicationAlreadyExists, self.local_api.create_application, self.application, self.roles,
                              self.path)

    def test__create_application_structure(self):
        with patch('cli.api.local_api.Path.mkdir') as mock_mkdir, \
             patch.object(LocalApi, "_get_network_nodes") as _get_nodes_mock, \
             patch("cli.api.local_api.utils.get_dummy_application") as get_dummy_application_mock, \
             patch("cli.api.local_api.shutil.rmtree") as rmtree_mock, \
             patch("cli.api.local_api.utils.write_json_file") as write_json_file_mock, \
             patch("cli.api.local_api.utils.write_file") as write_file_mock, \
             patch.object(self.config_manager, "application_exists", return_value=False) as application_exists_mock, \
             patch.object(self.config_manager, 'add_application') as config_manager_mock:

            _get_nodes_mock.return_value = {"dummy_network": ["network1", "network2", "network3"]}
            get_dummy_application_mock.return_value = {'application': [{'roles': ['dummy_role']}]}
            application_exists_mock.return_value = (False, self.path)
            self.local_api.create_application(self.application, self.roles, self.path)

            application_exists_mock.assert_called_once_with(self.application)
            config_manager_mock.assert_called_once_with(self.application, self.path)
            self.assertEqual(write_file_mock.call_count, 1 + len(self.roles))
            self.assertEqual(mock_mkdir.call_count, 2)
            write_json_file_mock.call_count = 3
            write_file_mock.call_count = 2
            _get_nodes_mock.assert_called_once()
            get_dummy_application_mock.assert_called_once()
            application_exists_mock.assert_called_once_with(self.application)
            config_manager_mock.assert_called_once_with(self.application, self.path)

            # Raise exception when no network available
            _get_nodes_mock.return_value = {}
            self.assertRaises(NoNetworkAvailable, self.local_api.create_application, self.application, self.roles,
                              self.path)
            rmtree_mock.assert_called_once()

    def test_is_application_unique(self):
        with patch.object(LocalApi, "_LocalApi__create_application_structure", return_value=True) as structure_mock, \
             patch.object(self.config_manager, "application_exists") as application_exists_mock:

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
             patch.object(self.config_manager, "application_exists") as application_exists_mock, \
             patch.object(LocalApi, "_LocalApi__is_config_valid") as is_config_valid_mock:

            # If application is not unique, is_config_valid() returns an error and warning
            application_exists_mock.return_value = True, None

            self.assertEqual(self.local_api.is_application_valid(application_name=self.application), self.error_dict)

            application_exists_mock.assert_called_once_with(self.application)
            is_structure_valid_mock.assert_called_once_with(self.application, self.error_dict)
            is_config_valid_mock.assert_called_once_with(self.application, self.error_dict)

            # If application is unique
            application_exists_mock.reset_mock()
            application_exists_mock.return_value = False, None
            self.assertEqual(self.local_api.is_application_valid(application_name=self.application),
                             {"error": [f"Application '{self.application}' does not exist"], "warning": [], "info": []})
            application_exists_mock.assert_called_once_with(self.application)

    def test__is_structure_valid(self):
        with patch.object(self.config_manager, "application_exists", return_value=(True, None)), \
             patch.object(LocalApi, "_LocalApi__is_config_valid", return_value=True), \
             patch.object(self.config_manager, "get_application_path") as get_application_path_mock, \
             patch("cli.api.local_api.validate_json_file") as validate_json_file_mock, \
             patch.object(LocalApi, "_LocalApi__get_role_file_names") as get_role_file_names_mock, \
             patch("cli.api.local_api.Path.is_dir", return_value=True) as is_dir_mock, \
             patch("cli.api.local_api.Path.is_file", return_value=True) as is_file_mock, \
             patch("cli.api.local_api.os.listdir") as listdir_mock:

            is_dir_mock.side_effect = [True, True, True, True]
            is_file_mock.side_effect = [True, True, True, True, True]
            get_application_path_mock.return_value = self.path
            listdir_mock.return_value = ["role1.py", "role2.py"]
            get_role_file_names_mock.return_value = [{"roles": ["role1", "role2"]}]
            validate_json_file_mock.return_value = (True, None)
            self.local_api.is_application_valid(application_name=self.application)
            is_dir_mock.call_count = 4
            is_file_mock.call_count = 5
            get_application_path_mock.assert_called_once()
            validate_json_file_mock.assert_called_once()
            listdir_mock.assert_called_once()

            # If the app_config_path, app_config_path / application.json does not exist and validate_json_file is False
            is_dir_mock.reset_mock()
            is_file_mock.reset_mock()
            get_application_path_mock.reset_mock()
            validate_json_file_mock.reset_mock()
            listdir_mock.reset_mock()
            validate_json_file_mock.reset_mock()
            is_dir_mock.side_effect = [False, True, True, True]
            is_file_mock.side_effect = [True, False, True, True, True]
            get_application_path_mock.return_value = self.path
            validate_json_file_mock.return_value = (False, None)
            self.local_api.is_application_valid(application_name=self.application)
            is_dir_mock.call_count = 3
            is_file_mock.call_count = 4
            get_application_path_mock.assert_called_once()
            validate_json_file_mock.assert_called_once()

    def test__is_config_valid(self):
        with patch.object(LocalApi, "_LocalApi__is_structure_valid") as is_structure_valid_mock,\
             patch.object(self.config_manager, "application_exists", return_value=(True, None)), \
             patch("cli.api.local_api.Path.is_file", return_value=True) as is_file_mock, \
             patch.object(self.config_manager, "get_application_path") as get_application_path_mock, \
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
        with patch.object(self.config_manager, "get_applications") as get_applications_mock:
            self.local_api.list_applications()
            get_applications_mock.assert_called_once()

    def test_experiments_create(self):
        with patch.object(LocalApi, "get_network_data") as get_network_data_mock, \
             patch.object(LocalApi, "create_asset_network") as create_network_asset_mock, \
             patch.object(LocalApi, "create_experiment") as create_exp_mock:

            get_network_data_mock.return_value = {'a': 'b'}
            create_network_asset_mock.return_value = {'c': 'd'}
            self.local_api.experiments_create(experiment_name='name', app_config={'foo': 'bar'},
                                              network_name='network_name', path=Path('dummy'),
                                              application_name='application')
            get_network_data_mock.assert_called_once_with(network_name='network_name')
            create_network_asset_mock.assert_called_once_with(network_data={'a': 'b'}, app_config={'foo': 'bar'})
            create_exp_mock.assert_called_once_with(experiment_name='name', app_config={'foo': 'bar'},
                                                    asset_network={'c': 'd'}, path=Path('dummy'),
                                                    application_name='application')

    def test_create_experiment(self):
        with patch("cli.api.local_api.utils.write_json_file") as write_mock, \
             patch('cli.api.local_api.Path.mkdir') as mkdir_mock, \
             patch.object(LocalApi, "_LocalApi__copy_input_files_from_application") as copy_files_mock:

            self.local_api.create_experiment(experiment_name='test', app_config=self.mock_app_config,
                                             asset_network={'a': 'b'}, path=Path('dummy'), application_name='app_name')

            self.assertEqual(mkdir_mock.call_count, 2)

            experiment_dir = Path('dummy') / 'test'
            input_dir = experiment_dir / 'input'
            copy_files_call = [call('app_name', input_dir)]

            copy_files_mock.assert_has_calls(copy_files_call)

            expected_asset_application = [{
                    "roles": ["Sender"],
                    "values": [{"name": "phi", "value": 0.0, "scale_value": "pi"},
                               {"name": "theta", "value": 0.0, "scale_value": 2.0}
                              ]
                }
            ]
            self.experiment_data_local['meta']['description'] = 'test: experiment description'
            self.experiment_data_local['asset'] = {'network': {'a': 'b'}, 'application': expected_asset_application}

            write_mock.assert_called_once_with(Path('dummy') / 'test' / 'experiment.json', self.experiment_data_local)

    def test_get_application_config(self):
        with patch.object(self.config_manager, "get_application") as get_application_mock, \
             patch("cli.api.local_api.utils.read_json_file") as read_mock:

            read_mock.side_effect = [[{'app': 'foo'}], {'network': 'bar'}]
            get_application_mock.return_value = {'path': 'some-path'}
            config = self.local_api.get_application_config('test')
            get_application_mock.assert_called_once_with('test')
            self.assertEqual(read_mock.call_count, 2)
            self.assertDictEqual(config, {'application': [{'app': 'foo'}], 'network': {'network': 'bar'}})

            get_application_mock.reset_mock()
            get_application_mock.return_value = {}
            config = self.local_api.get_application_config('test')
            self.assertIsNone(config)

    def test_validate_experiment(self):
        pass

    def test_run_experiment(self):
        with patch.object(RoundSetManager, "prepare_input") as prepare_input_mock, \
             patch.object(LocalApi, "_get_asset") as get_asset_mock, \
             patch.object(RoundSetManager, "process") as process_mock:

            self.local_api.run_experiment(Path('dummy'))
            get_asset_mock.assert_called_once()
            prepare_input_mock.assert_called_once()
            process_mock.assert_called_once()

    def test_get_results(self):
        with patch.object(OutputConverter, "convert") as convert_mock:
            self.local_api.get_results(path=Path('dummy'))
            convert_mock.assert_called_once_with(round_number=1)

    def test_is_network_available(self):
        with patch.object(LocalApi, "_get_network_slug") as get_network_slug_mock:
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
        with patch.object(LocalApi, "_get_network_nodes") as _get_nodes_mock, \
         patch.object(LocalApi, "_get_network_slug") as get_network_slug_mock, \
         patch.object(LocalApi, "_get_channels_for_network") as get_channels_for_network_mock, \
         patch.object(LocalApi, "_get_channel_info") as get_channel_info_mock, \
         patch.object(LocalApi, "_get_node_info") as get_node_info_mock, \
         patch.object(LocalApi, "_LocalApi__read_generic_data") as read_generic_mock:
            channel_info_list = [{"slug": "c1-slug"},{"slug": "c2-slug"},{"slug": "c3-slug"}]
            node_info_list = [{"slug": "n1-slug"}, {"slug": "n2-slug"}, {"slug": "n3-slug"}]

            _get_nodes_mock.return_value = {"network-slug-1": ["n1", "n2", "n3"]}
            get_network_slug_mock.return_value = 'network-slug-1'
            get_channels_for_network_mock.return_value = ['c1', 'c2', 'c3']
            get_channel_info_mock.side_effect = channel_info_list
            get_node_info_mock.side_effect = node_info_list

            # Initialize the data for networks, channels, nodes and templates
            read_generic_mock.side_effect = [self.mock_network_data, self.mock_channel_data,
                                             self.mock_node_data, self.mock_template_data]

            test_local_api = LocalApi(config_manager=self.config_manager)

            data = test_local_api.get_network_data('Network 1')
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
        # pylint: disable-msg=too-many-statements, too-many-locals
        with patch.object(LocalApi, "_LocalApi__read_generic_data") as read_generic_mock:

            mock_network_data = {
                        "name": 'Network 1',
                        "slug": 'network-slug-1',
                        "channels": self.channel_info_list,
                        "nodes": self.node_info_list,
            }
            mock_app_config = {'application': [{'app': 'foo'}],
                               'network': {'networks': ['network-slug-2', 'network-slug-1'],
                                           'roles': ['role1', 'role2']}
                               }
            # Initialize the data for networks, channels, nodes and templates
            read_generic_mock.side_effect = [self.mock_network_data, self.mock_channel_data,
                                             self.mock_node_data, self.mock_template_data]

            test_local_api = LocalApi(config_manager=self.config_manager)

            asset_network = test_local_api.create_asset_network(network_data=mock_network_data,
                                                                app_config=mock_app_config)

            # Check Roles data
            self.assertIn('roles', asset_network)
            self.assertIn('role1', asset_network['roles'])
            self.assertIn('role2', asset_network['roles'])

            # Check Channels data
            self.assertIn('channels', asset_network)
            self.assertEqual(len(asset_network["channels"]), 3)
            for channel in asset_network['channels']:
                self.assertIn('parameters', channel)
                self.assertNotIn('filled_parameters', channel)

            expected_param_1_dict = {'slug': 'param-1',
                                     'values': [{'name': 'fidelity', 'value': 1.0, 'scale_value': 1.0}]}
            expected_param_2_dict = {'slug': 'param-2',
                                     'values': [{'name': 't1', 'value': 0, 'scale_value': 12.0}]}

            c1_channel = asset_network['channels'][0]
            self.assertEqual((c1_channel["slug"]), "c1-slug")
            self.assertEqual(len(c1_channel["parameters"]), 2)
            self.assertDictEqual(c1_channel["parameters"][0], expected_param_1_dict)
            self.assertDictEqual(c1_channel["parameters"][1], expected_param_2_dict)

            c2_channel = asset_network['channels'][1]
            self.assertEqual((c2_channel["slug"]), "c2-slug")
            self.assertEqual(len(c2_channel["parameters"]), 1)
            self.assertDictEqual(c2_channel["parameters"][0], expected_param_1_dict)

            c3_channel = asset_network['channels'][2]
            self.assertEqual((c3_channel["slug"]), "c3-slug")
            self.assertEqual(len(c3_channel["parameters"]), 1)
            self.assertDictEqual(c3_channel["parameters"][0], expected_param_2_dict)

            # Check Nodes data
            self.assertIn('nodes', asset_network)
            self.assertEqual(len(asset_network["nodes"]), 3)
            for node in asset_network['nodes']:
                self.assertIn('node_parameters', node)
                self.assertIn('qubits', node)
                self.assertNotIn('number_of_qubits', node)
                self.assertNotIn('qubit_parameters', node)
                self.assertNotIn('filled_node_parameters', node)

            # Node 1 (n1-slug)
            n1_node = asset_network['nodes'][0]
            self.assertEqual((n1_node["slug"]), "n1-slug")
            self.assertEqual(len(n1_node["node_parameters"]), 2)
            self.assertDictEqual(n1_node["node_parameters"][0], expected_param_1_dict)
            self.assertDictEqual(n1_node["node_parameters"][1], expected_param_2_dict)

            self.assertEqual(len(n1_node["qubits"]), 2)

            self.assertEqual(n1_node["qubits"][0]['qubit_id'], 0)
            self.assertEqual(len(n1_node["qubits"][0]['qubit_parameters']), 2)
            self.assertDictEqual(n1_node["qubits"][0]['qubit_parameters'][0], expected_param_1_dict)
            self.assertDictEqual(n1_node["qubits"][0]['qubit_parameters'][1], expected_param_2_dict)

            self.assertEqual(n1_node["qubits"][1]['qubit_id'], 1)
            self.assertEqual(len(n1_node["qubits"][1]['qubit_parameters']), 2)
            self.assertDictEqual(n1_node["qubits"][1]['qubit_parameters'][0], expected_param_1_dict)
            self.assertDictEqual(n1_node["qubits"][1]['qubit_parameters'][1], expected_param_2_dict)

            # Node 2 (n2-slug)
            n2_node = asset_network['nodes'][1]
            self.assertEqual((n2_node["slug"]), "n2-slug")
            self.assertEqual(len(n2_node["node_parameters"]), 1)
            self.assertDictEqual(n2_node["node_parameters"][0], expected_param_2_dict)

            self.assertEqual(len(n2_node["qubits"]), 1)

            self.assertEqual(n2_node["qubits"][0]['qubit_id'], 0)
            self.assertEqual(len(n2_node["qubits"][0]['qubit_parameters']), 1)
            self.assertDictEqual(n2_node["qubits"][0]['qubit_parameters'][0], expected_param_1_dict)

            # Node 3 (n3-slug)
            n3_node = asset_network['nodes'][2]
            self.assertEqual((n3_node["slug"]), "n3-slug")
            self.assertEqual(len(n3_node["node_parameters"]), 1)
            self.assertDictEqual(n3_node["node_parameters"][0], expected_param_1_dict)

            self.assertEqual(len(n3_node["qubits"]), 1)

            self.assertEqual(n3_node["qubits"][0]['qubit_id'], 0)
            self.assertEqual(len(n3_node["qubits"][0]['qubit_parameters']), 1)
            self.assertDictEqual(n3_node["qubits"][0]['qubit_parameters'][0], expected_param_2_dict)

    def test_get_network_nodes(self):
        with patch.object(LocalApi, "_LocalApi__read_generic_data") as read_generic_mock:
            read_generic_mock.side_effect = \
                [
                    {
                        "networks": {
                            "randstad": {
                                "name": "Randstad",
                                "slug": "randstad",
                                "channels": [
                                    "amsterdam-leiden",
                                    "leiden-the-hague",
                                    "delft-the-hague",
                                    "delft-rotterdam"
                                ]
                            }
                        }
                    },
                    {
                        "channels": [
                            {
                                "slug": "amsterdam-leiden",
                                "node1": "amsterdam",
                                "node2": "leiden",
                                "parameters": [
                                    "elementary-link-fidelity"
                                ]
                            },
                            {
                                "slug": "leiden-the-hague",
                                "node1": "leiden",
                                "node2": "the-hague",
                                "parameters": [
                                    "elementary-link-fidelity"
                                ]
                            }
                        ]
                    },
                    {},
                    {}
                ]

            test_local_api = LocalApi(config_manager=self.config_manager)
            data = test_local_api._get_network_nodes()  # pylint: disable=W0212
            self.assertEqual(data, {'randstad': ['amsterdam', 'leiden', 'the-hague']})

            # Check when only two nodes are available
            read_generic_mock.reset_mock()
            read_generic_mock.side_effect = \
                [
                    {
                        "networks": {
                            "randstad": {
                                "name": "Randstad",
                                "slug": "randstad",
                                "channels": [
                                    "amsterdam-leiden",
                                    "leiden-the-hague",
                                    "delft-the-hague",
                                    "delft-rotterdam"
                                ]
                            }
                        }
                    },
                    {
                        "channels": [
                            {
                                "slug": "amsterdam-leiden",
                                "node1": "amsterdam",
                                "node2": "leiden",
                                "parameters": [
                                    "elementary-link-fidelity"
                                ]
                            },
                        ]
                    },
                    {},
                    {}
                ]

            test_local_api = LocalApi(config_manager=self.config_manager)
            data = test_local_api._get_network_nodes()  # pylint: disable=W0212
            self.assertEqual(data, {'randstad': ['amsterdam', 'leiden']})

    def test_network_helpers(self):
        # pylint: disable=W0212
        with patch.object(LocalApi, "_LocalApi__read_generic_data") as read_generic_mock:
            # Initialize the data for networks, channels, nodes and templates
            read_generic_mock.side_effect = [self.mock_network_data, self.mock_channel_data,
                                             self.mock_node_data, self.mock_template_data]

            test_local_api = LocalApi(config_manager=self.config_manager)

            network_info = test_local_api._get_network_info(identifier_value="network1")
            self.assertEqual(network_info['slug'], 'network1')

            network_info = test_local_api._get_network_info(identifier_value="NETWORK1")
            self.assertIsNotNone(network_info)

            network_info = test_local_api._get_network_info(identifier_value="NETWORK 1", identifier_type="name")
            self.assertIsNotNone(network_info)

            self.assertEqual(test_local_api._get_network_slug(network_name='NETWORK 1'), 'network1')
            self.assertIsNone(test_local_api._get_network_slug(network_name='NETWORK 42'))

            self.assertEqual(test_local_api._get_network_name(network_slug='network1'), 'Network 1')
            self.assertIsNone(test_local_api._get_network_name(network_slug='network42'))

            self.assertEqual(test_local_api._get_qne_network_name(network_name='NETWORK 1'), 'Network 1')
            self.assertEqual(test_local_api._get_qne_network_name(network_name='Network 1'), 'Network 1')
            self.assertIsNone(test_local_api._get_qne_network_name(network_name='NETWORK 42'))

            expected_channel_list = ["n1-n2", "n2-n3"]
            self.assertEqual(test_local_api._get_channels_for_network(network_slug='network1'), expected_channel_list)
            self.assertIsNone(test_local_api._get_channels_for_network(network_slug='network-unknown'))

            expected_channel_info = {
              "slug": "n1-n2",
              "node1": "n1",
              "node2": "n2",
              "parameters": [
                    "param-1"
                ]
            }
            self.assertEqual(test_local_api._get_channel_info(channel_slug='n1-n2'), expected_channel_info)
            self.assertIsNone(test_local_api._get_channel_info(channel_slug='channel-unknown'))

            expected_node_info = {
              "name": "N1",
              "slug": "n1",
              "coordinates": {
                "latitude": 52.3667,
                "longitude": 4.8945
              },
              "node_parameters": [
                "gate-fidelity"
              ],
              "number_of_qubits": 3,
              "qubit_parameters": [
                "relaxation-time",
                "dephasing-time"
              ]
            }
            self.assertEqual(test_local_api._get_node_info(node_slug='n1'), expected_node_info)
            self.assertIsNone(test_local_api._get_node_info(node_slug='node-unknown'))

            expected_template_info = {
                "param-1": {
                      "title": "Parameter One",
                      "slug": "param-1",
                      "values": [
                        {
                          "name": "fidelity",
                          "default_value": 1.0,
                          "minimum_value": 0.5,
                          "maximum_value": 1.0,
                          "unit": "unit-name",
                          "scale_value": 1.0
                        }
                      ],
                      "input_type": "fidelity_slider"
                    },
                "param-2": {
                      "title": "Parameter 2",
                      "slug": "param-2",
                      "values": [
                          {
                              "name": "t1",
                              "default_value": 0,
                              "minimum_value": 0,
                              "maximum_value": 1000,
                              "unit": "milliseconds",
                              "scale_value": 12.0
                          }
                      ],
                      "input_type": "time"
                    }
            }
            self.assertEqual(test_local_api._get_templates(), expected_template_info)
