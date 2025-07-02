from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr
import users_model
from users_db import engine, SessionLocal
from sqlalchemy.orm import Session
import bcrypt

app = FastAPI()

users_model.Base.metadata.create_all(bind=engine)

#communicate with database --------------------
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#hashing the same password we got at the sign_up panel --------------------
def hash_pass(plain_pass: str) -> str:
    return bcrypt.hashpw(plain_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

#unhash the password for authenticate in login panel --------------------
def verify_pass(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

#Pydantic models for request validation --------------------
class Users(BaseModel):
    f_name: str = Field(min_length=1, max_length=10)
    l_name: str = Field(min_length=1, max_length=10)
    Email: EmailStr = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=100)

class Loginreq(BaseModel):
    Email: EmailStr = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=100)

#login panel --------------------
@app.post("/login")
def login(credentials: Loginreq, db: Session = Depends(get_db)):
    user = db.query(users_model.Users).filter(users_model.Users.Email == credentials.Email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_pass(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {"message": "Login successful", "user": user.f_name+" "+user.l_name, "role": user.role}

#sign up panel --------------------
@app.post("/sign-up")
def sign_up(users: Users, db: Session = Depends(get_db)):
    exist_user = db.query(users_model.Users).filter(users_model.Users.Email == users.Email).first()
    
    if exist_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_pass(users.password)

    user = users_model.Users(
        role="customer",
        f_name=users.f_name,
        l_name=users.l_name,
        Email=users.Email,
        password=hashed_pw
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully", "user": user.f_name+" "+user.l_name}