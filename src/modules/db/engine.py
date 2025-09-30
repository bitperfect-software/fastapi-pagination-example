from sqlmodel import Session, create_engine

from src.modules.db.session import db_session
from src.settings import settings

engine = create_engine(settings.database_url)


async def get_session():
    with Session(engine) as session:
        token = db_session.set(session)
        yield session
    db_session.reset(token)
