import json

import jsonschema
from jsonschema import Draft7Validator, RefResolver, draft7_format_checker
from cli.exceptions import JSONSchemaValidationError, JSONValidationError


def validate_json_string(instance_path):
    try:
        with open(instance_path, mode="r") as instance_value:
            _ = json.load(instance_value)
    except json.decoder.JSONDecodeError as e:
        raise JSONValidationError(e, instance_path)


def validate_json_schema(instance_path, schema_path):
    try:
        with open(instance_path, mode="r") as instance_value:
            with open(schema_path, mode="r") as schema_value:
                json_schema = json.load(schema_value)
                json_file = json.load(instance_value)

                resolver = RefResolver(base_uri=f'file://{schema_path}', referrer=json_schema)
                Draft7Validator(json_schema, resolver=resolver, format_checker=draft7_format_checker).validate(json_file)
    except jsonschema.exceptions.ValidationError as ve:
        raise JSONSchemaValidationError(ve, schema_path)


def validate_json(instance_path, schema_path):
    # Check instance for correct json syntax
    validate_json_string(instance_path)

    # Check instance against schema
    validate_json_schema(instance_path, schema_path)
