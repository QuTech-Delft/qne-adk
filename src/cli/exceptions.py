from pathlib import Path

class MalformedJsonFile(Exception):
    """Raised when trying to read a file containing malformed json """

    def __init__(self, path: Path, e: Exception) -> None:
        super().__init__(f'The file {path} does not contain valid json. Error: {e}')


class ApplicationAlreadyExists(Exception):
    """Raised when application name is not unique and already exists in .qne/application.json"""

    def __init__(self, application: str, path: str) -> None:
        super().__init__(f"Application '{application}' already exists. Application location: '{path}'")


class ApplicationNotFound(Exception):
    """ Raised when application is not found in .qne/application.json"""

    def __init__(self, application: str) -> None:
        super().__init__(f"Application '{application}' was not found.")


class NetworkNotFound(Exception):
    """ Raised when the specified network was not found"""

    def __init__(self, network: str) -> None:
        super().__init__(f"Network {network} was not found.")


class NetworkNotAvailableForApplication(Exception):
    """ Raised when the given network is not available for use in the application"""

    def __init__(self, network: str, application: str) -> None:
        super().__init__(f"Network {network} is not available for use in Application {application}")


class NoNetworkAvailable(Exception):
    """Raised when there are no networks available with the amount nodes compared with the amount of roles"""

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


class ApplicationDoesNotExist(Exception):
    """Raised when application path (the current path the user is in) doesn't match any of the application paths in
    .qne/application.json"""

    def __init__(self) -> None:
        super().__init__("Current directory does not appear to be a valid application directory")


class NoConfigFileExists(Exception):
    """Raised when .qne/application.json doesn't exist"""

    def __init__(self, path: Path) -> None:
        super().__init__(f"The application configuration file {path} does not exist")


class ExperimentDirectoryAlreadyExists(Exception):
    """ Raised when a directory for experiment already exists at the given path """

    def __init__(self, experiment_name: str, path: str) -> None:
        super().__init__(f"Directory for Experiment '{experiment_name}' already exists at location: '{path}'")
