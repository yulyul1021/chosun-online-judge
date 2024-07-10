from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.dependencies import SessionDep
from app.core import security
from app.core.config import settings
from app.models import Token

router = APIRouter()


# 로그인(JWT 생성)
@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, student_id=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect id or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.student_id, expires_delta=access_token_expires
        ),
        token_type="bearer",
        username=user.student_id,
        is_professor=user.is_professor
    )


# 비밀번호 재설정