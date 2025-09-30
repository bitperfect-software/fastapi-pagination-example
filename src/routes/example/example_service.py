from typing import ClassVar

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.base import Options

from src.models.example import Example
from src.modules.db.pagination import get_page
from src.modules.db.session import db_session
from src.types.example import ExampleFields, ExampleOut
from src.types.pagination import ListInput, Pagination


class ExampleService:
    query_options: ClassVar[list[Options]] = [joinedload(Example.contact)]

    def __init__(self, db: Session | None = None):
        if db is None:
            self.db = db_session.get()
        else:
            self.db = db

    @classmethod
    def to_out(cls, example: Example) -> ExampleOut:
        return ExampleOut.model_validate(example, from_attributes=True)

    def list(self, list_input: ListInput[ExampleFields]) -> Pagination[ExampleOut]:
        page, total = get_page(Example, list_input, self.query_options)
        return Pagination(total=total, page=[self.to_out(example) for example in page])
