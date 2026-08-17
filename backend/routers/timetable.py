#admin add time slot to the database----no confilct of classrooms and time
#admin delete time slot from the database
#admin update time slot in the database
#the user and lecturere can view the time slot in the database

from database import get_db
from models import Course, User, Enrollment, TimeSlot, Room
from protection import get_current_user
from schemas import timeslot, timeupdate
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, Depends, status, APIRouter,Request,Response
import hashlib
import json
from redis_client import redis_client


router = APIRouter(prefix="/timetable", tags=["TimeSlots"])


@router.post("/add_timeslot")
def add_timeslots(time: timeslot, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="not authorized")

    existing_course = db.query(Course).filter(Course.id == time.course_id).first()
    if existing_course is None:
        raise HTTPException(status_code=404, detail="Course does not exist")

    existing_room_slot = db.query(TimeSlot).filter(
        TimeSlot.room_id == time.room_id,
        TimeSlot.Day == time.day,
        TimeSlot.start_time < time.end_time,
        TimeSlot.End_time > time.start_time
    ).first()
    if existing_room_slot:
        raise HTTPException(status_code=409, detail="Room is already occupied during this period")

    existing_lec = db.query(TimeSlot).filter(
        TimeSlot.lecturer_id == time.lecturer_id,
        TimeSlot.Day == time.day,
        TimeSlot.start_time < time.end_time,
        TimeSlot.End_time > time.start_time
    ).first()
    if existing_lec:
        raise HTTPException(status_code=409, detail="Lecturer already has a class during this period")

    time_slot = TimeSlot(
        course_id=time.course_id,
        room_id=time.room_id,
        lecturer_id=time.lecturer_id,
        Day=time.day,
        start_time=time.start_time,
        End_time=time.end_time,
        Academic_yr=time.Academic_yr,
        created_by=time.created_by,
    )
    db.add(time_slot)
    db.commit()
    db.refresh(time_slot)
    return {"message": "timeslot added successfully"}


@router.get("/timetable/student/week")
def get_student_weekly_timetable(request:Request,response:Response,user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "Student":
        raise HTTPException(status_code=403, detail="Not authorized")

    slots = (
        db.query(TimeSlot)
        .join(Enrollment, Enrollment.course_id == TimeSlot.course_id)
        .filter(Enrollment.user_id == user.id)
        .all()
    )
    if not slots:
        raise HTTPException(status_code=404, detail="No timeslot found")

    payload= [
            {
                "id": slot.id,
                "Day": slot.Day,
                "start_time": slot.start_time.isoformat(),
                "End_time": slot.End_time.isoformat(),
                "Semester": slot.Semester,
                "Academic_yr": slot.Academic_yr,
                "created_by": slot.created_by,
            }
            for slot in slots
        ]
    
    #fingerprint the response data(change payload to a json and sort it alphabetic then encode &
    #  hash it to etag)
    encode_byte=json.dumps(payload,sort_keys=True).encode()
    etag=hashlib.md5(encode_byte).hexdigest()

    if request.headers.get("if-non-match")==etag:
        return Response(status_code=304)

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=30"
    return {"timeslots": payload}

#@router.get("/timetable/lecturer/week")
#def get_lecturer_weekly_timetable(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
 #   if user.role != "lecturer":
  #      raise HTTPException(status_code=403, detail="Not authorized")

   # slots = db.query(TimeSlot).filter(TimeSlot.lecturer_id == user.id).all()
    #if not slots:
     #   raise HTTPException(status_code=404, detail="No timeslot found")

    #return {
     #   "timeslots": [
      #      {
       #         "id": slot.id,
        #        "Day": slot.Day,
         #       "start_time": slot.start_time,
          #      "End_time": slot.End_time,
           #     "Semester": slot.Semester,
            #    "Academic_yr": slot.Academic_yr,
             #   "created_by": slot.created_by,
            #}
            #for slot in slots
        #]
    #}

@router.get("/timetable/lecturer/week")
def get_lecturer_weekly_timetable(
    request: Request,
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role != "lecturer":
        raise HTTPException(status_code=403, detail="Not authorized")

    cache_key = f"lecturer_timetable:{user.id}"

    # 1. Check Redis first
    cached = redis_client.get(cache_key)
    if cached:
        return {"timeslots": json.loads(cached), "source": "cache"}

    # 2. Cache miss — hit the DB like normal
    slots = db.query(TimeSlot).filter(TimeSlot.lecturer_id == user.id).all()
    if not slots:
        raise HTTPException(status_code=404, detail="No timeslot found")

    payload = [
        {
            "id": slot.id,
            "Day": slot.Day,
            "start_time": slot.start_time.isoformat(),
            "End_time": slot.End_time.isoformat(),
            "Semester": slot.Semester,
            "Academic_yr": slot.Academic_yr,
            "created_by": slot.created_by,
        }
        for slot in slots
    ]

    # 3. Write to Redis for next time, expire after 60 seconds
    redis_client.set(cache_key, json.dumps(payload), ex=60)

    return {"timeslots": payload, "source": "db"}


@router.patch("/update_slot/{timeslot_id}")
def update_timeslot(
    timeslot_id: str,
    payload: timeupdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update")

    time_slot = db.query(TimeSlot).filter(TimeSlot.id == timeslot_id).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="timeslot not found")

    update_data = payload.model_dump(exclude_unset=True)

    # schema field -> actual model attribute name (case differs on this one)
    if "end_time" in update_data:
        update_data["End_time"] = update_data.pop("end_time")

    for field, value in update_data.items():
        setattr(time_slot, field, value)

    db.commit()
    db.refresh(time_slot)
    return {"message": "timeslot updated", "COURSE": time_slot}


@router.delete("/delete_slot/{timeslot_id}")
def delete_timeslot(timeslot_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="not authorized")

    existing_slot = db.query(TimeSlot).filter(TimeSlot.id == timeslot_id).first()
    if existing_slot is None:
        raise HTTPException(status_code=404, detail="timeslot does not exist")

    db.delete(existing_slot)
    db.commit()
    return {"message": "TimeSlot deleted successfully"}