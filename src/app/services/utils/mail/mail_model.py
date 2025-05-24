from pydantic import BaseModel,EmailStr
from typing import List
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class MailAddress(BaseModel):
    Email:EmailStr
    Name:str

class MailMessage(BaseModel):
    From:MailAddress
    To:List[MailAddress]
    Subject:str
    TextPart:str
    HTMLPart:str

class ActivationMailMessage(MailMessage):

    @classmethod
    def fill_data(cls,
                  to_email:EmailStr,
                  to_username:str
                  ):
        print(getenv("ACCOUNT_VERIFICATION_SUBJECT"))
        print(getenv("MAILJET_API_KEY"))
        return cls(
            From = MailAddress(
                Email=getenv("MAILJET_SENDER_EMAIL"),
                Name=getenv("MAILJET_SENDER_NAME")),
            To = [MailAddress(Email=to_email,Name=to_username)],
            Subject = getenv("ACCOUNT_VERIFICATION_SUBJECT"),
            TextPart = f"{getenv("ACCOUNT_VERIFICATION_TEXT")}{getenv("ACCOUNT_VERIFICATION_LINK")}{to_username}",
            HTMLPart = f"{getenv("ACCOUNT_VERIFICATION_TEXT")}<a href='{getenv("ACCOUNT_VERIFICATION_LINK")}{to_username}'>Activation Link</a>"
        )

class ActivationMessagesList(BaseModel):
    Messages:List[ActivationMailMessage]