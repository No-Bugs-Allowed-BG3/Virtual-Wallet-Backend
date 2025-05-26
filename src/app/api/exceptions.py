from fastapi import HTTPException

USER_NOT_FOUND = HTTPException(
    status_code=404,detail="User not found!"
)

USER_UNAUTHORIZED = HTTPException(
    status_code=401,detail="Unauthorized access! You don't have sufficient rights to access this page!"
)

USER_VERIFICATION_ERROR = HTTPException(
    status_code=400,detail="An error occured during verification. User not found / login expired or other error. Please contact an administrator"
)

USER_ACTIVATION_ERROR = HTTPException(
    status_code=400,detail="An error occured during activation. User not found / login expired or other error. Please contact an administrator"
)

PASSWORD_INCORRECT_FORMAT = HTTPException(
    status_code=422,detail="Password must contain at least 8 characters, with at least one UPPERCASE character, one DIGIT and one SPECIAL character"
)

USERNAME_INCORRECT_FORMAT = HTTPException(
    status_code=422,detail="Username must be between 2 and 20 characters!"
)

USER_ALREADY_EXISTS_EXCEPTION = HTTPException(
    status_code=400,detail="An user with this username and/or e-mail already exists!"
)