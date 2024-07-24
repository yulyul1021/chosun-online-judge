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
    # email: EmailStr | None = Field(unique=True, max_length=255)
    is_professor: bool = False
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    student_id: str
    password: str = Field(min_length=8, max_length=40)
    verify_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    submissions: List["Submission"] | None = Relationship(back_populates="submitter")

    courses_as_professor: List["Course"] | None = Relationship(back_populates="professor")
    courses_as_ta: List["TA"] | None = Relationship(back_populates="ta")
    courses_as_student: List["Student"] | None = Relationship(back_populates="user")


class UserPublic(UserBase):
    id: int
    student_id: str


class CourseBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)


class CourseCreate(CourseBase):
    title: str = Field(min_length=1, max_length=255)
    professor_id: int


class Course(CourseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_active: bool = False

    professor_id: int | None = Field(default=None, foreign_key="user.id")
    professor: User | None = Relationship(back_populates="courses_as_professor")

    tas: List["TA"] | None = Relationship(back_populates="course")
    students: List["Student"] | None = Relationship(back_populates="course")

    problems: List["CourseProblem"] | None = Relationship(back_populates="course")


class CoursePublic(CourseBase):
    id: int
    professor_id: int


class CoursesPublic(SQLModel):
    data: List[CoursePublic]
    count: int


class TA(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    course_id: int | None = Field(default=None, foreign_key="course.id")
    course: Course | None = Relationship(back_populates="tas")

    ta_id: int | None = Field(default=None, foreign_key="user.id")
    ta: User | None = Relationship(back_populates="courses_as_ta")


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    course_id: int | None = Field(default=None, foreign_key="course.id")
    course: Course | None = Relationship(back_populates="students")

    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="courses_as_student")


class ProblemBase(SQLModel):
    title: str
    content: str


class Problem(ProblemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    testcases: List["TestCase"] | None = Relationship(back_populates="problem")

    course_problems: List["CourseProblem"] | None = Relationship(back_populates="problem")


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
    input_texts: List[str]
    output_texts: List[str]


class TestCase(TestCaseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    problem_id: int | None = Field(default=None, foreign_key="problem.id", nullable=False)
    problem: Problem | None = Relationship(back_populates="testcases")


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    is_professor: bool


class TokenPayload(SQLModel):
    sub: int | None = None
