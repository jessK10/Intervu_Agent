from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.routers import auth, health, profile, career
from app.routers import interview 

app = FastAPI(title=settings.APP_NAME)

# ✅ CORS settings
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # allow Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],          # allow all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],          # allow all headers (fixes OPTIONS preflight issues)
)

# ✅ Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(interview.router)
app.include_router(profile.router)
app.include_router(career.router)

# ✅ Add security scheme for Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description="API documentation for InterVu",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
