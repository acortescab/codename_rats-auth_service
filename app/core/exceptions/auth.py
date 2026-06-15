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

class InvalidCredentials(Exception):
    """
    Exception raised when login credentials are not valid
    """
    def __init__(self, message: str = "Invalid registration"):
        """
        Constructor
        """
        self.message = message
        super().__init__(message)

class InvalidRegistration(Exception):
    """
    Exception raised when registration is not valid
    """
    def __init__(self, message: str = "Invalid registration"):
        """
        Constructor
        """
        self.message = message
        super().__init__(message)