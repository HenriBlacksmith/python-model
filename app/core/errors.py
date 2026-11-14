class CoreError(Exception):
    message: str


class UserNotFoundError(CoreError):
    message = "User not found."


class UsernameAlreadyInUseError(CoreError):
    message = "The requested username is already in use."
