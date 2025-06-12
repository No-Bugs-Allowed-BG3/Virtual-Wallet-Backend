from fastapi import HTTPException, status

class CustomException(HTTPException):
    def __init__(
            self,
            detail: str,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.detail=detail
        self.status_code=status_code

class UserNotFound(CustomException):
    def __init__(self, detail: str = "User not found!"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class TransactionNotFound(CustomException):
    def __init__(self, detail: str = "Transaction not found!"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class UserUnauthorized(CustomException):
    def __init__(self, detail: str = "Unauthorized access! You don't have sufficient rights to access this page!"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class UserVerificationError(CustomException):
    def __init__(self, detail: str = "An error occured during verification. User not found / login expired or other error. Please contact an administrator"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

class UserActivationError(CustomException):
    def __init__(self, detail: str = "An error occured during activation. User not found / login expired or other error. Please contact an administrator"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

class PasswordIncorrectFormat(CustomException):
    def __init__(self, detail: str = "Password must contain at least 8 characters, with at least one UPPERCASE character, one DIGIT and one SPECIAL character"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class PINIncorrectFormat(CustomException):
    def __init__(self, detail: str = "User PIN is with incorrect format!"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class UsernameIncorrectFormat(CustomException):
    def __init__(self, detail: str = "Username must be between 2 and 20 characters!"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class UserAlreadyExists(CustomException):
    def __init__(self, detail: str = "An user with this username and/or e-mail already exists!"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

class CardNotFound(CustomException):
    def __init__(self, detail: str = "A card with this number could not be found."):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class NoCards(CustomException):
    def __init__(self, detail: str = "No registered cards."):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class CardAlreadyExists(CustomException):
    def __init__(self, detail: str = "A card with this number has already been registered."):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)

class BalanceNotFound(CustomException):
    def __init__(self, detail: str = "No wallet balances found for this user."):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class CurrencyNotFound(CustomException):
    def __init__(self, detail: str = "The virtual wallet does not support this currency."):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class BalanceAlreadyExists(CustomException):
    def __init__(self, detail: str = "A balance in this currency has already been registered."):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)

class ContactNotFound(CustomException):
    def __init__(self, detail: str = "No contact found."):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class ContactAlreadyExists(CustomException):
    def __init__(self, detail: str = "Contact has already been added."):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)