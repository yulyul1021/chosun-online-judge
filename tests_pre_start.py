from sqlmodel import Session
from app import crud
from app.core.config import settings
from app.core.database import engine
from app.models import UserCreate

PROF_ID_FOR_TEST = "prof1234"
PROF_PW_FOR_TEST = "00000000"
STUDENT_ID_FOR_TEST = "std1234"
STUDENT_PW_FOR_TEST = "00000000"


def create_superuser(session: Session) -> None:
    user = crud.get_user_by_student_id(session=session, student_id=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            student_id=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)


def create_professor(session: Session) -> None:
    user = crud.get_user_by_student_id(session=session, student_id=PROF_ID_FOR_TEST)
    if not user:
        user_in = UserCreate(
            student_id=PROF_ID_FOR_TEST,
            password=PROF_PW_FOR_TEST,
            is_professor=True,
        )
        user = crud.create_user(session=session, user_create=user_in)


def create_student(session: Session) -> None:
    user = crud.get_user_by_student_id(session=session, student_id=STUDENT_ID_FOR_TEST)
    if not user:
        user_in = UserCreate(
            student_id=STUDENT_ID_FOR_TEST,
            password=STUDENT_PW_FOR_TEST,
        )
        user = crud.create_user(session=session, user_create=user_in)


def main():
    with Session(engine) as session:
        create_superuser(session)
        create_professor(session)
        create_student(session)


if __name__ == "__main__":
    main()
