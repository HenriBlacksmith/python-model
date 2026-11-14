class CoreError(Exception):
    message: str


class UserNotFoundError(CoreError):
    message = "User not found."
