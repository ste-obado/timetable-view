from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta
from fastapi import HTTPException,status
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCSESS_TOKEN_EXPIRE_MINUTES"))



pwt_Context=CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Could not validate credentials",
                                    headers={"WWW-Authenticate":"Bearer"})

def hash_password(password:str):
    return pwt_Context.hash(password)

def verify_password(password:str, hashed_password:str):
    return pwt_Context.verify(password,hashed_password)

def create_access_token(data:dict)-> str:
    encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp":expire})
    token=jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)
    return token



def verify_access_token(token:str)-> dict:
    try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

       return payload
    except JWTError:
        return credentials_exception

blacklist=set()

def is_token_blacklisted(token: str) -> bool:
    return token in blacklist

def blacklist_token(token:str):
    blacklist.add(token)
