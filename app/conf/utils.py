from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def bcrypt_hash(password: str):
    return password_context.hash(password)

def verify(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)


SECRET_KEY = "d450647aaac9d2f98bb444d4b4592d23b74211fa1f238f8ab6f6bc24aacd11a1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
