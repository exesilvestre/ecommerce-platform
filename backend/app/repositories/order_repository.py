from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OrderStatus, PaymentStatus
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.product import Product


class OrderRepository:
    async def create_pending_order(
        self,
        db: AsyncSession,
        *,
        customer_id: int,
        warehouse_id: int,
        total_amount: Decimal,
        shipping_address: str,
        shipping_latitude: float,
        shipping_longitude: float,
        quantities_by_product_id: dict[int, int],
        products_by_id: dict[int, Product],
    ) -> tuple[Order, Payment]:
        order = Order(
            customer_id=customer_id,
            warehouse_id=warehouse_id,
            status=OrderStatus.AWAITING_PAYMENT,
            total_amount=total_amount,
            shipping_address=shipping_address,
            shipping_latitude=shipping_latitude,
            shipping_longitude=shipping_longitude,
        )
        db.add(order)
        await db.flush()

        for product_id, quantity in quantities_by_product_id.items():
            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=products_by_id[product_id].price,
                )
            )

        payment = Payment(
            order_id=order.id,
            amount=total_amount,
            status=PaymentStatus.PENDING,
            payment_intent_id=None,
        )
        db.add(payment)
        await db.flush()
        return order, payment

    async def get_order_for_update(
        self,
        db: AsyncSession,
        order_id: int,
    ) -> Order | None:
        return await db.get(Order, order_id, with_for_update=True)

    async def get_payment_for_update(
        self,
        db: AsyncSession,
        order_id: int,
    ) -> Payment:
        result = await db.execute(
            select(Payment).where(Payment.order_id == order_id).with_for_update()
        )
        return result.scalar_one()

    def mark_confirmed(
        self,
        order: Order,
        payment: Payment,
        payment_intent_id: str,
    ) -> None:
        if order.status != OrderStatus.CONFIRMED:
            order.status = OrderStatus.CONFIRMED
            payment.status = PaymentStatus.SUCCESS
            payment.payment_intent_id = payment_intent_id

    def mark_failed(self, order: Order, payment: Payment) -> None:
        order.status = OrderStatus.FAILED
        payment.status = PaymentStatus.FAILED
