# from datetime import datetime, timedelta
# from typing import Optional
# import os
# import jwt
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from pydantic import BaseModel

# # In production, make sure to use a strong secret key and store it securely.
# SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Fake users database for demonstration.
# # In a real app, you'll query your database.
# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "hashed_password": "fakehashedsecret",  # This should be a properly hashed password.
#         "disabled": False,
#     }
# }

# def fake_hash_password(password: str) -> str:
#     return "fakehashed" + password

# # Pydantic models for token and user data.
# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: Optional[str] = None

# class User(BaseModel):
#     username: str
#     full_name: Optional[str] = None
#     disabled: Optional[bool] = None

# class UserInDB(User):
#     hashed_password: str

# def get_user(db, username: str) -> Optional[UserInDB]:
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)
#     return None

# def authenticate_user(fake_db, username: str, password: str) -> Optional[UserInDB]:
#     user = get_user(fake_db, username)
#     if not user:
#         return None
#     if user.hashed_password != fake_hash_password(password):
#         return None
#     return user

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     to_encode = data.copy()
#     if expires_delta:
#          expire = datetime.utcnow() + expires_delta
#     else:
#          expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
#     credentials_exception = HTTPException(
#          status_code=status.HTTP_401_UNAUTHORIZED,
#          detail="Could not validate credentials",
#          headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#          payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#          username: str = payload.get("sub")
#          if username is None:
#              raise credentials_exception
#          token_data = TokenData(username=username)
#     except jwt.PyJWTError:
#          raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#          raise credentials_exception
#     return user

# async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
#     if current_user.disabled:
#          raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user



import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
import moudles as models
from moudles import TokenData

from dotenv import load_dotenv
load_dotenv()

# Read secret settings from environment variables (or provide defaults)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Could not validate credentials",
         headers={"WWW-Authenticate": "Bearer"},
    )
    try:
         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
         username: str = payload.get("sub")
         if username is None:
             raise credentials_exception
         token_data = TokenData(username=username)
    except JWTError:
         raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
         raise credentials_exception
    return user

def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
         raise HTTPException(status_code=400, detail="Inactive user")
    return current_user