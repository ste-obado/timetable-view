from fastapi import FastAPI
#from routers import users,timetables,courses,authentication 
from database import Base,engine
import models


#creating tables 
models.Base.metadata.create_all(bind=engine)

app=FastAPI()

#include each router 
#app.include_router(users.router)
#app.include_router(timetables.router)
#app.include_router(courses.router)
#app.include_router(authentication.router)
