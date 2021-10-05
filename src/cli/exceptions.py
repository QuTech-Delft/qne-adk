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


class JSONLoadInvalid(Exception):
    """ Raised when trying to load invalid JSON"""

    def __init__(self, path: str) -> None:
        super().__init__(f"Trying to load invalid JSON. File trying to load: '{path}'")


class InvalidPathName(Exception):
    """ Raised when one of the following characters are used in an input name ['/', '\', '*', ':', '?', '"', '<', '>',
    '|']"""

    def __init__(self, obj: str) -> None:
        super().__init__(f"{obj} name can't contain any of the following characters: ['/', '\\', '*',"
                         f" ':', '?', '\"', '<', '>', '|']")
