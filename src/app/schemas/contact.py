from pydantic import BaseModel
from app.persistence.contacts.contact import Contact

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