from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


class CustomerRepository:
    async def get_customer(self, db: AsyncSession, customer_id: int) -> Customer | None:
        return await db.get(Customer, customer_id)
