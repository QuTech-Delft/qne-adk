class MalformedJsonFile(Exception):
    """ Raised when trying to read a file containing malformed json """


class ApplicationAlreadyExists(Exception):
    """ Raised when application name is not unique and already exists in .qne/application.json"""

    def __init__(self, application: str) -> None:
        super().__init__(f"Application '{application}' already exists. Please delete the existing application or "
                         f"rename the one that you are trying to create")


class NoNetworkAvailable(Exception):
    """ Raised when there is no networks available with the amount nodes compared with the amount of roles"""

    def __init__(self) -> None:
        super().__init__("No network available which contains enough nodes for all the roles. Please lower the amount "
                         "of roles")
