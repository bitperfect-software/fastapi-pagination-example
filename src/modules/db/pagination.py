from collections.abc import Sequence
from typing import Any

from sqlalchemy import ColumnElement, Select, func
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql._typing import _ColumnExpressionArgument, _ColumnExpressionOrStrLabelArgument
from sqlalchemy.sql.base import Options
from sqlmodel import SQLModel, asc, desc, select

from src.modules.db.session import db_session
from src.types.pagination import ListInput

Where = _ColumnExpressionArgument[bool] | bool
OrderBy = _ColumnExpressionOrStrLabelArgument[Any]

filter_functions_map = {
    "eq": lambda col, val: col == val,
    "not": lambda col, val: col != val,
    "lt": lambda col, val: col < val,
    "lte": lambda col, val: col <= val,
    "gt": lambda col, val: col > val,
    "gte": lambda col, val: col >= val,
    "like": lambda col, val: col.ilike(f"%{val}%"),
    "isnull": lambda col, val: col.is_(None) if val else col.is_not(None),
}


def apply_joins(statement: Select, model: type[SQLModel], filter_and_sort_fields: list[str]) -> Select:
    joined = set()
    current_path = []

    for field in filter_and_sort_fields:
        parts = field.split(".")
        if len(parts) < 2:
            continue  # Not a relationship field

        current_model = model
        current_path.clear()
        for part in parts[:-1]:  # all but last part are relationships
            current_path.append(part)
            path_str = ".".join(current_path)

            if path_str in joined:
                continue

            relationship_attr = getattr(current_model, part, None)
            if relationship_attr is None:
                break

            rel_prop = getattr(relationship_attr, "property", None)
            if not isinstance(rel_prop, RelationshipProperty):
                break

            statement = statement.join(relationship_attr)
            joined.add(path_str)
            current_model = rel_prop.mapper.class_

    return statement


def resolve_column(model: type, path: str) -> ColumnElement | None:
    parts = path.split(".")
    attr = getattr(model, parts[0], None)

    for part in parts[1:]:
        if attr is None:
            return None
        attr = getattr(attr.property.mapper.class_, part, None)

    return attr


def add_order_by[T](model: type[T], list_input: ListInput) -> list[OrderBy]:
    order_bys = []
    if list_input.sort:
        for sort in list_input.sort:
            if sort.sort_field:
                column = resolve_column(model, sort.sort_field)
                if column is not None:
                    order_clause = asc(column) if sort.sort_order == "asc" else desc(column)
                    order_bys.append(order_clause)
    return order_bys


def add_filter[T](model: type[T], list_input: ListInput) -> list[Where]:
    wheres = []
    if list_input.filter is not None:
        for filter_in in list_input.filter:
            if filter_in.filter_field and filter_in.filter_function and filter_in.filter_value is not None:
                column = resolve_column(model, filter_in.filter_field)
                if column is not None and filter_in.filter_function in filter_functions_map:
                    clause = filter_functions_map[filter_in.filter_function](column, filter_in.filter_value)
                    wheres.append(clause)
    return wheres


def get_where_and_sort[T](model: type[T], list_input: ListInput) -> tuple[list[Where], list[OrderBy]]:
    wheres: list[Where] = add_filter(model, list_input)
    sort: list[OrderBy] = add_order_by(model, list_input)
    return wheres, sort


def get_total(statement: Select) -> int:
    session = db_session.get()
    count_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    return session.exec(count_statement).one()


def get_page[T](model: type[T], list_input: ListInput, options: list[Options] | None = None) -> tuple[Sequence[T], int]:
    session = db_session.get()
    wheres, sorts = get_where_and_sort(model, list_input)

    filter_and_sort_fields = list(
        set(
            [f.filter_field for f in list_input.filter or [] if f.filter_field and "." in f.filter_field]
            + [s.sort_field for s in list_input.sort or [] if s.sort_field and "." in s.sort_field]
        )
    )

    statement = select(model)
    statement = apply_joins(statement, model, filter_and_sort_fields)

    if wheres:
        statement = statement.where(*wheres)
    if sorts:
        statement = statement.order_by(*sorts)

    total = get_total(statement)

    # options are initial joins to prevent lazy loading sub-tables they are not needed for the total query
    if options:
        statement = statement.options(*options)

    statement = statement.offset(list_input.offset).limit(list_input.limit)
    rows = session.exec(statement).all()
    return rows, total
