from fastapi import FastAPI
from src.core.config import settings
from src.core.firebase import firebase_admin
from src.api.v1.endpoints import auth, users

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
