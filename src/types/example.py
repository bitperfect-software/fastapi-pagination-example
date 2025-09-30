from enum import Enum

from pydantic import BaseModel


class ContactInfoOut(BaseModel):
    id: str
    name: str
    email: str
    phone: str


class ExampleOut(BaseModel):
    id: int
    contact: ContactInfoOut


class ExampleFields(str, Enum):
    id = "id"
    name = "contact.name"
    email = "contact.email"
    phone = "contact.phone"
