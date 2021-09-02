from pathlib import Path
from unittest.mock import patch, mock_open
import unittest

from cli.utils import read_json_file
from cli.exceptions import MalformedJsonFile

class TestUtils(unittest.TestCase):

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
