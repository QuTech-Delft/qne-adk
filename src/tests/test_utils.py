from pathlib import Path
from unittest.mock import patch, mock_open
import unittest

from cli.utils import read_json_file, write_json_file, reorder_data, get_network_nodes, get_dummy_application, \
                      get_py_dummy, write_file
from cli.exceptions import MalformedJsonFile


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.path = Path("dummy")
        self.roles = ["role1", "role2"]

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
