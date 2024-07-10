from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.dependencies import SessionDep
from app.models import UserCreate, UserRegister, UserPublic, Message

router = APIRouter()


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    유저 생성(회원가입)
    """
    user = crud.get_user_by_student_id(session=session, student_id=user_in.student_id)
    if user:    # 이미 존재하는 사용자(학번)
        raise HTTPException(
            status_code=400,
            detail="The user with this student id already exists in the system",
        )

    if user_in.password != user_in.verify_password:
        return Message(message="비밀번호가 다릅니다.")

    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user


#TODO 유저 읽기
#TODO 유저 삭제(탈퇴)