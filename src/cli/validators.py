from pathlib import Path
import jsonschema
from jsonschema import Draft7Validator, RefResolver, draft7_format_checker
from cli.exceptions import JSONSchemaValidationError
from cli.utils import read_json_file


def validate_json_string(instance_path: Path) -> None:
    read_json_file(instance_path)


def validate_json_schema(instance_path: Path, schema_path: Path) -> None:
    try:
        json_file = read_json_file(instance_path)
        json_schema = read_json_file(schema_path)

        resolver = RefResolver(base_uri=f'file://{schema_path}', referrer=json_schema)
        Draft7Validator(json_schema, resolver=resolver, format_checker=draft7_format_checker). \
            validate(json_file)
    except jsonschema.exceptions.ValidationError as ve:
        raise JSONSchemaValidationError(ve, schema_path) from ve


def validate_json(instance_path: Path, schema_path: Path) -> None:
    # Check instance for correct json syntax
    validate_json_string(instance_path)

    # Check instance against schema
    validate_json_schema(instance_path, schema_path)
