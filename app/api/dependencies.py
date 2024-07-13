from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session, sessionmaker
from starlette import status
from sqlmodel import Session as SQLModelSession

from app import crud
from app.core import security
from app.core.config import settings
from app.core.database import engine
from app.models import User


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/login/access-token"
)

SessionLocal = sessionmaker(class_=SQLModelSession, autoflush=False, bind=engine)


def get_session():
    with SessionLocal() as session:
        yield session


QueryDep = Annotated[str, Query()]
SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        student_id: str = payload.get("sub")
        if student_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = crud.get_user_by_student_id(session=session, student_id=student_id)
        if user is None:
            raise credentials_exception
        return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_professor(current_user: CurrentUser) -> User:
    if not current_user.is_professor:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
