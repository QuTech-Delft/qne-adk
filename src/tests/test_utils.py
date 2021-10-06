from pathlib import Path
from unittest.mock import call, patch, mock_open
import unittest

from cli.exceptions import MalformedJsonFile, InvalidPathName
from cli.settings import BASE_DIR
from cli.utils import copy_files, get_network_nodes, get_dummy_application, \
                      get_py_dummy, get_all_networks_data, get_network_slug, \
                      get_network_name, get_channel_info, get_channels_for_network, get_node_info, get_templates, \
                      read_json_file, reorder_data, write_json_file, write_file, validate_path_name


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.path = Path("dummy")
        self.roles = ["role1", "role2"]
        self.invalid_name = "invalid/name"
        self.network_data_1 = {
                  "networks": {
                    "network-slug-1": {
                      "name": "network name",
                      "slug": "network-slug-1",
                      "channels": [
                        "n1-n2",
                        "n3-n2",
                      ]
                    },
                    "network-slug-2": {
                      "name": "network 2",
                      "slug": "network-slug-2",
                      "channels": [
                          "n4-n3"
                      ]
                    }
                  }
                }
        self.network_data_2 = {
                "networks": {
                    "network-slug-1": {
                        "name": "network 1",
                        "slug": "network-slug-1",
                        "channels": [
                            "n1-n2"
                        ]
                    },
                    "network-slug-2": {
                        "name": "network 2",
                        "slug": "network-slug-2",
                        "channels": [
                            "n4-n3"
                        ]
                    }
                }
            }
        self.channel_1 = {
              "slug": "channel-1",
              "node1": "n1",
              "node2": "n2",
              "parameters": [
                "param-1"
              ]
            }
        self.channel_2 = {
            "slug": "channel-2",
            "node1": "n3",
            "node2": "n4",
            "parameters": [
                "param-1",
                "param-2"
            ]
        }
        self.node_1 = {
            "name": "Node 1",
            "slug": "node-1",
            "coordinates": {
                "latitude": 52.3667,
                "longitude": 4.8945
            },
            "node_parameters": [
                "param-1"
            ],
            "number_of_qubits": 3,
            "qubit_parameters": [
                "param-2",
                "param-3"
            ]
        }
        self.node_2 = {
            "name": "Node 2",
            "slug": "node-2",
            "coordinates": {
                "latitude": 52.3667,
                "longitude": 4.8945
            },
            "node_parameters": [
                "param-3"
            ],
            "number_of_qubits": 2,
            "qubit_parameters": [
                "param-1",
                "param-3"
            ]
        }
        self.template_1 = {
          "title": "Parameter 1",
          "slug": "param-1",
          "values": [
            {
              "name": "Parameter 1",
              "default_value": 1.0,
              "minimum_value": 0.5,
              "maximum_value": 1.0,
              "unit": "",
              "scale_value": 1.0
            }
          ],
          "input_type": "test_type"
        }
        self.template_2 = {
          "title": "Parameter 2",
          "slug": "param-2",
          "values": [
            {
              "name": "Parameter 2",
              "default_value": 1.0,
              "minimum_value": 0.5,
              "maximum_value": 1.0,
              "unit": "",
              "scale_value": 1.0
            }
          ],
          "input_type": "test_type"
        }

    def test_write_json_file(self):
        with patch("cli.utils.open") as open_mock, \
             patch("cli.utils.json.dump") as json_dump_mock:

            write_json_file(self.path, {})
            open_mock.assert_called_once()
            json_dump_mock.assert_called_once()

    def test_write_file(self):
        with patch("cli.utils.open") as open_mock:

            write_file(self.path, {})
            open_mock.assert_called_once()

    def test_read_json_file_valid(self):
        dummy_apps_config = "{" \
                                "\"app_1\" : {\"path\": \"/some/path/\"," \
                                              "\"application_id\": 1}," \
                                "\"app_2\" : {\"path\": \"/some/path/\"," \
                                              "\"application_id\": 2}" \
                            "}"

        with patch('cli.utils.open', mock_open(read_data=dummy_apps_config)):
            data = read_json_file(Path('dummy'))
            self.assertEqual(len(data), 2)
            self.assertIn('app_1', data)
            self.assertIn('app_2', data)

    def test_read_json_file_invalid(self):
        malformed_apps_config = "{" \
                            "\"app_1\"  {\"path\" \"/some/path/\"," \
                            "\"application_id\" 1}," \
                            "\"app_2\"  {\"path\" \"/some/path/\"," \
                            "\"application_id\" 2}" \
                            "}"

        with patch('cli.utils.open', mock_open(read_data=malformed_apps_config)):
            self.assertRaises(MalformedJsonFile, read_json_file, Path('dummy'))

    def test_reorder_data(self):
        dict_1 = {'k1': 1, "k3": 3, "k2": 2}
        dict_2 = {'k1': 2, "k2": 4, "k3": 6}
        dict_3 = {'k2': 6, "k3": 9, "k1": 3}
        data_list = [dict_1, dict_2, dict_3]
        desired_order = ["k3", "k2", "k1"]

        reordered_data = reorder_data(data_list, desired_order)

        for item in reordered_data:
            key_list = list(item)
            for i, key in enumerate(desired_order):
                self.assertIn(key, item)
                self.assertEqual(key_list[i], key)

    def test_get_network_nodes(self):
        with patch("cli.utils.Path.cwd") as cwd_mock, \
             patch("cli.utils.open") as open_mock, \
             patch("cli.utils.json.load") as json_load_mock:

            json_load_mock.side_effect = \
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
                    }
                ]

            self.assertEqual(get_network_nodes(), {'randstad': ['amsterdam', 'leiden', 'the-hague']})
            cwd_mock.call_count = 2
            open_mock.call_count = 2
            json_load_mock.call_count = 2

            # Check when only two nodes are available
            json_load_mock.side_effect = \
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
                    }
                ]

            self.assertEqual(get_network_nodes(), {'randstad': ['amsterdam', 'leiden']})
            cwd_mock.call_count = 2
            open_mock.call_count = 2
            json_load_mock.call_count = 2

    def test_get_dummy_application(self):
        get_dummy_application(self.roles)

    def test_get_py_dummy(self):
        get_py_dummy()

    def test_validate_path_name(self):
        self.assertRaises(InvalidPathName, validate_path_name, "object", self.invalid_name)

    def test_get_all_networks_data(self):
        with patch("cli.utils.read_json_file") as read_json_mock:
            read_json_mock.return_value = {'foo': {'bar': {}}}
            data = get_all_networks_data()
            read_json_mock.assert_called_once_with(Path(BASE_DIR) / "networks/networks.json")
            self.assertDictEqual(data, {'foo': {'bar': {}}})

    def test_get_network_slug(self):
        with patch("cli.utils.get_all_networks_data") as get_networks_mock:
            get_networks_mock.return_value = self.network_data_1
            slug = get_network_slug('network name')
            self.assertEqual(slug, 'network-slug-1')

            slug = get_network_slug('non existent network name')
            self.assertIsNone(slug)

    def test_get_network_name(self):
        with patch("cli.utils.get_all_networks_data") as get_networks_mock:
            get_networks_mock.return_value = self.network_data_1
            name = get_network_name('network-slug-2')
            self.assertEqual(name, 'network 2')

            name = get_network_name('non-existent-network-slug')
            self.assertIsNone(name)

    def test_get_channels_for_network(self):
        with patch("cli.utils.get_all_networks_data") as get_networks_mock:
            get_networks_mock.return_value = self.network_data_1
            channels = get_channels_for_network('network-slug-2')
            self.assertListEqual(channels, ["n4-n3"])

            channels = get_channels_for_network('non-existent-network-slug')
            self.assertIsNone(channels)

    def test_get_channel_info(self):
        with patch("cli.utils.read_json_file") as read_json_mock:
            read_json_mock.return_value = {'channels': [self.channel_1, self.channel_2]}
            data = get_channel_info("channel-1")
            read_json_mock.assert_called_once_with(Path(BASE_DIR) / "networks/channels.json")
            self.assertDictEqual(data, self.channel_1)

            read_json_mock.reset_mock()
            read_json_mock.return_value = {'channels': [self.channel_1, self.channel_2]}
            data = get_channel_info("channel-non-existing")
            read_json_mock.assert_called_once_with(Path(BASE_DIR) / "networks/channels.json")
            self.assertIsNone(data)

    def test_get_node_info(self):
        with patch("cli.utils.read_json_file") as read_json_mock:
            read_json_mock.return_value = {'nodes': [self.node_1, self.node_2]}
            data = get_node_info("node-1")
            read_json_mock.assert_called_once_with(Path(BASE_DIR) / "networks/nodes.json")
            self.assertDictEqual(data, self.node_1)

            read_json_mock.reset_mock()
            read_json_mock.return_value = {'nodes': [self.node_1, self.node_2]}
            data = get_node_info("node-non-existing")
            read_json_mock.assert_called_once_with(Path(BASE_DIR) / "networks/nodes.json")
            self.assertIsNone(data)

    def test_get_templates(self):
        with patch("cli.utils.read_json_file") as read_json_mock:
            read_json_mock.return_value = {'templates': [self.template_1, self.template_2]}
            data = get_templates()
            read_json_mock.assert_called_once_with(Path(BASE_DIR) / "networks/templates.json")
            self.assertDictEqual(data, {"param-1": self.template_1, "param-2": self.template_2})

    def test_copy_files(self):
        with patch("cli.utils.os.path.isfile") as isfile_mock, \
             patch("cli.utils.os.listdir") as listdir_mock, \
             patch("cli.utils.shutil.copy") as copy_mock, \
             patch("cli.utils.os.path.join") as join_mock:

            isfile_mock.return_value = True
            listdir_mock.return_value = ['file1', 'file2']
            join_mock.side_effect = ['file1_path', 'file2_path']

            copy_files("source", "dest")

            join_calls = [call("source", 'file1'), call("source", 'file2')]
            join_mock.assert_has_calls(join_calls)
            copy_calls = [call("file1_path", 'dest'), call("file2_path", 'dest')]
            copy_mock.assert_has_calls(copy_calls)
