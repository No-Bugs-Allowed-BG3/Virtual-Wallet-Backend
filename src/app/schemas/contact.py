from pydantic import BaseModel, model_validator
from app.persistence.contacts.contact import Contact

class ContactCreate(BaseModel):
    username: str | None = None
    phone:    str | None = None
    email:    str | None = None

    @model_validator(mode="before")
    def exactly_one(cls, values: dict) -> dict:
        non_null = sum(bool(values.get(field)) for field in ("username", "phone", "email"))
        if non_null != 1:
            raise ValueError("Provide exactly one of username, phone or email")
        return values


class ContactResponse(BaseModel):
    username: str
    phone: str
    email: str

    @classmethod
    def create(cls, obj: Contact) -> "ContactResponse":
        return ContactResponse(
            username=obj.contact.username,
            phone=obj.contact.phone,
            email=obj.contact.email
        )