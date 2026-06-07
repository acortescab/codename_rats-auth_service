from enum import Enum
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer


class JWTAlgorithm(str, Enum):
    """
    Enum for Encryptation algorithm
    """
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
OAuthDep = Annotated[str, Depends(oauth2_scheme)]