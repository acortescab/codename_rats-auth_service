from fastapi import Depends
from typing import Annotated
from app.factories import create_auth_service
from app.db.session import get_write_db, get_read_db
from sqlalchemy.orm import Session

WriteDBDep = Annotated[Session, Depends(get_write_db)]
ReadDBDep = Annotated[Session, Depends(get_read_db)]

def get_auth_service(write_db: WriteDBDep, read_db: ReadDBDep):
    """
    Returns an AuthService instance initialized with the database connection.
    """
    return create_auth_service(write_db, read_db)