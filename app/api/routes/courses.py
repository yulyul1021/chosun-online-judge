from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from sqlmodel import select
from starlette import status

from app import crud
from app.api.dependencies import SessionDep, CurrentUser, get_current_superuser, get_current_professor
from app.models import (CoursesPublic, Course, Student, CoursePublic, CourseCreate,
                        ProblemsPublic, Message, CourseProblem, ProblemPublic, Problem, CourseProblemCreate)

router = APIRouter()


@router.get("/", response_model=CoursesPublic)
def read_my_course_list(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    내 수업 불러오기
    """
    if current_user.is_professor:
        statement = select(Course).where(Course.professor_id == current_user.id)
        courses = session.exec(statement).all()
        count = session.exec(select(func.count()).select_from(statement.subquery())).one()
    else:
        statement = (
            select(Course)
            .join(Student)
            .where(Student.user_id == current_user.id)
            .where(Course.is_active)
        )
        courses = session.exec(statement).all()
        count = session.exec(select(func.count()).select_from(statement.subquery())).one()

    return CoursesPublic(data=courses, count=count)


@router.post("/create", dependencies=[Depends(get_current_superuser)], response_model=CoursePublic)
def create_course(session: SessionDep, course_in: CourseCreate) -> Course:
    """
    수업 생성(관리자)
    """
    course = crud.create_course(session=session, course_in=course_in)
    return course


@router.patch("/{course_id}/disable", dependencies=[Depends(get_current_professor)], response_model=Message)
def disable_course(session: SessionDep, current_user: CurrentUser, course_id: int) -> Message:
    """
    해당 수업course_id의 담당 교수자: 수업 비공개
    """
    course = session.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.professor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to update this course")

    course.is_active = False
    session.add(course)
    session.commit()
    session.refresh(course)
    return Message(messade="수업이 비공개로 전환 되었습니다.")


@router.patch("/{course_id}/enable", dependencies=[Depends(get_current_professor)], response_model=Message)
def enable_course(session: SessionDep, current_user: CurrentUser, course_id: int) -> Message:
    """
    해당 수업course_id의 담당 교수자: 수업 공개
    """
    course = session.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.professor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to update this course")

    course.is_active = True
    session.add(course)
    session.commit()
    session.refresh(course)
    return Message(message="수업이 공개로 전환 되었습니다.")


@router.get("/{course_id}", response_model=ProblemsPublic)
def read_problem_list_in_my_course(session: SessionDep, current_user: CurrentUser, course_id: int):
    """
    해당 수업course_id의 담당 교수자 및 학생: 수업에 있는 문제 목록
    """
    course = session.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if current_user.is_professor:
        statement = select(CourseProblem).where(Course.course_id == course_id)
        count = session.exec(statement).one()
        problems = session.exec(statement).all()
    else:
        statement = select(CourseProblem).where(Course.course_id == course_id and Course.is_active)
        count = session.exec(statement).one()
        problems = session.exec(statement).all()

    return ProblemsPublic(data=problems, count=count)


@router.post("/{course_id}/{problem_id}/add", dependencies=[Depends(get_current_professor)], response_model=ProblemPublic)
def add_problem(session: SessionDep, current_user: CurrentUser, course_problem_in: CourseProblemCreate, course_id: int, problem_id: int) -> Any:
    """
    해당 수업course_id의 담당 교수자: 전체 문제 목록에서 문제(problem_id) 가져와서 수업(course_id)에 추가하기
    """
    course = session.query(Course).filter(Course.id == course_id).first()
    problem = session.query(Problem).filter(Problem.id == problem_id).first()

    if not course or not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    if course.professor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to update this course")

    new_problem = crud.add_problem_in_course(course_problem_in=course_problem_in, course_id=course_id, problem_id=problem_id)
    return new_problem


#TODO 수업에 조교 임명(교수)
