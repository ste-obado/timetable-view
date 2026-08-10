from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")


#creating database engine
engine=create_engine(DATABASE_URL)

#creating session local class
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

#creating model base class
Base=declarative_base()

#creating tunnel connection to db
def get_db ():
   db=SessionLocal()
   try:
       yield db
   finally:
       db.close()
  
   

