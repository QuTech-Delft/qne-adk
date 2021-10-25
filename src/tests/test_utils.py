from pathlib import Path
from unittest.mock import call, patch, mock_open
import unittest

from cli.exceptions import MalformedJsonFile, InvalidPathName
from cli.utils import copy_files, get_dummy_application, get_py_dummy, read_json_file, reorder_data, write_json_file, \
    write_file, validate_path_name


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.path = Path("dummy")
        self.roles = ["role1", "role2"]
        self.invalid_name = "invalid/name"

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

    def test_get_dummy_application(self):
        get_dummy_application(self.roles)

    def test_get_py_dummy(self):
        get_py_dummy()

    def test_validate_path_name(self):
        self.assertRaises(InvalidPathName, validate_path_name, "object", self.invalid_name)

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
