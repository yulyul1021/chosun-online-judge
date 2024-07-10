from datetime import datetime
from enum import Enum
from typing import List

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class LanguageEnum(str, Enum):
    c = "c"
    cpp = "cpp"
    java = "java"
    python = "python"


class UserBase(SQLModel):
    student_id: str = Field(unique=True, index=True, max_length=8)
    email: EmailStr | None = Field(unique=True, max_length=255)
    is_professor: bool = False
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    student_id: str
    # email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    verify_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    submissions: List["Submission"] | None = Relationship(back_populates="submitter")

    courses_as_professor: List["Course"] | None = Relationship(back_populates="professor")
    courses_as_ta: List["TA"] | None = Relationship(back_populates="user")
    courses_as_student: List["Student"] | None = Relationship(back_populates="user")


class UserPublic(UserBase):
    id: int
    student_id: str


class CourseBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)


class CourseCreate(CourseBase):
    title: str = Field(min_length=1, max_length=255)
    professor_id: int


# Database model, database table inferred from class name
class Course(CourseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_active: bool = False

    professor_id: int | None = Field(default=None, foreign_key="user.id")
    professor: User | None = Relationship(back_populates="courses_as_professor")

    tas: List["TA"] | None = Relationship(back_populates="courses_as_ta")
    students: List["Student"] | None = Relationship(back_populates="courses_as_student")

    problems: List["CourseProblem"] | None = Relationship(back_populates="course")
    # languages: list["LanguageEnum"] = Field(sa_column_kwargs={"type_": "ENUM(LanguageEnum)"})
    # 사용할 수 있는 언어


class CoursePublic(CourseBase):
    id: int
    professor_id: int


class CoursesPublic(SQLModel):
    data: List[CoursePublic]
    count: int


# Database model, database table inferred from class name
class TA(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    course_id: int | None = Field(default=None, foreign_key="course.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)


# Database model, database table inferred from class name
class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    course_id: int | None = Field(default=None, foreign_key="course.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)


class ProblemBase(SQLModel):
    title: str
    content: str


# Database model, database table inferred from class name
class Problem(ProblemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    testcases: List["TestCase"] | None = Relationship(back_populates="problem")

    course_problems: List["CourseProblem"] | None = Relationship(back_populates="original_problem")


class ProblemCreate(ProblemBase):
    title: str
    content: str
    start_date: datetime
    end_date: datetime


class CourseProblemCreate(SQLModel):
    start_date: datetime
    end_date: datetime


class CourseProblem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    start_date: datetime
    end_date: datetime
    is_active: bool = False

    problem_id: int | None = Field(default=None, foreign_key="problem.id", nullable=False)
    problem: Problem | None = Relationship(back_populates="course_problems")

    course_id: int | None = Field(default=None, foreign_key="course.id", nullable=False)
    course: Course | None = Relationship(back_populates="problems")
    submissions: List["Submission"] | None = Relationship(back_populates="problem")


class ProblemPublic(ProblemBase):
    id: int


class ProblemsPublic(SQLModel):
    data: List[ProblemPublic]
    count: int


class SubmissionBase(SQLModel):
    source: str
    language: str
    score: float
    create_date: datetime


class SubmissionCreate(SubmissionBase):
    source: str
    language: str


# Database model, database table inferred from class name
class Submission(SubmissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    submitter_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    submitter: User | None = Relationship(back_populates="submissions")

    problem_id: int | None = Field(default=None, foreign_key="courseproblem.id", nullable=False)
    problem: CourseProblem | None = Relationship(back_populates="submissions")


class SubmissionPublic(SubmissionBase):
    id: int
    submitter_id: int
    problem_id: int


class SubmissionsPublic(SQLModel):
    submissions: List[SubmissionPublic]
    count: int


class TestCaseBase(SQLModel):
    input_text: str
    output_text: str


class TestCasesCreate(TestCaseBase):
    input_texts: List[str]   # input이 없으면 None ? 빈문자열?
    output_texts: List[str]


# Database model, database table inferred from class name
class TestCase(TestCaseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    problem_id: int | None = Field(default=None, foreign_key="problem.id", nullable=False)
    problem: Problem | None = Relationship(back_populates="testcases")


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    is_professor: bool


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None
