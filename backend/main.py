# main.py (updated)
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
from jose import JWTError, jwt
from users_db import UserDB  # New import
from excel_processor import ExcelSQLiteSync
from pathlib import Path

# Configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
EXCEL_FILE_PATH = "C:\\Users\\Anbuselvan\\Desktop\\Book1.xlsx"
DB_PATH = "assets.db"

# CORS Configuration
ORIGINS = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
]

# Initialize databases
user_db = UserDB()  # Replaces fake_users_db
excel_sync = ExcelSQLiteSync(
    excel_path=EXCEL_FILE_PATH,
    db_path=DB_PATH
)

# Models
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    disabled: Optional[bool] = None

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str = "user"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None

class AssetReassignment(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    date_of_return: Optional[str] = None
    date_of_reassign: Optional[str] = None

# Security setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        
        # Verify the role is valid
        if role not in ["admin", "user"]:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    if not (user := user_db.get_user(username)):
        raise credentials_exception
        
    # Ensure the user's role matches the token's role
    if user.get("role") != role:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_admin(current_user: dict = Depends(get_current_active_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# Routes
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, current_user: dict = Depends(require_admin)):
    if not user_db.create_user(
        username=user.username,
        password=user.password,
        full_name=user.full_name,
        email=user.email,
        role=user.role
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    return {"message": "User created successfully"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if not (user := user_db.authenticate_user(form_data.username, form_data.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(
            data={"sub": user["username"], "role": user["role"]}, 
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        ),
        "token_type": "bearer",
        "role": user["role"]
    }

@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return {
        "username": current_user["username"],
        "role": current_user["role"]
    }

# Update the asset endpoints to properly require admin privileges

async def require_asset_access(current_user: dict = Depends(get_current_active_user)):
    print(f"Checking access for user: {current_user['username']} with role: {current_user['role']}")  # Debug logging
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access assets",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

@app.get("/assets/{asset_tag}")
async def get_asset_by_tag(
    asset_tag: str,
    current_user: dict = Depends(require_asset_access)
):
    """Search assets (Admin only)"""
    try:
        assets = excel_sync.get_asset_by_tag(asset_tag)
        if not assets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        return assets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.put("/assets/{asset_tag}/reassign")
async def reassign_asset(
    asset_tag: str,
    reassignment: AssetReassignment,
    current_user: dict = Depends(require_asset_access)
):
    """Reassign asset (Admin only)"""
    try:
        updates = {
            k: v for k, v in reassignment.dict().items() 
            if v is not None and k != "asset_tag"
        }
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
            
        if not excel_sync.reassign_asset(asset_tag, updates):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
            
        return {"message": "Asset reassigned successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/sync/refresh")
async def refresh_sync(current_user: dict = Depends(require_admin)):
    """Manual sync from DB to Excel (Admin only)"""
    try:
        result = excel_sync.sqlite_to_excel()
        return {
            "message": "Manual sync completed",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))