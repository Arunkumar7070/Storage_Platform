from fastapi import Form, HTTPException, APIRouter
from app.database import get_database
from app.models import User

# For new user registration
router = APIRouter(prefix="/auth", tags=["Authentication"])
@router.post("/register")
def register(username=Form(...), password=Form(...)):
    with get_database() as db:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        new_user = User(username=username, password_hash=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully", "user_id": new_user.id}

#Check if the user exists
@router.post("/login")
def login(username=Form(...), password=Form(...)):
    with get_database() as db:
        user = db.query(User).filter(User.username == username).first()
        if not user or user.password_hash != password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        return {"message": "Login successful", "user_id": user.id}