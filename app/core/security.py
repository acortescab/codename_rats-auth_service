from enum import Enum

import bcrypt
from fastapi.security import HTTPBearer


class JWTAlgorithm(str, Enum):
    """
    Enum for Encryptation algorithm
    """
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    
oauth2_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    """
    Creates an encrypted hash for password
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies is the plain password matchs with the hashed one
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())