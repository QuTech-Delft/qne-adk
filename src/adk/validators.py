import platform
import os
from pathlib import Path
from typing import Tuple, Any
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

from adk.exceptions import JsonFileNotFound, MalformedJsonFile, PackageNotComplete
from adk.utils import read_json_file


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

    resource = Resource(contents=json_schema, specification=DRAFT7)
    try:
        if platform.system() == 'Windows':
            path = os.path.dirname(schema_path)
            json_schema_full_path = os.path.realpath(path).replace('\\', '/')
            registry = Registry().with_resource(uri=f'file:///{json_schema_full_path}/', resource=resource)
        else:
            json_schema_full_path = os.path.realpath(schema_path)
            registry = Registry().with_resource(uri=f'file://{json_schema_full_path}', resource=resource)

        Draft7Validator(json_schema, registry=registry).validate(json_file)
        return True, None
    except ValidationError as ve:
        return False, f'In file {file_name}: {ve.message}'
