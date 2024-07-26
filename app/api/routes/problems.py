from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from starlette import status

from app import crud
from app.api.dependencies import get_current_professor, SessionDep, get_current_user, CurrentUser
from app.models import ProblemPublic, ProblemCreate, TestCasesCreate, Problem, CourseProblem, Message, Course, \
    ProblemsPublic

router = APIRouter()


@router.get("/all", dependencies=[Depends(get_current_professor)], response_model=ProblemsPublic)
def read_all_problem_list(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    교수자: 전체 문제 리스트 읽기
    """
    # TODO 페이징 처리
    statement = select(Problem)
    problems = session.exec(statement).all()
    return problems


@router.get("/all/{problem_id}", dependencies=[Depends(get_current_user)], response_model=ProblemPublic)
def read_problem(session: SessionDep, problem_id: int) -> Any:
    """
    교수자: 전체 문제 중 해당 problem_id를 가진 문제 읽기
    """
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.post("/create/{course_id}", dependencies=[Depends(get_current_professor)], response_model=ProblemPublic)
def create_problem(session: SessionDep,
                   current_user: CurrentUser,
                   course_id: int,
                   problem_create: ProblemCreate,
                   testcases_in: TestCasesCreate
) -> Any:
    """
    해당 수업course_id의 담당 교수자: 수업 내에서 새 문제 생성
    """
    course = session.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    problem = crud.create_problem_in_course(session=session,
                                            problem_create=problem_create,
                                            testcases_in=testcases_in,
                                            course_id=course_id,
                                            author_id=current_user.id
                                            )
    return problem


@router.get("/courses/{problem_id}", dependencies=[Depends(get_current_user)], response_model=ProblemPublic)
def read_problem_in_course(session: SessionDep, problem_id: int) -> Any:
    """
    해당 수업course_id의 담당 교수자, 학생: 수업 내의 문제 중 해당 (course)problem_id를 가진 문제 읽기
    """
    problem = session.get(CourseProblem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.patch("/courses/disable/{problem_id}", dependencies=[Depends(get_current_professor)],
              response_model=Message)
def disable_problem(session: SessionDep, current_user: CurrentUser, problem_id: int) -> Message:
    """
    해당 수업course_id의 담당 교수자: 수업 내의 문제 중 해당 (course)problem_id를 가진 문제 비공개
    """
    problem = session.query(CourseProblem).filter(CourseProblem.id == problem_id).first()
    course = session.query(Course).filter(Course.id == problem.course_id).first()

    if not course or not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    if course.professor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to update this course")

    problem.is_active = False
    session.add(problem)
    session.commit()
    session.refresh(problem)
    return Message(messade="문제가 비공개로 전환 되었습니다.")


@router.patch("/courses/enable/{problem_id}", dependencies=[Depends(get_current_professor)],
              response_model=Message)
def enable_problem(session: SessionDep, current_user: CurrentUser, problem_id: int) -> Message:
    """
    해당 수업course_id의 담당 교수자: 수업 내의 문제 중 해당 (course)problem_id를 가진 문제 공개
    """
    problem = session.query(CourseProblem).filter(CourseProblem.id == problem_id).first()
    course = session.query(Course).filter(Course.id == problem.course_id).first()

    if not course or not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    if course.professor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to update this course")

    problem.is_active = True
    session.add(problem)
    session.commit()
    session.refresh(problem)
    return Message(messade="문제가 공개로 전환 되었습니다.")


#TODO 문제 수정(문제, 테케 업데이트)
#TODO 문제 복제()
#TODO 문제 삭제 -> 수업에서
#TODO 문제 DB에서 삭제



