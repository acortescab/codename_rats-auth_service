from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_read_db, get_write_db
from app.factories import create_auth_service, create_player_service, create_token_service

WriteDBDep = Annotated[Session, Depends(get_write_db)]
ReadDBDep = Annotated[Session, Depends(get_read_db)]

def get_auth_service(write_db: WriteDBDep, read_db: ReadDBDep):
    """
    Returns an AuthService instance initialized with the database connection.
    """
    return create_auth_service(write_db, read_db)

def get_token_service(write_db: WriteDBDep, read_db: ReadDBDep):
    """
    Returns a TokenService instance initialized with the database connection
    """
    return create_token_service(write_db, read_db)

def get_player_service(write_db: WriteDBDep, read_db: ReadDBDep):
    """
    Returns a PlayerService instance initialized with the database connection
    """
    return create_player_service(write_db, read_db)