import os
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from controllers.mawaqitController import router as mawaqitRouter
from config.settings import settings
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    # Enlève read_root qui cause une erreur
    app = FastAPI(title='Mawaqit Api', debug=False)
    
    # === CONFIG CORS ===
    origins = [
        "https://mosquee-arrahmane-web.lovable.app",
        "https://mosquee-arrahmane-web.vercel.app",
        "https://www.arrahman.fr",
        "https://arrahman.fr",
        # "http://localhost:5173",  # décommente pour test local
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # === RATE LIMITING ===
    if settings.ENABLE_REDIS:
        storage_uri = settings.REDIS_URI
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[settings.RATE_LIMIT],
            storage_uri=storage_uri
        )
    else:
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[settings.RATE_LIMIT]
        )
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    return app

app = create_app()
app.include_router(router=mawaqitRouter)

# Route de test
@app.get("/")
async def root():
    return {
        "message": "Mawaqit API is running",
        "status": "ok",
        "docs": "/docs"
    }

# Point d'entrée pour uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
