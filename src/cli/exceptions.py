class MalformedJsonFile(Exception):
    """ Raised when trying to read a file containing malformed json """


class ApplicationAlreadyExists(Exception):
    """ Raised when application name is not unique and already exists in .qne/application.json"""

    def __init__(self) -> None:
        # Call the base class constructor with the parameters it needs
        super().__init__("Application already exists with the same name. Please delete the existing version or rename "
                         "the current")


class NoNetworkAvailable(Exception):
    """ Raised when there is no networks available with the amount nodes compared with the amount of roles"""

    def __init__(self) -> None:
        # Call the base class constructor with the parameters it needs
        super().__init__("No network available which contains enough nodes for every roll. Please lower the amount of "
                         "roles given as input parameter")
