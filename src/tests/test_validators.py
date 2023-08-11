from pathlib import Path
from unittest.mock import patch
import unittest

from adk.exceptions import JsonFileNotFound, MalformedJsonFile, PackageNotComplete
from adk.validators import validate_json_file, validate_json_schema


class TestValidators(unittest.TestCase):

    def setUp(self) -> None:
        self.path = Path("dummy")
        self.roles = ["role1", "role2"]
        self.invalid_name = "invalid/name"
        self.json_file = {
            "application": [
                {
                    "title": "Title for this application",
                    "description": "Description of this application"
                }
            ]
        }

        self.schema_file = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "application": {
                    "type": "array",
                    "items": [
                        {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "title",
                                "description"
                            ]
                        }
                    ]
                }
            },
            "required": [
                "application"
            ]
        }

    def test_validate_json_schema_fails(self):
        with patch("adk.validators.read_json_file") as read_json_file_mock:
            read_json_file_mock.side_effect = [self.json_file, JsonFileNotFound("schema/applications/application.json")]
            self.assertRaises(PackageNotComplete, validate_json_schema, self.path, self.path)

        with patch("adk.validators.read_json_file") as read_json_file_mock:
            read_json_file_mock.side_effect = JsonFileNotFound("applications/application.json")
            self.assertEqual(validate_json_schema(self.path, self.path),
                             (False, "File 'applications/application.json' not found"))

        with patch("adk.validators.read_json_file") as read_json_file_mock:
            read_json_file_mock.side_effect = MalformedJsonFile(str(self.path),
                                                                Exception("Extra data: line 1 column 1 (char 31)"))

            return_value, error = validate_json_schema(self.path, self.path)
            self.assertEqual(return_value, False)
            self.assertIn(f"The file '{str(self.path)}' does not contain valid json. "
                          f"Extra data: line 1 column 1 (char 31)", error)

    def test_validate_json_schema(self):
        with patch("adk.validators.read_json_file") as read_json_file_mock:

            read_json_file_mock.side_effect = [self.json_file, self.schema_file]

            validate_json_schema(self.path, self.path)
            self.assertEqual(read_json_file_mock.call_count, 2)
            read_json_file_mock.assert_called_with(self.path)

            read_json_file_mock.reset_mock()
            read_json_file_mock.side_effect = [self.json_file, self.schema_file]
            validate_json_schema(self.path, self.path)
            self.assertEqual(read_json_file_mock.call_count, 2)
            read_json_file_mock.assert_called_with(self.path)

            # Raise ValidationError when validation returns False
            wrong_json_file = {
              "application": [
                {
                  "description": "Description of this application"
                }
              ]
            }

            read_json_file_mock.reset_mock()
            read_json_file_mock.side_effect = [wrong_json_file, self.schema_file]
            validate_json_schema(self.path, self.path)
            self.assertEqual(read_json_file_mock.call_count, 2)
            read_json_file_mock.assert_called_with(self.path)

    def test_validate_json_file(self):
        with patch("adk.validators.read_json_file") as read_json_file_mock:

            read_json_file_mock.return_value = '{}'
            self.assertEqual(validate_json_file(self.path), (True, None))
            read_json_file_mock.assert_called_once_with(self.path)

            # When file doesn't exist
            read_json_file_mock.side_effect = JsonFileNotFound(f"{str(self.path)}")
            self.assertEqual(validate_json_file(self.path), (False, f"File '{str(self.path)}' not found"))

            # When file isn't json
            read_json_file_mock.side_effect = MalformedJsonFile(str(self.path),
                                                                Exception("Extra data: line 1 column 1 (char 31)"))
            return_value, error = validate_json_file(self.path)
            self.assertEqual(return_value, False)
            self.assertIn(f"The file '{str(self.path)}' does not contain valid json. "
                          f"Extra data: line 1 column 1 (char 31)", error)
