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