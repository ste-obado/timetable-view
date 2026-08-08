from pydantic import BaseModel,EmailStr,field_validator,model_validator
from  typing import Optional


class register(BaseModel):
    name:str
    email:EmailStr
    role:str="Student"
    password:str

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

class course(BaseModel):
     course_code:str
     course_name:str
     description:str

class CourseUpdate(BaseModel):
    Code: Optional[str] = None
    name: Optional[str] = None
    Description: Optional[str] = None

class RoomS(BaseModel):
    room_name:str
    capacity:int
    room_code:str

class RoomUpdate(BaseModel):
     room_name: Optional[str] = None
     capacity: Optional[int] = None
     room_code: Optional[int] = None
