#admin adds room name and capacity to the database
#user enter course code and course name to enroll in a course
from database import get_db
from models import Room,User
from protection import get_current_user
from schemas import Rooms,RoomUpdate
from sqlalchemy.orm import Session

from fastapi import  HTTPException,Depends,status,APIRouter

router=APIRouter( prefix="/room",tags=["Rooms"])

@router.post("/add_room")
def add_room(room:Rooms,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #check the user role
    if user.role != "admin":
        raise HTTPException(status_code=403,detail="not authorized")
    #check if room exists
    existing_room=db.query(Room).filter(Room.Code==room.room_code).first()

    if existing_room :
        raise HTTPException(status_code=404,detail="Room exist")

    room=Room(room_name=room.room_name,capacity=room.capacity,Code=room.room_code)
    db.add(room)
    db.commit()
    db.refresh(room)
    return {"message":"Room added"}

#let user get room that exist
@router.get("/available_rooms/{user_id}")
def get_rooms(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    existing_rooms=db.query(Room).all()
    return {"courses":existing_rooms }


#only admin can update a course
@router.patch("/update_room/{course_id}")
def update_course(room_id:str, room2:RoomUpdate, user:User = Depends(get_current_user),
                  db:Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404,detail="room not found")
    if user.role!="admin":
          raise HTTPException(status_code=403,detail="Not authorized to update")
    room.room_name=room2.room_name
    room.capacity=room2.capacity
    room.room_code=room2.room_code
    db.commit()
    db.refresh(room)       
    return {"message":"room updated","ROOM":room}