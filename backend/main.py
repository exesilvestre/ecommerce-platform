from fastapi import FastAPI
from app.api.routes import orders, products
from app.api.exception_handlers import register_exception_handlers
from app.openapi import setup_openapi

app = FastAPI(
    title="E-commerce Order API",
    description="Canals assessment — order API. Reviewer guide: ASSESSMENT.md. Test scenarios in /docs.",
)
register_exception_handlers(app)
app.include_router(orders.router)
app.include_router(products.router)
setup_openapi(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}


