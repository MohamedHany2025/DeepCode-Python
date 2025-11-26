# FastAPI Dashboard - High-Performance REST API with Real-time Data Visualization
# Project: FastAPI Dashboard
# Language: Python
# Description: High-performance REST API with real-time data visualization and advanced authentication

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, List
import asyncio

# Configuration
DATABASE_URL = "postgresql://user:password@localhost/deepcode_db"
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database Setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== Database Models ====================
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class DataRecord(Base):
    __tablename__ = "data_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    value = Column(Float)
    metadata = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== Pydantic Models ====================
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DataRecordCreate(BaseModel):
    value: float
    metadata: str = ""

class DataRecordResponse(BaseModel):
    id: int
    value: float
    metadata: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_records: int
    average_value: float
    max_value: float
    min_value: float
    last_update: datetime

# ==================== Authentication ====================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(lambda: SessionLocal())):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return user

# ==================== FastAPI Application ====================
app = FastAPI(
    title="DeepCode Dashboard API",
    description="Advanced Python REST API with Authentication and Real-time Data Visualization",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== API Endpoints ====================

@app.post("/api/auth/register", response_model=dict)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "message": "User registered successfully",
        "user_id": db_user.id,
        "email": db_user.email
    }

@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """User login endpoint"""
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    records = db.query(DataRecord).filter(DataRecord.user_id == current_user.id).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No records found")
    
    values = [r.value for r in records]
    
    return DashboardStats(
        total_records=len(records),
        average_value=sum(values) / len(values),
        max_value=max(values),
        min_value=min(values),
        last_update=max(r.created_at for r in records)
    )

@app.post("/api/data/record", response_model=DataRecordResponse)
async def create_data_record(
    data: DataRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new data record"""
    db_record = DataRecord(
        user_id=current_user.id,
        value=data.value,
        metadata=data.metadata
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/api/data/records", response_model=List[DataRecordResponse])
async def get_user_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all user records"""
    records = db.query(DataRecord).filter(DataRecord.user_id == current_user.id).all()
    return records

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "DeepCode Dashboard API"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DeepCode Dashboard API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
