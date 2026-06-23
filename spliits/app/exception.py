class EmailAlreadyExists(Exception):
    pass

class NoUserExists(Exception):
    pass

class InvalidCredentials(Exception):
    pass

class NoPoolExist(Exception):
    pass

class AlreadyInThePool(Exception):
    pass

class ForbiddenUser(Exception):
    pass