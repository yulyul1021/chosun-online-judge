from fastapi import APIRouter, Depends
from sqlmodel import select

from app.api.dependencies import SessionDep, get_current_superuser
from app.models import User

router = APIRouter()


@router.get("/users", dependencies=[Depends(get_current_superuser)])
def read_all_users(session: SessionDep,
                   student_id: str | None,
                   skip: int = 0, limit: int = 30):
    """
    모든 유저 읽기
    """
    # 페이징, 검색 가능
    statement = select(User)
    users = session.exec(statement).all()
    return users




"""
회원
- 유저 조회(전체 or 검색가능)
- 특정 유저의 수업/제출 조회
- 유저 CRUD
- 특정 유저 권한 변경

수업
- 수업 조회(전체 or 검색가능)
- 수업 CRUD
- 해당 수업의 문제 CRUD
- 수업에 교수자 임명
- 수업에 학생들 추가

문제
- 전체 문제 조회(전체 or 검색가능)
- 문제 CRUD
-

제출
- 전체 제출 조회(전체 or 검색가능)
- 재채점

"""