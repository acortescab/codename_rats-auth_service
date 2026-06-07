class InvalidRefreshTokenError(Exception):
    """
    Exception raised when not finding token or it's revoked
    """
    def __init__(self, message: str = "Invalid refresh token"):
        """
        Constructor
        """
        self.message = message
        super().__init__(message)

class InvalidToken(Exception):
    """
    Exception raised when token in header is not valid 
    """
    def __init__(self, message: str = "Invalid refresh token"):
        """
        Constructor
        """
        self.message = message
        super().__init__(message)