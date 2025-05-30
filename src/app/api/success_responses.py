from fastapi.responses import JSONResponse
from fastapi import status


class CustomSuccessResponse(JSONResponse):
    def __init__(
        self,
        detail: str,
        *,
        status_code: int = status.HTTP_200_OK,
    ):
        payload = {"detail": detail}
        super().__init__(content=payload, status_code=status_code)


class ContactDeleted(CustomSuccessResponse):
    def __init__(self, detail: str = "Contact has been deleted successfully."):
        super().__init__(detail=detail, status_code=status.HTTP_202_ACCEPTED)

class UserBlocked(CustomSuccessResponse):
    def __init__(self, detail: str = "User has been blocked successfully."):
        super().__init__(detail=detail, status_code=status.HTTP_202_ACCEPTED)

class UserUnblocked(CustomSuccessResponse):
    def __init__(self, detail: str = "User has been unblocked successfully."):
        super().__init__(detail=detail, status_code=status.HTTP_202_ACCEPTED)

class CardDeleted(CustomSuccessResponse):
    def __init__(self, detail: str = "Card has been deleted successfully."):
        super().__init__(detail=detail, status_code=status.HTTP_202_ACCEPTED)