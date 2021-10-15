import platform
import os
import json
from pathlib import Path
from typing import Tuple, Any
from jsonschema import Draft7Validator, RefResolver, draft7_format_checker
from jsonschema.exceptions import ValidationError
from cli.utils import read_json_file


def validate_json_string(instance_path: Path) -> Tuple[bool, Any]:
    try:
        with open(instance_path, encoding="utf-8") as fp:
            json.load(fp)
        return True, None
    except Exception as e:
        return False, f"{instance_path} contains invalid json. {e}"


def validate_json_schema(instance_path: Path, schema_path: Path) -> Tuple[bool, Any]:
    try:
        json_file = read_json_file(instance_path)
        json_schema = read_json_file(schema_path)
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
