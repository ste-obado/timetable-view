
from fastapi import APIRouter, Depends
from protection import get_current_user, OAuth_Schema, blacklist_token
from models import User
from database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/profile", tags=['User'])

#get user profile
@router.get("/profile/{user.id}")
def get_profile(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return {"name":user.name,
            "email":user.email,
            "role":user.role,
            "created_at":user.created_at}


#update user update profile
#accoutn log out
@router.post("/logout")
def logout(token: str = Depends(get_current_user)):
    blacklist_token(token)
    return {"message": "Successfully logged out"}


#deleting account 
@router.delete("/account_deletion")
def del_account(token:str=Depends(OAuth_Schema),
                db:Session=(Depends(get_db)),user:User=Depends(get_current_user)):
    del_user=user
    blacklist_token(token)
    db.delete(del_user)
    db.commit()
    return {"message":"your account is deleted successfully"}