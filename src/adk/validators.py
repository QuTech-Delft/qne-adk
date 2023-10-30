import os
from pathlib import Path
from urllib.parse import urlparse
from typing import Tuple, Any
from referencing import Registry, Resource
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

from adk.exceptions import JsonFileNotFound, MalformedJsonFile, PackageNotComplete
from adk.settings import BASE_DIR
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
        json_to_validate = read_json_file(file_name)
    except JsonFileNotFound as e:
        return False, str(e)
    except MalformedJsonFile as e:
        return False, f"{e}"

    try:
        schema = read_json_file(schema_path)
    except JsonFileNotFound:
        raise PackageNotComplete(str(schema_path)) from None

    schema_base_path = Path(os.path.join(BASE_DIR, 'schema'))

    def retrieve_schema(uri: str): # type: ignore
        path = schema_base_path / urlparse(uri).path[1:]
        contents = read_json_file(path)
        return Resource.from_contents(contents)

    try:
        registry = Registry(retrieve=retrieve_schema) # type: ignore
        Draft7Validator(schema, registry=registry).validate(json_to_validate)
        return True, None
    except ValidationError as ve:
        return False, f'In file {file_name}: {ve.message}'
