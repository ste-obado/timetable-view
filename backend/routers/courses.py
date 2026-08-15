#user enter course code and course name to enroll in a course
from database import get_db
from models import Course,User,Enrollment
from protection import get_current_user
from schemas import course,CourseUpdate,enroll
from sqlalchemy.orm import Session
from fastapi import  HTTPException,Depends,status,APIRouter

router=APIRouter( prefix="/courses",tags=["Courses"])

@router.post("/add_courses")
def add_course(enroll:course,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403,detail="Only admin can add add courses")
        
    course=Course(Code=enroll.course_code,name=enroll.course_name,Description=enroll.description)
    db.add(course)
    db.commit()
    db.refresh(course)
    return {"message":"Course added successfully"}
     

@router.post("/enroll")
def enroll_course(enroll:enroll,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #check the user role
    if user.role != "Student":
        raise HTTPException(status_code=403,detail="Only users can enroll in courses")
    #check if course exists
    existing_course=db.query(Course).filter(Course.Code==enroll.course_code).first()

    if existing_course is None:
        raise HTTPException(status_code=404,detail="Course does not exist")

    #check if user is already enrolled in the course
    existing_enrollment=db.query(Enrollment).filter(Enrollment.user_id==user.id,
                                                    Enrollment.course_id==existing_course.id).first()
    if existing_enrollment:
            raise HTTPException(status_code=400,detail="User is already enrolled in a course")
        
   # course=Course(Code=enroll.course_code,name=enroll.course_name,Description=enroll.description)
    new_enrollment = Enrollment(user_id=user.id, course_id=existing_course.id)
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return {"message":"Course enrolled successfully"}

#let user get courses they enrolled in
@router.get("/my_courses")
def get_my_courses(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    enrolled_courses=db.query(Course).join(Enrollment).filter(Enrollment.user_id==user.id).all()
    
    return {"courses": enrolled_courses}

#only can get all courses
@router.get("/all_courses")
def get_my_courses(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    courses=db.query(Course).all()
    return {"courses available": courses}



#only addmin can update a course
@router.patch("/update_course/{course_id}")
def update_course(course_id:str, update:CourseUpdate, user:User = Depends(get_current_user),
                  db:Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404,detail="Course not found")
    if user.role!="admin":
          raise HTTPException(status_code=403,detail="Not authorized to update")

    update_data=update.model_dump(exclude_unset=True)
    if 'Code' in update:
        existing_code=db.query(Course).filter(Course.Code==course.Code,Course.id != course.id).first()
        if existing_code:
            raise HTTPException(status=409,detail='Code cannot be duplicate')

    for field,value in update_data.items():
        setattr(course,field,value)
    
    
    db.commit()
    db.refresh(course)       
    return {"message":"course updated","COURSE":course}

#only admin can delete a course
@router.delete("/delete_course/{course_id}")
def del_account(course_id:int,db:Session=(Depends(get_db)),user:User=Depends(get_current_user)):
   
    if user.role != "admin":
        raise HTTPException(status_code=403,detail="Only admin can delete account")
    #get course
    existing_course=db.query(Course).filter(Course.id==course_id).first()
    if existing_course is None:
        raise HTTPException(status_code=404,detail="Course does not exist")
    
    db.delete(existing_course)
    db.commit()
    return {"message":"Course deleted successfully"}

