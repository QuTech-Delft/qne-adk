from pathlib import Path
from jsonschema.exceptions import ValidationError


class MalformedJsonFile(Exception):
    """Raised when trying to read a file containing malformed json """

    def __init__(self, path: Path, e: Exception) -> None:
        super().__init__(f'The file {path} does not contain valid json. Error: {e}')


class ApplicationAlreadyExists(Exception):
    """Raised when application name is not unique and already exists in .qne/application.json"""

    def __init__(self, application: str, path: str) -> None:
        super().__init__(f"Application '{application}' already exists. Application location: '{path}'")


class NoNetworkAvailable(Exception):
    """Raised when there is no networks available with the amount nodes compared with the amount of roles"""

    def __init__(self) -> None:
        super().__init__("No network available which contains enough nodes for all the roles.")


class NotEnoughRoles(Exception):
    """Raised when only one role is given"""

    def __init__(self) -> None:
        super().__init__("The number of roles must be higher than one")


class InvalidPathName(Exception):
    """Raised when one of the following characters are used in an input name ['/', '\', '*', ':', '?', '"', '<', '>',
    '|']"""

    def __init__(self, obj: str) -> None:
        super().__init__(f"{obj} name can't contain any of the following characters: ['/', '\\', '*',"
                         f" ':', '?', '\"', '<', '>', '|']")


class SchemaValidationError(Exception):
    """Raised when json file doesn't meet the requirements of the schema"""

    def __init__(self) -> None:
        super().__init__("The JSON file you are trying to load does not contain all the required fields")


class JSONSchemaValidationError(Exception):
    """Raised when the JSON file is invalid when validation against a the schema file"""

    def __init__(self, error: ValidationError, schema_path: Path) -> None:
        super().__init__(f"Failed when validating against schema file. {schema_path} {error.message}")


class ApplicationDoesNotExist(Exception):
    """Raised when application path (the current path the user is in) doesn't match any of the application paths in
    .qne/application.json"""

    def __init__(self) -> None:
        super().__init__("Application path not found")


class ApplicationDirectoryNotComplete(Exception):
    """Raised when the application directory does not contain all the directories and files necessary (MANIFEST, config,
    and src"""

    def __init__(self, path: Path) -> None:
        super().__init__(f"{path} should contain a MANIFEST.ini, src directory and config directory")


class ApplicationConfigNotComplete(Exception):
    """Raised when the the application/config directory is not complete. Should contain the JSON files application,
    network and result"""

    def __init__(self, path: Path) -> None:
        super().__init__(f"{path} should contain the files network.json, result.json and application.json")


class ApplicationSourceFilesIncomplete(Exception):
    """Raised when the the application/src directory is not complete. Should contain at least two Python files"""

    def __init__(self, path: Path) -> None:
        super().__init__(f"{path} should contain at least two Python files")


class NoApplicationExists(Exception):
    """Raised when there are no applications listed in .qne/application.json"""

    def __init__(self, path: Path) -> None:
        super().__init__(f"No applications exists in application.json file: {path}")


class NoConfigFileExists(Exception):
    """Raised when .qne/application.json doesn't exist"""

    def __init__(self, path: Path) -> None:
        super().__init__(f"The application configuration file {path} does not exist")
