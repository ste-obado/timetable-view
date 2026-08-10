
from fastapi import APIRouter, Depends,HTTPException
from protection import get_current_user, OAuth_Schema
from auth import blacklist_token
from schemas import updateprofile
from models import User
from database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/profile", tags=['User'])

#get user profile
@router.get("/profile/{user_id}")
def get_profile(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    user=db.query(User).filter(User.id==user.id).first()
    if not user:
        HTTPException(status=404,detail="user not found")
    return {"name":user.name,
            "email":user.email,
            "role":user.role,
            "created_at":user.created_at}


#update user update profile
@router.patch("/update_profile")
def update_course( user2:updateprofile, user:User = Depends(get_current_user),
                  db:Session = Depends(get_db)):
    #get user
    user = db.query(User).filter(User.id == user.id ).first()
    if not user:
        raise HTTPException(status_code=404,detail="user not found")
    user.name= user2.name
    user.email=user2.email
    db.commit()
    db.refresh(user)       
    return {"message":"profile updated",'PROFILE':user}


#accoutn log out
@router.post("/logout")
def logout(token: str = Depends(get_current_user)):
    blacklist_token(token)
    return {"message": "Successfully logged out"}


#deleting account 
@router.delete("/account_deletion")
def del_account(user_id:str,token:str=Depends(OAuth_Schema),
                db:Session=(Depends(get_db)),user:User=Depends(get_current_user)):

    if user.role != "admin":
        raise HTTPException(status_code=403,detail="Only admin can delete account")

    del_user= db.query(User).filter(User.id == user_id ).first()
    blacklist_token(token)
    db.delete(del_user)
    db.commit()
    return {"message":"your account is deleted successfully"}