from pathlib import Path
from unittest.mock import patch
import unittest
from cli.validators import validate_json_file, validate_json_schema


class TestValidators(unittest.TestCase):

    def setUp(self) -> None:
        self.path = Path("dummy")
        self.roles = ["role1", "role2"]
        self.invalid_name = "invalid/name"

    def test_validate_json_schema(self):
        with patch("cli.validators.read_json_file") as read_json_file_mock, \
             patch("cli.validators.platform.system") as system_mock:

            json_file = {
              "application": [
                {
                  "title": "Title for this application",
                  "description": "Description of this application"
                }
              ]
            }

            schema_file = {
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

            read_json_file_mock.side_effect = [json_file, schema_file]

            validate_json_schema(self.path, self.path)
            read_json_file_mock.call_count = 2
            system_mock.assert_called_once()
            read_json_file_mock.assert_called_with(self.path)

            # If platform.system() equals windows
            system_mock.reset_mock()
            system_mock.return_value = "Windows"
            read_json_file_mock.reset_mock()
            read_json_file_mock.side_effect = [json_file, schema_file]
            validate_json_schema(self.path, self.path)
            system_mock.assert_called_once()
            read_json_file_mock.call_count = 2
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
            system_mock.reset_mock()
            system_mock.return_value = "Windows"
            read_json_file_mock.side_effect = [wrong_json_file, schema_file]
            validate_json_schema(self.path, self.path)
            read_json_file_mock.call_count = 2
            read_json_file_mock.assert_called_with(self.path)
            system_mock.assert_called_once()

    def test_validate_json_file(self):
        with patch("cli.validators.open") as open_mock, \
             patch("cli.validators.json.load") as load_mock:

            validate_json_file(self.path)
            open_mock.assert_called_once_with(self.path, encoding='utf-8')
            load_mock.assert_called_once()

            # When open fails
            open_mock.reset_mock()
            open_mock.return_value = False
            validate_json_file(self.path)
            open_mock.assert_called_once_with(self.path, encoding='utf-8')
