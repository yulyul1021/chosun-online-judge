from datetime import datetime

from sqlmodel import Session, select

from app.api.judge import Judge
from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, ProblemCreate, Problem, TestCasesCreate, TestCase, CourseCreate, Course, \
    CourseProblem, CourseProblemCreate, SubmissionCreate, Submission, Student


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_by_student_id(*, session: Session, student_id: str) -> User | None:
    statement = select(User).where(User.student_id == student_id)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, student_id: str, password: str) -> User | None:
    db_user = get_user_by_student_id(session=session, student_id=student_id)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_course(*, session: Session, course_in: CourseCreate) -> Course:
    db_course = Course.model_validate(course_in)
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return db_course


def create_problem_in_course(*, session: Session, problem_create: ProblemCreate,
                             testcases_in: TestCasesCreate, course_id: int, author_id: int) -> CourseProblem:
    problem = create_problem(session=session,
                             problem_create=problem_create,
                             testcases_in=testcases_in,
                             author_id=author_id)

    db_problem = CourseProblem.model_validate({
        "start_date": problem_create.start_date,
        "end_date": problem_create.end_date,
        "problem_id": problem.id,
        "course_id": course_id
    })
    session.add(db_problem)
    session.commit()
    session.refresh(db_problem)

    return db_problem


def create_problem(*, session: Session, problem_create: ProblemCreate,
                   testcases_in: TestCasesCreate, author_id: int) -> Problem:
    db_problem = Problem.model_validate({
        "title": problem_create.title,
        "content": problem_create.content
    }, update={"author_id": author_id})
    session.add(db_problem)
    session.commit()
    session.refresh(db_problem)
    create_testcases(session=session, testcases_in=testcases_in, problem_id=db_problem.id)

    return db_problem


def create_testcases(*, session: Session, testcases_in: TestCasesCreate, problem_id: int) -> None:
    inputs = testcases_in.input_texts
    outputs = testcases_in.output_texts
    for input_text, output_text in zip(inputs, outputs):
        db_testcase = TestCase.model_validate({
            "input_text": input_text,
            "output_text": output_text,
        }, update={"problem_id": problem_id})
        session.add(db_testcase)
        session.commit()
        session.refresh(db_testcase)
    return None


def add_problem_to_course(*, session: Session, course_problem_in: CourseProblemCreate, course_id: int, problem_id: int) -> CourseProblem:
    db_course_problem = CourseProblem.model_validate(course_problem_in, update={
        "course_id": course_id,
        "problem_id": problem_id
    })
    session.add(db_course_problem)
    session.commit()
    session.refresh(db_course_problem)
    return db_course_problem


def add_student_to_course(*, session: Session, course_id: int, student_id: int) -> Student:
    db_student = Student.model_validate({
        "course_id": course_id,
        "student_id": student_id,
    })
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student


def create_submission(*, session: Session, submission_in: SubmissionCreate, user_id: int, course_problem_id: int) -> Submission:
    problem = session.get(CourseProblem, course_problem_id).problem

    judge = Judge(submission_in=submission_in, testcases=problem.testcases)
    judge.run_code()

    db_submission = Submission.model_validate(submission_in, update={
        "user_id": user_id,
        "problem_id": course_problem_id,
        "score": judge.get_score(),
        "create_date": datetime.now()
    })
    session.add(db_submission)
    session.commit()
    session.refresh(db_submission)
    return db_submission