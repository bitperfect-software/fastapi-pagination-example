from contextvars import ContextVar

from sqlmodel import Session

db_session: ContextVar[Session] = ContextVar("db_session")
