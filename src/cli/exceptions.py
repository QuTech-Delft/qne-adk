class MalformedJsonFile(Exception):
    """ Raised when trying to read a file containing malformed json """


class ApplicationAlreadyExists(Exception):
    """ Raised when application name is not unique and already exists in .qne/application.json"""

    # TODO: Can't they use application delete command instead of giving the path location?
    def __init__(self, application: str, path: str) -> None:
        super().__init__(f"Application '{application}' already exists. Application location: '{path}'")


class NoNetworkAvailable(Exception):
    """ Raised when there is no networks available with the amount nodes compared with the amount of roles"""

    def __init__(self) -> None:
        super().__init__("No network available which contains enough nodes for all the roles.")


class NotEnoughRoles(Exception):
    """ Raised when only one role is given"""

    def __init__(self) -> None:
        super().__init__("The amount of roles must be higher than one")


class JSONLoadInvalid(Exception):
    """ Raised when trying to load invalid JSON"""

    def __init__(self, path: str) -> None:
        super().__init__(f"Trying to load invalid JSON. File trying to load: '{path}'")


class InvalidApplicationName(Exception):
    """ Raised when one of the following characters are used in the application name ['/', '\', '*', ':', '?', '"',
        '<', '>', '|']"""

    def __init__(self, application: str) -> None:
        super().__init__(f"The application '{application}' cannot consist of the following characters: ['/', '\\', '*',"
                         f" ':', '?', '\"', '<', '>', '|']")


class InvalidRoleName(Exception):
    """ Raised when one of the following characters are used in a role name ['/', '\', '*', ':', '?', '"', '<', '>',
    '|']"""

    def __init__(self, role: str) -> None:
        super().__init__(f"Role name '{role}' cannot consist of the following characters: ['/', '\\', '*', ':', '?', "
                         f"'\"', '<', '>', '|']")
