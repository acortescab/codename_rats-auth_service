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