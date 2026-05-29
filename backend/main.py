from fastapi import FastAPI
from app.api.routes import orders, products
from app.api.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(orders.router)
app.include_router(products.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


