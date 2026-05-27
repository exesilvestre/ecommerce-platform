from fastapi import FastAPI


app = FastAPI()
app.include_router(orders.router)



@app.get("/health")
def health_check():
    return {"status": "ok"}


