import os
from pathlib import Path
from unittest.mock import call, patch, mock_open
import unittest

from adk.exceptions import InvalidPathName, JsonFileNotFound, MalformedJsonFile
from adk.utils import check_python_syntax, copy_files, move_files, get_dummy_application, get_function_arguments, \
    get_function_return_variables, get_py_dummy, read_json_file, reorder_data, write_json_file, write_file, \
    validate_path_name, get_default_manifest


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.path = Path("dummy")
        self.roles = ["role1", "role2"]
        self.invalid_name = "invalid/name"

    def test_write_json_file(self):
        with patch("adk.utils.open") as open_mock, \
             patch("adk.utils.json.dump") as json_dump_mock:

            write_json_file(self.path, {})
            open_mock.assert_called_once()
            json_dump_mock.assert_called_once()

    def test_write_file(self):
        with patch("adk.utils.open") as open_mock:

            write_file(self.path, {})
            open_mock.assert_called_once()

    def test_read_json_file_valid(self):
        dummy_apps_config = "{" \
                                "\"app_1\" : {\"path\": \"/some/path/\"," \
                                              "\"application_id\": 1}," \
                                "\"app_2\" : {\"path\": \"/some/path/\"," \
                                              "\"application_id\": 2}" \
                            "}"

        with patch('adk.utils.open', mock_open(read_data=dummy_apps_config)):
            data = read_json_file(self.path)
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

        with patch('adk.utils.open', mock_open(read_data=malformed_apps_config)):
            self.assertRaises(MalformedJsonFile, read_json_file, self.path)

    def test_read_json_file_not_found(self):
        with patch('adk.utils.open', side_effect=FileNotFoundError):
            self.assertRaises(JsonFileNotFound, read_json_file, self.path)

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
        py_dummy = get_py_dummy()
        self.assertIn('def main(app_config=None, x=0, y=0):', py_dummy)
        self.assertIn('if __name__ == "__main__":', py_dummy)

    def test_get_default_manifest(self):
        default_manifest = get_default_manifest('my_app')
        self.assertDictEqual({"application": {"name": "my_app",
                                              "description": "add description",
                                              "multi_round": False},
                              "remote": {}}, default_manifest)


    def test_validate_path_name(self):
        self.assertRaises(InvalidPathName, validate_path_name, "object", self.invalid_name)

    def test_copy_files(self):
        with patch("adk.utils.os.path.isfile") as isfile_mock, \
             patch("adk.utils.os.listdir") as listdir_mock, \
             patch("adk.utils.shutil.copy") as copy_mock, \
             patch("adk.utils.os.path.join") as join_mock:

            isfile_mock.return_value = True
            listdir_mock.return_value = ['file1', 'file2']
            join_mock.side_effect = ['file1_path', 'file2_path']

            copy_files(Path("source"), Path("dest"))

            join_calls = [call(Path("source"), 'file1'), call(Path("source"), 'file2')]
            join_mock.assert_has_calls(join_calls)
            copy_calls = [call("file1_path", Path("dest")), call("file2_path", Path("dest"))]
            copy_mock.assert_has_calls(copy_calls)

    def test_move_files(self):
        with patch("adk.utils.os.path.isfile") as isfile_mock, \
             patch("adk.utils.shutil.move") as move_mock, \
             patch("adk.utils.os.path.join") as join_mock:

            isfile_mock.side_effect = [True, False, True, False]
            join_mock.side_effect = ['file1_src_path', 'file1_dst_path', 'file2_src_path', 'file2_dst_path']

            move_files(Path("source"), Path("dest"), ['file1', 'file2'])

            join_calls = [call(Path("source"), 'file1'), call(Path("dest"), 'file1'),
                          call(Path("source"), 'file2'), call(Path("dest"), 'file2')]
            join_mock.assert_has_calls(join_calls)
            move_calls = [call("file1_src_path", Path("dest")),
                          call("file2_src_path", Path("dest"))]
            move_mock.assert_has_calls(move_calls)

    def test_do_not_move_existing_files(self):
        with patch("adk.utils.os.path.isfile") as isfile_mock, \
             patch("adk.utils.shutil.move") as move_mock, \
             patch("adk.utils.os.path.join") as join_mock:

            isfile_mock.side_effect = [False, False]
            join_mock.side_effect = ['file1_src_path', 'file1_dst_path', 'file2_src_path', 'file2_dst_path']

            move_files(Path("source"), Path("dest"), ['file1', 'file2'])

            join_calls = [call(Path("source"), 'file1'), call(Path("dest"), 'file1'),
                          call(Path("source"), 'file2'), call(Path("dest"), 'file2')]
            join_mock.assert_has_calls(join_calls)
            move_mock.assert_not_called()

    def test_check_python_syntax(self):
        valid_python_code = 'def main(app_config=None):\n    # Put your code here\n    return {}\n\n\n' \
                     'if __name__ == "__main__": \n    main()\n'

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            valid, message = check_python_syntax(self.path)

        self.assertTrue(valid)
        self.assertEqual(message, 'ok')

        invalid_python_code = 'definition main(app_config=None):\n    # Put your code here\n    return {}\n\n\n' \
                     'if __name__ == "__main__": \n    main()\n'

        with patch('adk.utils.open', mock_open(read_data=invalid_python_code)):
            valid, message = check_python_syntax(self.path)

        self.assertFalse(valid)
        self.assertIn('SyntaxError: invalid syntax', message)

    def test_get_function_arguments(self):
        valid_python_code = 'def main(app_config=None, q1=1, q3=3):\n    # Put your code here\n    return {}\n\n\n' \
                            'if __name__ == "__main__": \n    main()\n'

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            param_list = get_function_arguments(self.path, 'main')

        self.assertEqual(len(param_list), 3)
        self.assertEqual(param_list, ['app_config', 'q1', 'q3'])

        valid_python_code = 'def main1():\n    # Put your code here\n    return {}\n\n\n' \
                            'if __name__ == "__main__": \n    main1()\n'

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            param_list = get_function_arguments(self.path, 'main1')

        self.assertEqual(len(param_list), 0)
        self.assertEqual(param_list, [])

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            param_list = get_function_arguments(self.path, 'another_function')

        self.assertIsNone(param_list)

        invalid_python_code = 'definition main(app_config=None, q1=1, q3=3):\n    ' \
                              '# Put your code here\n    return {}\n\n\n' \
                              'if __name__ == "__main__": \n    main()\n'

        with patch('adk.utils.open', mock_open(read_data=invalid_python_code)):
            param_list = get_function_arguments(self.path, 'main')

        self.assertEqual(len(param_list), 0)
        self.assertEqual(param_list, [])

    def test_get_function_return_variables(self):
        dummy_file = os.path.join(os.path.dirname(__file__), 'data', 'dummy.py')
        with open(dummy_file,  encoding='utf-8') as f:
            valid_python_code = f.read()

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            return_list = get_function_return_variables(self.path, 'main')

        self.assertEqual(len(return_list), 2)

        self.assertEqual(len(return_list[0]), 9)
        self.assertListEqual(return_list[0], ['table', 'x_basis_count', 'z_basis_count', 'same_basis_count',
                                             'outcome_comparison_count', 'diff_outcome_count', 'qber',
                                             'key_rate_potential', 'raw_key'])

        self.assertEqual(len(return_list[1]), 1)
        self.assertListEqual(return_list[1], ['Q1'])

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            return_list = get_function_return_variables(self.path, 'main_another')

        self.assertIsNone(return_list)

        invalid_python_code = 'definition main(app_config=None, q1=1, q3=3):\n    ' \
                              '# Put your code here\n    return {}\n\n\n' \
                              'if __name__ == "__main__": \n    main()\n'

        with patch('adk.utils.open', mock_open(read_data=invalid_python_code)):
            return_list = get_function_return_variables(self.path, 'main')

        self.assertListEqual(return_list, [])

        dummy_file = os.path.join(os.path.dirname(__file__), 'data', 'dummy_non_dict_return.py')
        with open(dummy_file, encoding='utf-8') as f:
            valid_python_code = f.read()

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            return_list = get_function_return_variables(self.path, 'main')

        self.assertEqual(len(return_list), 0)

        dummy_file = os.path.join(os.path.dirname(__file__), 'data', 'dummy_mixed_return.py')
        with open(dummy_file, encoding='utf-8') as f:
            valid_python_code = f.read()

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            return_list = get_function_return_variables(self.path, 'main')

        self.assertEqual(len(return_list), 1)

    def test_get_function_return_variables_recursive(self):
        dummy_file = os.path.join(os.path.dirname(__file__), 'data', 'dummy_recursive.py')
        with open(dummy_file,  encoding='utf-8') as f:
            valid_python_code = f.read()

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            return_list = get_function_return_variables(self.path, 'main')

        self.assertEqual(len(return_list), 2)

        self.assertEqual(len(return_list[0]), 3)
        self.assertCountEqual(return_list[0], ['square1', 'col1', 'string1'])

        self.assertEqual(len(return_list[1]), 4)
        self.assertCountEqual(return_list[1], ['square', 'col', 'number', 'string'])

        dummy_file_1 = os.path.join(os.path.dirname(__file__), 'data', 'dummy_recursive_1.py')
        with open(dummy_file_1, encoding='utf-8') as f:
            valid_python_code = f.read()

        with patch('adk.utils.open', mock_open(read_data=valid_python_code)):
            return_list = get_function_return_variables(self.path, 'main')

        self.assertEqual(len(return_list), 3)

        self.assertEqual(len(return_list[0]), 3)
        self.assertCountEqual(return_list[0], ['square1', 'col1', 'string1'])

        self.assertEqual(len(return_list[1]), 4)
        self.assertCountEqual(return_list[1], ['square', 'col', 'number', 'string'])

        self.assertEqual(len(return_list[2]), 5)
        self.assertCountEqual(return_list[2], ['first_return', 'square', 'col', 'number', 'string'])
