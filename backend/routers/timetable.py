#admin add time slot to the database----no confilct of classrooms and time
#admin delete time slot from the database
#admin update time slot in the database
#the user and lecturere can view the time slot in the database

from database import get_db
from models import Course,User,Enrollment,TimeSlot,Room
from protection import get_current_user
from schemas import timeslot,timeupdate
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import  HTTPException,Depends,status,APIRouter


router=APIRouter( prefix="/timetable",tags=["TimeSlots"])

@router.post("/add_timeslot")
def enroll_course(time:timeslot,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #check the user role
    if user.role != "admin":
        raise HTTPException(status_code=403,detail="not authorized")
    #check if course exists
    existing_course=db.query(Course).filter(Course.id==time.course_id).first()

    if existing_course is None:
        raise HTTPException(status_code=404,detail="Course does not exist")

    #check if room is in use at that particular time
    existing_room_slot = db.query(TimeSlot).filter(
    TimeSlot.room_id == time.room_id,
    TimeSlot.day == time.day,
    TimeSlot.start_time < time.end_time,
    TimeSlot.end_time > time.start_time).first()

    if existing_room_slot:
      raise HTTPException(
        status_code=409,
        detail="Room is already occupied during this period"
    )
 
    #lecture clash
    existing_lec = db.query(TimeSlot).filter(
    TimeSlot.lecturer_id == time.lecturer_id,
    TimeSlot.day == time.day,
    TimeSlot.start_time < time.end_time,
    TimeSlot.end_time > time.start_time).first()

    if existing_lec:
       raise HTTPException(
        status_code=409,
        detail="Lecturer already has a class during this period"
    )
  

        
    time_slot = TimeSlot(
        course_id=time.course_id,
        room_id=time.room_id,
        lecturer_id=time.lecturer_id,
        Day=time.day,
        start_time=time.start_time,
        End_time=time.End_time,
        Academic_yr=time.Academic_yr,
        created_by=time.created_by,
    )
    db.add(time_slot)
    db.commit()
    db.refresh(time_slot)
    return {"message":"timeslot added successfully"}

#let student get timeslot 
@router.get("/timetable/student/week")
def get_my_courses(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    #check if the user is a Student
    if user.role!='Student':
        HTTPException(status=404,details="Not authorized")

    #check if the user is enrolled and get the enrolled courses in timeslot
    timeslot=db.query(TimeSlot).join(Enrollment,Enrollment.course_id==TimeSlot.course_id).filter(Enrollment.user_id==user.id).all()
    if not timeslot:
        raise HTTPException(status=404,details="no timeslot found")

    return {"id": timeslot.user_id,
             "Day":timeslot.Day,
             "start_tim": timeslot.start_time ,
             "End_time" :timeslot.End_time ,
             "Semester " : timeslot.Semester,  
             "Academic_yr": timeslot.Academic_yr,
             "created_by"  : timeslot.created_by }

#let Lecturer get timeslot 
@router.get("timetable/lecturer/week")
def get_my_courses(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    #check if the user is a Student
    if user.role!='lecturer':
        raise HTTPException(status=404,detail="Not authorized")

    #check the lesson for lecs
    timeslot=db.query(TimeSlot).filter(TimeSlot.lecturer_id==user.id).all()
    if not timeslot:
        raise HTTPException(status=404,details="No timeslot found")

    return {"id": timeslot.user_id,
             "Day":timeslot.Day,
             "start_tim": timeslot.start_time ,
             "End_time" :timeslot.End_time ,
             "Semester " : timeslot.Semester,  
             "Academic_yr": timeslot.Academic_yr,
             "created_by"  : timeslot.created_by }
                

#only addmin can update a timeslot
@router.patch("/update_slot/{timeslot_id}")
def update_course(timeslot_id:str, timeslot:timeupdate, user:User = Depends(get_current_user),
                  db:Session = Depends(get_db)):
    #get timeslot
    time= db.query(TimeSlot).filter(TimeSlot.id == timeslot_id).first()
    if not time:
        raise HTTPException(status_code=404,detail="timeslot not found")
    elif user.role!="admin":
          raise HTTPException(status_code=403,detail="Not authorized to update")
    else:
        time.room_id = timeslot.room_id
        time.start_time = timeslot.start_time
        time.end_time = timeslot.end_time
        time.lecturer_id=timeslot.lecture_id
        time.course_id=timeslot.course_id
        time.Semester=timeslot.Semester
        db.commit()
        db.refresh(time)       
        return {"message":"course updated","COURSE":time}

#only admin can delete a timeslot
@router.delete("/delete_slot/{TimeSlot_id}")
def del_account(timeslot_id:str,db:Session=(Depends(get_db)),user:User=Depends(get_current_user)):
   
    if user.role != "admin":
        raise HTTPException(status_code=403,detail="not authorized")
    #get course
    existing_slot=db.query(TimeSlot).filter(TimeSlot.id==timeslot_id).first()
    if existing_slot is None:
        raise HTTPException(status_code=404,detail="timeslot does not exist")
    
    db.delete(existing_slot)
    db.commit()
    return {"message":"TimeSlot deleted successfully"}

