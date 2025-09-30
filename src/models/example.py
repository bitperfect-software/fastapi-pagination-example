from sqlmodel import Field, Relationship, SQLModel


class ContactInfo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str

    example_id: int = Field(default=None, foreign_key="example.id")
    example: "Example" = Relationship(back_populates="contact")


class Example(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    contact: ContactInfo = Relationship(back_populates="example")
