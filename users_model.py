from sqlalchemy import Column, Integer, String
from users_db import Base

class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    f_name = Column(String(10))
    l_name = Column(String(10))
    Email = Column(String(100))
    password = Column(String(100))