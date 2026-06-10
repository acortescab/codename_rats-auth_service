from enum import Enum
from fastapi.security import HTTPBearer


class JWTAlgorithm(str, Enum):
    """
    Enum for Encryptation algorithm
    """
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    
oauth2_scheme = HTTPBearer()