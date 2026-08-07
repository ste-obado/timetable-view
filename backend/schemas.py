from pydantic import BaseModel,EmailStr,field_validator,model_validator
from  typing import Optional


class register(BaseModel):
    name:str
    email:EmailStr
    role:str="user"
    password:str

    @field_validator("role")
    def role_vallidator(cls,role):
           if role not in [ "admin","user"] :              
                raise ValueError("enter role as admin or user")
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
    