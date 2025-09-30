from typing import Annotated

from fastapi import APIRouter, Query

from src.types.example import ExampleFields, ExampleOut
from src.types.pagination import ListInput, Pagination

from .example_service import ExampleService

router = APIRouter(prefix="/example", tags=["example"])


@router.get(
    "/",
    response_model=Pagination[ExampleOut],
)
def list_examples(
    list_input: Annotated[ListInput[ExampleFields], Query()],
):
    return ExampleService().list(list_input)
