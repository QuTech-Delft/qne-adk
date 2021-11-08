import platform
import os
from pathlib import Path
from typing import Tuple, Any
from jsonschema import Draft7Validator, RefResolver, draft7_format_checker
from jsonschema.exceptions import ValidationError

from cli.exceptions import JsonFileNotFound, MalformedJsonFile, PackageNotComplete
from cli.utils import read_json_file


def validate_json_file(file_name: Path) -> Tuple[bool, Any]:
    """Checks file for existence and valid json

    Args:
        file_name: The file to check

    Returns:
        False and an error message in case the file doesn't exist or is not valid json or True and None
    """
    try:
        read_json_file(file_name)
        return True, None
    except JsonFileNotFound as file_error:
        return False, str(file_error)
    except MalformedJsonFile as e:
        return False, str(e)


def validate_json_schema(file_name: Path, schema_path: Path) -> Tuple[bool, Any]:
    """First read input and check for existence and valid json. Then read schema and check schema for existence.
     Then check input for validity against the json schema.

    Args:
        file_name: The file to check
        schema_path: The schema to check the file against

    Returns:
        False and an error message in case:
            the input doesn't exist
            the input is not valid json
            the input is not valid json for the schema
        Otherwise True and None (success)
    Raises:
        PackageNotComplete when the schema is not found
    """
    try:
        json_file = read_json_file(file_name)
    except JsonFileNotFound as file_error:
        return False, str(file_error)
    except MalformedJsonFile as malformed_json_error:
        return False, f"{malformed_json_error}"
    try:
        json_schema = read_json_file(schema_path)
    except JsonFileNotFound:
        raise PackageNotComplete(str(schema_path)) from None
    try:
        if platform.system() == 'Windows':
            path = os.path.dirname(schema_path)
            json_schema_full_path = os.path.realpath(path).replace('\\', '/')
            resolver = RefResolver(base_uri=f'file:///{json_schema_full_path}/', referrer=json_schema)
        else:
            json_schema_full_path = os.path.realpath(schema_path)
            resolver = RefResolver(base_uri=f'file://{json_schema_full_path}', referrer=json_schema)
        Draft7Validator(json_schema, resolver=resolver, format_checker=draft7_format_checker).validate(json_file)
        return True, None
    except ValidationError as ve:
        return False, f'In file {file_name}: {ve.message}'
