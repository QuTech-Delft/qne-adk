import json
import os
import platform

import jsonschema
from jsonschema import Draft7Validator, RefResolver, draft7_format_checker
from cli.exceptions import JSONValidationError


def validate_json_string(value):
    try:
        _ = json.load(value)
    except json.decoder.JSONDecodeError:
        raise JSONValidationError


def validate_json_schema(instance, file):
    print("validate_json_schema:")
    print(instance)
    print(file)
    try:
        with open(file) as json_file:
            json_schema = json.load(json_file)
            print(json_schema)
            if platform.system() == 'Windows':
                path = os.path.dirname(file)
                json_schema_full_path = os.path.realpath(path).replace('\\', '/')
                resolver = RefResolver(base_uri=f'file:///{json_schema_full_path}/', referrer=json_schema)
            else:
                json_schema_full_path = os.path.realpath(file)
                resolver = RefResolver(base_uri=f'file://{json_schema_full_path}', referrer=json_schema)
            print(resolver)
            Draft7Validator(json_schema, resolver=resolver, format_checker=draft7_format_checker).validate(instance)
    except jsonschema.exceptions.ValidationError as ve:
        raise ve.SchemaValidationError({"json_schema_error": f"{'.'.join(str(x) for x in ve.path)}: {ve.message}"}) from ve


def validate_json_schema_serializer(instance, serializer):
    schema_file = getattr(getattr(serializer, 'Meta'), "json_schema", None)
    if schema_file is not None:
        validate_json_schema(instance, schema_file)


# def validate_case_insensitive_unique(model, field, value):
#     if model.objects.filter(**{field+"__iexact": value}).count() > 0:
#         raise DjangoValidationError({field: f"{model.__name__} with this {field} already exists."})
