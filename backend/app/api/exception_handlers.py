


from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.constants import (
    ERR_CUSTOMER_NOT_FOUND,
    ERR_INSUFFICIENT_STOCK,
    ERR_NO_WAREHOUSE,
    ERR_PAYMENT_FAILED,
    ERR_PRODUCTS_NOT_FOUND,
)
from app.services.orders import (
    CustomerNotFoundError,
    InsufficientStockError,
    NoWarehouseAvailableError,
    ProductsNotFoundError,
)
from app.services.payments import PaymentFailedError


def register_exception_handlers(app):
    @app.exception_handler(CustomerNotFoundError)
    async def customer_not_found(_: Request, exc: CustomerNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc) or ERR_CUSTOMER_NOT_FOUND})
    
    @app.exception_handler(ProductsNotFoundError)
    async def products_not_founs(_: Request, exc: ProductsNotFoundError):
        return JSONResponse(
            status_code=404, 
            content={
                "detail": str(exc) or ERR_PRODUCTS_NOT_FOUND,
                "missing_product_ids": exc.missing_product_ids
            }
        )
    
    @app.exception_handler(NoWarehouseAvailableError)
    async def no_warehouse_available(_: Request, exc: NoWarehouseAvailableError):
        return JSONResponse(status_code=422, content={"detail": str(exc) or ERR_NO_WAREHOUSE})
    
    @app.exception_handler(InsufficientStockError)
    async def insufficient_stock(_: Request, exc: InsufficientStockError):
        return JSONResponse(status_code=422, content={"detail": str(exc) or ERR_INSUFFICIENT_STOCK})
    
    @app.exception_handler(PaymentFailedError)
    async def payment_failed(_: Request, exc: PaymentFailedError):
        return JSONResponse(status_code=402, content={"detail": str(exc) or ERR_PAYMENT_FAILED})
    
