from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ERR_CUSTOMER_NOT_FOUND
from app.domain.order_errors import CustomerNotFoundError
from app.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(
        self, customer_repository: CustomerRepository | None = None
    ) -> None:
        self.customer_repository = customer_repository or CustomerRepository()

    async def ensure_exists(self, db: AsyncSession, customer_id: int) -> None:
        customer = await self.customer_repository.get_customer(
            db=db, customer_id=customer_id
        )
        if not customer:
            raise CustomerNotFoundError(ERR_CUSTOMER_NOT_FOUND)
