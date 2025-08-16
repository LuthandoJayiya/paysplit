from fastapi import APIRouter, Depends
from src.core.security import decode_access_token

router = APIRouter()

@router.get("/me")
async def get_me(user=Depends(decode_access_token)):
    return {"message": "User profile"}