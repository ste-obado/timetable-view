from fastapi import FastAPI
#from routers 
from database import Base,engine
import models


#creating tables 
models.Base.metadata.create_all(bind=engine)

app=FastAPI()

#include each router 
#app.include_router(user.router)
#app.include_router(posts.router)
#app.include_router(likes.router)
#app.include_router(comments.router)
