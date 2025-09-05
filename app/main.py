from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from app.config.settings import settings
from app.config.logger import get_logger
from app.routes import register_routes

logger = get_logger("API Logger")

def create_app() -> FastAPI:
    app = FastAPI(title="Psychologist Backend Application")

    allowed_origins = [origin.strip() for origin in settings.FRONTEND_ORIGIN.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routers
    register_routes(app)
    
    @app.get("/")
    async def read_root():
        return {"message": "Welcome to the Backend."}
    
    @app.get("/health")
    async def check_health():
        logger.info(f"Health Check.")
        return {"message": "Server is healthy."}
    
    @app.middleware("http")
    async def catch_json_errors(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}")
            return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

    
    return app