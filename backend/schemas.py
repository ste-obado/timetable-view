from pydantic import BaseModel,EmailStr,field_validator,model_validator
from  typing import Optional
from datetime import time 


class register(BaseModel):
    name:str
    email:EmailStr
    role:str="Student"
    password:str
    confirm_password:str

    @field_validator("role")
    def role_vallidator(cls,role):
           if role not in [ "admin","Student","lecturer"] :              
                raise ValueError("enter role as admin, Student or lecturer")
           return role


    @field_validator("password")
    def validate_password(cls,password):
        if len(password)<8:
            raise ValueError("Password must be at least 8 characters long")
        return password
    
    @model_validator(mode="after")
    def password_verify(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class updateprofile(BaseModel):
     name: Optional[str] = None
     email:Optional[EmailStr] = None
   

class course(BaseModel):
     course_code:str
     course_name:str
     description:str

class enroll(BaseModel):
     course_code:str
    
class CourseUpdate(BaseModel):
    Code: Optional[str] = None
    name: Optional[str] = None
    Description: Optional[str] = None

class Rooms(BaseModel):
    room_name:str
    capacity:int
    room_code:str

class RoomUpdate(BaseModel):
     room_name: Optional[str] = None
     capacity: Optional[int] = None
     room_code: Optional[str] = None


class timeslot(BaseModel):
     course_id:int
     room_id:int
     lecturer_id:str
     day:str
     start_time:time
     end_time:time
     Semester:str
     Academic_yr:str
     created_by:str



class timeupdate(BaseModel):
     course_id:Optional[str] = None
     room_id:Optional[str] = None
     lecturer_id:Optional[str] = None
     day :Optional[str] = None
     start_time : Optional[time] = None
     end_time : Optional[time] = None
     Semester  :Optional[str] = None
     Academic_yr : Optional[str] = None
     created_by :  Optional[str] = None


     
    


