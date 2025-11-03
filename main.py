import os
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from controllers.mawaqitController import router as mawaqitRouter
from config.settings import settings

# Import CORS en tête
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title='Mawaqit Api', debug=False, read_root="/")

    # === CONFIG CORS (insérée correctement DANS create_app) ===
    origins = [
        "https://mosquee-arrahmane-web.lovable.app",   # ton site Lovable
        "https://mosquee-arrahmane-web.vercel.app",
        "https://www.arrahman.fr",
        "https://arrahman.fr",# <-- PAS de slash final
        # "http://localhost:5173",                   # <-- décommente si tu veux tester en local
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,            # autorise uniquement les origines listées
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    # ========================================================

    if settings.ENABLE_REDIS:
        storage_uri = settings.REDIS_URI
        limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT], storage_uri=storage_uri)
    else:
        limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    return app

app = create_app()
app.include_router(router=mawaqitRouter)
