"""Exceptions for Qne Cli"""


class QneCliException(Exception):
    """Base exception for Qne Cli exceptions"""


class ApplicationAlreadyExists(QneCliException):
    """Raised when application name is not unique and already exists in .qne/application.json"""

    def __init__(self, application_name: str, path: str) -> None:
        super().__init__(f"Application '{application_name}' already exists. Application location: '{path}'")


class ApplicationDoesNotExist(QneCliException):
    """Raised when application path (the current path the user is in) doesn't match any of the application paths in
    .qne/application.json or when application path isn't identified as an application directory"""

    def __init__(self, application_path: str) -> None:
        super().__init__(f"Directory '{application_path}' does not appear to be a valid application directory")


class ApplicationNotFound(QneCliException):
    """Raised when application is not found in .qne/application.json"""

    def __init__(self, application_name: str) -> None:
        super().__init__(f"Application '{application_name}' was not found.")


class CommandNotImplemented(QneCliException):
    """Raised when a command is used that is not yet implemented"""

    def __init__(self) -> None:
        super().__init__("Command is not yet implemented")


class DirectoryIsFile(QneCliException):
    """Raised when a directory we want to create is already a file"""

    def __init__(self, path: str) -> None:
        super().__init__(f"Cannot create directory '{path}'. It appears to be a file already")


class DirectoryAlreadyExists(QneCliException):
    """Raised when a directory already exists at the given path"""

    def __init__(self, obj: str, path: str) -> None:
        super().__init__(f"{obj} directory '{path}' already exists")


class ExperimentDirectoryAlreadyExists(QneCliException):
    """Raised when a directory for experiment already exists at the given path"""

    def __init__(self, experiment_name: str, path: str) -> None:
        super().__init__(f"Directory for Experiment '{experiment_name}' already exists at location: '{path}'")


class ExperimentDirectoryNotValid(QneCliException):
    """Raised when experiment path (the current path the user is in) isn't identified as an experiment directory"""

    def __init__(self, experiment_path: str) -> None:
        super().__init__(f"Directory '{experiment_path}' does not appear to be a valid experiment directory")


class InvalidPathName(QneCliException):
    """Raised when one of the following characters are used in an input name ['/', '\', '*', ':', '?', '"', '<', '>',
    '|']"""

    def __init__(self, obj: str) -> None:
        super().__init__(f"{obj} name can't contain any of the following characters: ['/', '\\', '*',"
                         f" ':', '?', '\"', '<', '>', '|']")


class MalformedJsonFile(QneCliException):
    """Raised when trying to read a file containing malformed json"""

    def __init__(self, file_name: str, e: Exception) -> None:
        super().__init__(f"The file '{file_name}' does not contain valid json. {e}")


class NetworkNotFound(QneCliException):
    """Raised when the specified network was not found"""

    def __init__(self, network_name: str) -> None:
        super().__init__(f"Network {network_name} was not found.")


class NetworkNotAvailableForApplication(QneCliException):
    """Raised when the given network is not available for use in the application"""

    def __init__(self, network_name: str, application_name: str) -> None:
        super().__init__(f"Network {network_name} is not available for use in Application {application_name}")


class NoNetworkAvailable(QneCliException):
    """Raised when there are no networks available with the amount nodes compared with the amount of roles"""

    def __init__(self) -> None:
        super().__init__("No network available which contains enough nodes for all the roles")


class NotEnoughRoles(QneCliException):
    """Raised when only one role is given"""

    def __init__(self) -> None:
        super().__init__("The number of roles must be higher than one")


class JsonFileNotFound(QneCliException):
    """Json file not found that was expected"""
    def __init__(self, file_name: str) -> None:
        super().__init__(f"File '{file_name}' not found")


class PackageNotComplete(QneCliException):
    """Essential package file is missing"""

    def __init__(self, file_name: str) -> None:
        super().__init__(f'File {file_name} not found. This file is essential for the correct operation of '
                         f'this package. Please reinstall the package')


class RolesNotUnique(QneCliException):
    """Raised when given roles are not unique. The test is case insensitive so 'Sender' and 'sender' are the same"""

    def __init__(self) -> None:
        super().__init__("The role names must be unique")


class ResultDirectoryNotAvailable(QneCliException):
    """Raised when the result directory is not present"""

    def __init__(self, path: str) -> None:
        super().__init__(f"Result directory is not available at location: '{path}'")
