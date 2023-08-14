"""Exceptions for Qne Adk"""


class QneAdkException(Exception):
    """Base exception for Qne Adk exceptions"""


class ApiClientError(QneAdkException):
    """Raised on error from api client"""

    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class AppConfigNotFound(QneAdkException):
    """Raised when app_config is not found for application name or invalid (all remote app_versions are disabled)"""

    def __init__(self, application_name: str) -> None:
        super().__init__(f"Application configuration for application '{application_name}' was not found or invalid")


class ApplicationError(QneAdkException):
    """Raised when the application or app versions is not valid"""

    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class ApplicationAlreadyExists(QneAdkException):
    """Raised when application name is not unique and already exists in .qne/application.json"""

    def __init__(self, application_name: str, path: str) -> None:
        super().__init__(f"Application '{application_name}' already exists. Application location: '{path}'")


class ApplicationDoesNotExist(QneAdkException):
    """Raised when application path (the current path the user is in) doesn't match any of the application paths in
    .qne/application.json or when application path isn't identified as an application directory"""

    def __init__(self, application_path: str) -> None:
        super().__init__(f"Directory '{application_path}' does not appear to be a valid application directory")


class ApplicationNotComplete(QneAdkException):
    """Raised when application is not complete"""

    def __init__(self, application_name: str) -> None:
        super().__init__(f"Components of application '{application_name}' are missing")


class ApplicationNotFound(QneAdkException):
    """Raised when application is not found in .qne/application.json"""

    def __init__(self, application_name: str) -> None:
        super().__init__(f"Application '{application_name}' was not found")


class ApplicationValueError(QneAdkException):
    """Raised when a value in the application is not valid"""

    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class ApplicationFailedValidation(QneAdkException):
    """Raised when an application fails validation"""

    def __init__(self, application_name: str, validation_messages: str) -> None:
        super().__init__(f"Application '{application_name}' failed validation. Please resolve the following issues:\n"
                         f"{validation_messages}")


class AuthenticationError(QneAdkException):
    """Raised when authentication failed"""

    def __init__(self, message: str) -> None:
        super().__init__(f"Authentication failed: {message}")


class CommandNotImplemented(QneAdkException):
    """Raised when a command is used that is not yet implemented"""

    def __init__(self) -> None:
        super().__init__("Command is not yet implemented")


class ConnectApiError(QneAdkException):
    """Raised when could not connect to api"""

    def __init__(self, base_uri: str) -> None:
        super().__init__(f'Could not connect to {base_uri}')


class DirectoryIsFile(QneAdkException):
    """Raised when a directory we want to create is already a file"""

    def __init__(self, path: str) -> None:
        super().__init__(f"Cannot create directory '{path}'. It appears to be a file already")


class DirectoryAlreadyExists(QneAdkException):
    """Raised when a directory already exists at the given path"""

    def __init__(self, obj: str, path: str) -> None:
        super().__init__(f"{obj} directory '{path}' already exists")


class ExperimentDirectoryAlreadyExists(QneAdkException):
    """Raised when a directory for experiment already exists at the given path"""

    def __init__(self, experiment_name: str, path: str) -> None:
        super().__init__(f"Directory for Experiment '{experiment_name}' already exists at location: '{path}'")


class ExperimentDirectoryNotValid(QneAdkException):
    """Raised when experiment path (the current path the user is in) isn't identified as an experiment directory"""

    def __init__(self, experiment_path: str) -> None:
        super().__init__(f"Directory '{experiment_path}' does not appear to be a valid experiment directory")


class ExperimentFailed(QneAdkException):
    """Raised when an experiment failed running on the backend"""

    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class ExperimentNotRun(QneAdkException):
    """Raised when experiment was not run but results were fetched"""

    def __init__(self, experiment_path: str) -> None:
        super().__init__(f"Experiment in directory '{experiment_path}' did not run via command 'experiment run'")


class ExperimentValueError(QneAdkException):
    """Raised when a value in the experiment is not valid"""

    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class ExperimentFailedValidation(QneAdkException):
    """Raised when an experiment fails validation"""

    def __init__(self, validation_messages: str) -> None:
        super().__init__(f"Experiment failed validation. Please resolve the following issues:\n"
                         f"{validation_messages}")


class ExperimentExecutionError(QneAdkException):
    """Raised when an experiment encountered an error while running"""

    def __init__(self, message: str) -> None:
        super().__init__(f"Experiment encountered an error while running:\n{message}")


class InvalidPath(QneAdkException):
    """Raised when an invalid path was found in the appsource tarball"""

    def __init__(self, obj: str) -> None:
        super().__init__(f"Invalid path in tar-file: {obj}")


class InvalidPathName(QneAdkException):
    """Raised when one of the following characters are used in an input name ['/', '\', '*', ':', '?', '"', '<', '>',
    '|']"""

    def __init__(self, obj: str) -> None:
        super().__init__(f"{obj} name can't contain any of the following characters: ['/', '\\', '*',"
                         f" ':', '?', '\"', '<', '>', '|']")


class JobTimeoutError(QneAdkException):
    """Waiting for job results time out"""
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class JsonFileNotFound(QneAdkException):
    """Json file not found that was expected"""
    def __init__(self, file_name: str) -> None:
        super().__init__(f"File '{file_name}' not found")


class MalformedJsonFile(QneAdkException):
    """Raised when trying to read a file containing malformed json"""

    def __init__(self, file_name: str, e: Exception) -> None:
        super().__init__(f"The file '{file_name}' does not contain valid json. {e}")


class NetworkNotFound(QneAdkException):
    """Raised when the specified network was not found"""

    def __init__(self, network_name: str) -> None:
        super().__init__(f"Network {network_name} was not found.")


class NetworkNotAvailableForApplication(QneAdkException):
    """Raised when the given network is not available for use in the application"""

    def __init__(self, network_name: str, application_name: str) -> None:
        super().__init__(f"Network {network_name} is not available for use in Application {application_name}")


class NoNetworkAvailable(QneAdkException):
    """Raised when there are no networks available with the amount nodes compared with the amount of roles"""

    def __init__(self) -> None:
        super().__init__("No network available which contains enough nodes for all the roles")


class NotLoggedIn(QneAdkException):
    """Raised when remote host api is called without being logged in"""

    def __init__(self) -> None:
        super().__init__("Cannot connect to remote. Not logged in")


class PackageNotComplete(QneAdkException):
    """Essential package file is missing"""

    def __init__(self, file_name: str) -> None:
        super().__init__(f'File {file_name} not found. This file is essential for the correct operation of '
                         f'this package. Please reinstall the package')


class ResultDirectoryNotAvailable(QneAdkException):
    """Raised when the result directory is not present"""

    def __init__(self, path: str) -> None:
        super().__init__(f"Result directory is not available at location: '{path}'")


class RolesNotUnique(QneAdkException):
    """Raised when given roles are not unique. The test is case insensitive so 'Sender' and 'sender' are the same"""

    def __init__(self) -> None:
        super().__init__("The role names must be unique")


class SchemaError(QneAdkException):
    """Raised when error during schema validation"""

    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")
