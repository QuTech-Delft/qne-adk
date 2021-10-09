from pathlib import Path
from unittest.mock import patch
import unittest
from cli.validators import validate_json_string, validate_json_schema, validate_json
from cli.exceptions import JSONSchemaValidationError


class TestValidators(unittest.TestCase):

    def setUp(self) -> None:
        self.path = Path("dummy")
        self.roles = ["role1", "role2"]
        self.invalid_name = "invalid/name"

    def test_validate_json_string(self):
        with patch("cli.validators.read_json_file") as read_json_file_mock:
            validate_json_string(self.path)
            read_json_file_mock.assert_called_once()

    def test_validate_json_schema(self):
        with patch("cli.validators.read_json_file") as read_json_file_mock:

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
            read_json_file_mock.assert_called_with(self.path)

            # Raise JSONSchemaValidationError when validation returns False
            wrong_json_file = {
              "application": [
                {
                  "description": "Description of this application"
                }
              ]
            }

            read_json_file_mock.reset_mock()
            read_json_file_mock.side_effect = [wrong_json_file, schema_file]
            self.assertRaises(JSONSchemaValidationError, validate_json_schema, self.path, self.path)
            read_json_file_mock.call_count = 2
            read_json_file_mock.assert_called_with(self.path)

    def test_validate_json(self):
        with patch("cli.validators.validate_json_string", return_value=True) as validate_json_string_mock, \
             patch("cli.validators.validate_json_schema", return_value=True) as validate_json_schema_mock:

            validate_json(self.path, self.path)
            validate_json_string_mock.assert_called_once_with(self.path)
            validate_json_schema_mock.assert_called_once_with(self.path, self.path)
