from app.services.utils.mail.mail_model import ActivationMessagesList,ActivationMailMessage
from mailjet_rest import Client
from os import getenv

async def send_activation_mail(to_email:str,
                               to_username:str,
                               to_user_id:str)->bool:
    mailjet = Client(
        auth=(getenv("MAILJET_API_KEY"),getenv("MAILJET_SECRET_KEY")),
        version="v3.1"
    )
    mail_obj = ActivationMailMessage.fill_data(
        to_email=to_email,
        to_username=to_username,
        to_user_id=to_user_id
    )

    mail_data = ActivationMessagesList(Messages=[mail_obj]).model_dump()
    result = mailjet.send.create(data=mail_data)
    if not result.status_code == 200:
        return False
    return True