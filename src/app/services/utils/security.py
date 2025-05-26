import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password=plain_password.encode('utf-8'),
        hashed_password=hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    password_salt = bcrypt.gensalt(14)
    return bcrypt.hashpw(
        password.encode('utf-8'),
        password_salt
    ).decode('utf-8')
