from database import Base
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import String,Column,ForeignKey,Integer,DateTime,TIMESTAMP,func,Enum,Boolean
from datetime import timezone,datetime



class User(Base):
     __tablename__ ="user"

     id=Column(String(200),primary_key=True,default=lambda:str(uuid.uuid4()))
     name=Column(String(200),nullable=False)
     email=Column(String(200),nullable=False)
     password=Column(String(200),nullable=False)
     role=Column(Enum("admin", "user","lecturer", name="user_roles"),
                 default="user",nullable=False)
     created_at=Column(TIMESTAMP,server_default=func.now())

     post=relationship("Posts",back_populates="user",cascade="all, delete-orphan")
     coment=relationship("Comments",back_populates="user",cascade="all, delete-orphan")
     like=relationship("Likes",back_populates="user",cascade="all, delete-orphan")

     #Using checkcontarint function
     #__table_args__ = (
    #CheckConstraint(
     #   "role IN ('admin', 'user')",
      #  name="check_user_role"
    #),)
class Enrollment(Base):
    __tablename__ ="enrollments"

    id=Column(String(200),primary_key=True,default=lambda:str(uuid.uuid4()))
    user_id=Column(String(200),ForeignKey("users.id"))
    course_id=Column(String(200),ForeignKey("courses.id"))
    

class Course(Base):
    __tablename__ ="courses"

    id=Column(String(200),primary_key=True,default=lambda:str(uuid.uuid4()))
    Code=Column(String(50),nullable=False)
    name=Column(String(100),nullable=False)
    Description=Column(String(100),nullable=False)
    created_at=Column(TIMESTAMP,server_default=func.now())
    #user can set his posting time

    posting_time=Column(DateTime,default=lambda:datetime.now(timezone.utc))
    owner_id=Column(String(200),ForeignKey("user.id"))
    user=relationship("User",back_populates="post")
    like=relationship("Likes",back_populates="post",cascade="all, delete-orphan")
    coment=relationship("Comments",back_populates="post",cascade="all, delete-orphan")

class Room(Base):
    __tablename__ ="rooms"

    id=Column(Integer,primary_key=True)
    room_name=Column(String(200),nullable=False)
    capacity=Column(Integer,nullable=False)
    Code=Column(String(50),nullable=False)

    #comment_id=Column(String(20),ForeignKey("Comment.id"))
    user_id=Column(String(200),ForeignKey("user.id"))
    post=relationship("Posts",back_populates="like")
    #coment=relationship("comment",back_populates="Like")
    user=relationship("User",back_populates="like")


class TimeSlot(Base):
    __tablename__ ="time_slots"

    id=Column(Integer,primary_key=True)
    name=Column(String(20))
    comment=Column(String(200))
    course_id=Column(String(200),ForeignKey("courses.id"))
    lecturer_id=Column(String(200),ForeignKey("users.id"))
    room_id=Column(Integer,ForeignKey("rooms.id"))
    Day=Column(String(20))
    start_time=Column(String(20))
    End_time=Column(String(20))
    Semester=Column(String(20))
    Academic_yr=Column(String(20))
    created_by=Column(String(200),ForeignKey("user.id"))
    created_at=Column(TIMESTAMP,server_default=func.now())
    updated_at=Column(TIMESTAMP,server_default=func.now())

    user_id=Column(String(200),ForeignKey("user.id"))
    post=relationship("Posts",back_populates="coment")
    user=relationship("User",back_populates="coment")


class Notification(Base):
    __tablename__ ="notifications"

    id=Column(String(200),primary_key=True,default=lambda:str(uuid.uuid4()))
    user_id=Column(String(200),ForeignKey("users.id"))
    title=Column(String(100),nullable=False)
    message=Column(String(100),nullable=False)
    is_read=Column(Boolean,default=False)
    created_at=Column(TIMESTAMP,server_default=func.now())
