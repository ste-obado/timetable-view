from database import get_db
from models import User
from auth import hash_password,verify_password,create_access_token
from schemas import register
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import  HTTPException,Depends,status



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
def login_user(form_data:OAuth2PasswordRequestForm=Depends()
               ,db:Session=(Depends(get_db))):
    existing_user = db.query(User).filter(User.email == form_data.username).first()

    #validate if user does exist
    if not existing_user:
        raise HTTPException(status_code=404,detail='USER DONT EXIST')
    #verify password 
    if not verify_password(form_data.password, existing_user.password):
        raise HTTPException(status_code=404,detail='INVALID PASSWORD')

    #create access_token
    token_data=({"sub":str(existing_user.id)})
    token=create_access_token(token_data)

    return {"access_token": token,
            "token_type":"bearer"}







    

