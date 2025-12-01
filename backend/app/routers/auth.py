from fastapi import APIRouter, Depends, HTTPException, Header, status
from app.schemas.user import UserCreate, UserLogin, UserPublic
from app.schemas.auth import Token
from app.db.mongo import users_col
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])


# ✅ Register new user
@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate):
    col = users_col()
    existing = await col.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "role": "candidate",
    }

    res = await col.insert_one(doc)

    return {
        "id": str(res.inserted_id),
        "name": payload.name,
        "email": payload.email,
        "role": "candidate"
    }


# ✅ Login
@router.post("/login", response_model=Token)
async def login(payload: UserLogin):
    col = users_col()
    user = await col.find_one({"email": payload.email})

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # JWT token contains user_id as subject (sub)
    token = create_access_token(str(user["_id"]))

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "name": user.get("name") or user["email"].split("@")[0],
            "email": user["email"],
            "role": user["role"],
        },
    }


# ✅ Dependency: get current logged-in user
async def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = authorization.split(" ", 1)[1]
    sub = decode_token(token)  # sub = user_id extracted from JWT

    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await users_col().find_one({"_id": ObjectId(sub)})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # ✅ Ensure consistent field names with Interview routes
    return {
        "id": str(user["_id"]),
        "name": user.get("name") or user.get("email").split("@")[0],
        "email": user["email"],
        "role": user["role"],
    }


# ✅ Get user profile
@router.get("/me", response_model=UserPublic)
async def me(current=Depends(get_current_user)):
    return current
