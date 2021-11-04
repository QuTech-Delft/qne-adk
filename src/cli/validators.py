import platform
import os
from pathlib import Path
from typing import Tuple, Any
from jsonschema import Draft7Validator, RefResolver, draft7_format_checker
from jsonschema.exceptions import ValidationError

from cli.exceptions import JsonFileNotFound, MalformedJsonFile, PackageNotComplete
from cli.utils import read_json_file


def validate_json_file(file_name: Path) -> Tuple[bool, Any]:
    try:
        read_json_file(file_name)
        return True, None
    except JsonFileNotFound as file_error:
        raise file_error
    except MalformedJsonFile as e:
        return False, str(e)


def validate_json_schema(instance_path: Path, schema_path: Path) -> Tuple[bool, Any]:
    """First check input for valid json, then check input for validity of the json schema"""
    try:
        json_file = read_json_file(instance_path)
    except MalformedJsonFile as malformed_json_error:
        return False, f"In file {instance_path}: {str(malformed_json_error)}"
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
        return False, f"In file {instance_path}: {ve.message}"
