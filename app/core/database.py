from sqlmodel import create_engine, Session, select
from .config import settings
from .. import crud
from ..models import User, UserCreate

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


def init_db(session: Session) -> None:

    user = session.exec(
        select(User).where(User.student_id == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            student_id=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)