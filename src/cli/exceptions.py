class MalformedJsonFile(Exception):
    """ Raised when trying to read a file containing malformed json """


class ApplicationAlreadyExists(Exception):
    """ Raised when application name is not unique and already exists in .qne/application.json"""

    def __init__(self, application: str, path: str) -> None:
        super().__init__(f"Application '{application}' already exists. Application location: '{path}'")


class NoNetworkAvailable(Exception):
    """ Raised when there is no networks available with the amount nodes compared with the amount of roles"""

    def __init__(self) -> None:
        super().__init__("No network available which contains enough nodes for all the roles.")


class NotEnoughRoles(Exception):
    """ Raised when only one role is given"""

    def __init__(self) -> None:
        super().__init__("The number of roles must be higher than one")


class InvalidPathName(Exception):
    """ Raised when one of the following characters are used in an input name ['/', '\', '*', ':', '?', '"', '<', '>',
    '|']"""

    def __init__(self, obj: str) -> None:
        super().__init__(f"{obj} name can't contain any of the following characters: ['/', '\\', '*',"
                         f" ':', '?', '\"', '<', '>', '|']")


class SchemaValidationError(Exception):
    """Raised when json file doesn't meet the requirements of the schema"""

    def __init__(self, message="The JSON file you are trying to load does not contain all the required fields"):
        self.message = message
        super().__init__(self.message)


class JSONValidationError(Exception):
    """Raised when JSON string is not valid"""

    def __init__(self, message="The JSON file you are trying to load has invalid syntax"):
        self.message = message
        super().__init__(self.message)


class ApplicationDoesntExist(Exception):
    """Raised when application name doesn't exist in .qne/application.json"""

    def __init__(self, message="Application directory not found. Please make sure you are in your application directory "
                               "before validating or first create your application"):
        self.message = message
        super().__init__(self.message)


class ApplicationDirectoryNotComplete(Exception):
    """Raised when the application directory does not contain all the directories and files necessary (MANIFEST, config,
    and application"""
    def __init__(self, message="Please make sure your application consists of a MANIFEST.ini, application directory and "
                               "config directory"):
        self.message = message
        super().__init__(self.message)


class ApplicationConfigNotComplete(Exception):
    """Raised when the the 'application_name'/config directory is not complete. Should contain the JSON files application,
    network and result"""

    def __init__(self, message="Are you sure the configuration directory is complete? Should contain the JSON files "
        "network.json, result.json and application.json"):
        self.message = message
        super().__init__(self.message)


class ApplicationFilesNonExisting(Exception):
    """Raised when the the 'application_name'/application directory is not complete. Should contain at least one Python
        file"""

    def __init__(self, message="Are you sure the application directory is complete? Should contain at least one Python "
                               "file"):
        self.message = message
        super().__init__(self.message)

