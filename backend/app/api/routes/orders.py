from fastapi import APIRouter

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("")
async def create_order():
    return {"message": "Order created"}



