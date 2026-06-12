from enum import Enum

from fastapi.security import HTTPBearer
from passlib.context import CryptContext


class JWTAlgorithm(str, Enum):
    """
    Enum for Encryptation algorithm
    """
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    
oauth2_scheme = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Creates an encrypted hash for password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies is the plain password matchs with the hashed one
    """
    return pwd_context.verify(plain_password, hashed_password)