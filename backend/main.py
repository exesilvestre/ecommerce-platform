from fastapi import FastAPI
from app.api.routes import orders, products
from app.api.exception_handlers import register_exception_handlers
from app.openapi import setup_openapi

app = FastAPI(
    title="E-commerce Order API",
    description="Minimal order management API for the Canals assessment. See POST /orders examples in /docs.",
)
register_exception_handlers(app)
app.include_router(orders.router)
app.include_router(products.router)
setup_openapi(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}


