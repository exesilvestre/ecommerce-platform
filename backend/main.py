from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.routes import orders, products
from app.core.rate_limit import limiter
from app.openapi import setup_openapi

app = FastAPI(
    title="E-commerce Order API",
    description="Order API. Reviewer guide: SEED_DATA.md. Test scenarios in /docs.",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
register_exception_handlers(app)
app.include_router(orders.router)
app.include_router(products.router)
setup_openapi(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}
