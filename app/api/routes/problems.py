from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from starlette import status

from app import crud
from app.api.dependencies import get_current_professor, SessionDep, get_current_user, CurrentUser
from app.models import ProblemPublic, ProblemCreate, TestCasesCreate, Problem, CourseProblem, Message, Course, \
    ProblemsPublic

router = APIRouter()


@router.get("/", dependencies=[Depends(get_current_user)], response_model=ProblemsPublic)
def read_all_problems_list(session: SessionDep) -> Any:
    """
    전체 문제 리스트 읽기
    """
    statement = select(Problem)
    problems = session.exec(statement).all()
    return problems


@router.get("/{problem_id}", dependencies=[Depends(get_current_user)], response_model=ProblemPublic)
def read_problem(session: SessionDep, problem_id: int) -> Any:
    """
    전체 문제 중 해당 problem_id를 가진 문제 읽기
    """
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.post("/{course_id}/create", dependencies=[Depends(get_current_professor)], response_model=ProblemPublic)
def create_problem(session: SessionDep, course_id: int, problem_create: ProblemCreate, testcases_in: TestCasesCreate
) -> Any:
    """
    수업 내에서 새 문제 생성
    """
    course = session.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    problem = crud.create_problem_in_course(session=session,
                                            problem_create=problem_create,
                                            testcases_in=testcases_in,
                                            course_id=course_id)
    return problem


#TODO 문제 수정(문제, 테케 업데이트)
#TODO 문제 복제()
#TODO 문제 삭제 -> 수업에서
#TODO 문제 DB에서 삭제



