class MalformedJsonFile(Exception):
    """ Raised when trying to read a file containing malformed json """


class ApplicationAlreadyExists(Exception):
    """ Raised when application name is not unique and already exists in .qne/application.json"""
