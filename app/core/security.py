from enum import Enum

class JWTAlgorithm(str, Enum):
    """
    Enum for Encryptation algorithm
    """
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
