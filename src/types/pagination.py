from datetime import datetime
from typing import Literal, Annotated

from pydantic import BaseModel, field_validator, Field

from src.types.validators import StringDictValidator

filter_functions = Literal["eq", "lt", "lte", "gt", "gte", "not", "like", "isnull"]

class Filter[T](
    BaseModel,
):
    filter_field: T
    filter_function: filter_functions
    filter_value: str | int | float | bool | datetime

    @field_validator("filter_value", mode="before")
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                # Try parsing the string as a datetime
                return datetime.fromisoformat(v)
            except ValueError:
                pass  # If it can't be parsed, return it as a string
        return v

class Sort[T](BaseModel):
    sort_field: T | None = None
    sort_order: Literal["asc", "desc"] | None = None

class ListInput[T](BaseModel):
    limit: int | None = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    sort: Annotated[list[Sort[T]] | None, StringDictValidator] = Field(default=None, validate_default=True)
    filter: Annotated[list[Filter[T]] | None, StringDictValidator] = Field(default=None, validate_default=True)

class Pagination[T](BaseModel):
    page: list[T]
    total: int