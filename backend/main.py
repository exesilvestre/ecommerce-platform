from fastapi import FastAPI
from app.api.routes import orders


app = FastAPI()
app.include_router(orders.router)



@app.get("/health")
def health_check():
    return {"status": "ok"}


