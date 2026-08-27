from database import get_db
from models import User
from auth import hash_password,verify_password,create_access_token
from schemas import register
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import  HTTPException,Depends,Request
from redis_client import redis_client



from fastapi import APIRouter


router=APIRouter( prefix="/auth",tags=['Authentication'])



#CREATING USER ACCOUNT

@router.post("/register")
def register_user(newuser:register,db:Session=(Depends(get_db))):
    #if user exists
    existing_user=db.query(User).filter(User.email==newuser.email).first()
    if existing_user:
        raise HTTPException(status_code=404,detail='USER EXIXTS')
    #create user

    #print(newuser.password)
    #print(type(newuser.password))
    #print(len(newuser.password))
    password=hash_password(newuser.password)
    db_newuser=User(name=newuser.name,email=newuser.email,role=newuser.role,password=password)
    db.add(db_newuser)
    db.commit()
    db.refresh(db_newuser)
    return {"message":"signup successfully"}

#user--login
@router.post("/login")
def login_user(request:Request,form_data:OAuth2PasswordRequestForm=Depends()
               ,db:Session=(Depends(get_db))):

    #create a key in redis 
    rate_key=f"login_attemps:{form_data.username}"
    attempts = redis_client.get(rate_key)
    if attempts and int(attempts) >= 5:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Try again in a minute."
        )
    existing_user = db.query(User).filter(User.email == form_data.username).first()
  
    if not existing_user or not verify_password(form_data.password, existing_user.password):
    # Failed attempt — increment the counter
        new_count = redis_client.incr(rate_key)
        if new_count == 1:
              redis_client.expire(rate_key, 60)  # only set TTL on the first failure,more than 5 failures in that ttl window "too many requests"
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Successful login — clear any failed attempt count
    redis_client.delete(rate_key)

    #create access_token
    token_data=({"sub":str(existing_user.id)})
    token=create_access_token(token_data)

    return {"access_token": token,
            "token_type":"bearer"}







    

