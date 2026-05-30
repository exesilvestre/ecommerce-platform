import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from schemas import DEFAULT_CUSTOMER_EMAIL, SeedDataSchema


class SeedLoadError(Exception):
    pass


@dataclass
class SeedLoadResult:
    customer_id: int
    customer_email: str
    product_count: int
    warehouse_count: int
    inventory_count: int


class SeedLoader:
    _DELETE_ORDER = (
        "idempotency_keys",
        "payments",
        "order_items",
        "orders",
        "warehouse_inventory",
        "warehouses",
        "products",
        "customers",
    )
    _SEQUENCES = (
        "payments_id_seq",
        "order_items_id_seq",
        "orders_id_seq",
        "customers_id_seq",
        "products_id_seq",
        "warehouses_id_seq",
    )

    def __init__(self, database_url: str) -> None:
        self._engine: Engine = create_engine(database_url)
        self._session_factory = sessionmaker(bind=self._engine)

    def load_from_file(self, file_path: Path) -> SeedLoadResult:
        data = self._read_seed_file(file_path)
        with self._session_factory() as session:
            with session.begin():
                self._reset_tables(session)
                return self._insert_seed_data(session, data)

    def _read_seed_file(self, file_path: Path) -> SeedDataSchema:
        if not file_path.is_file():
            raise SeedLoadError(f"seed file not found: {file_path}")
        raw = json.loads(file_path.read_text(encoding="utf-8"))
        return SeedDataSchema.model_validate(raw)

    def _reset_tables(self, session: Session) -> None:
        for table_name in self._DELETE_ORDER:
            session.execute(text(f"DELETE FROM {table_name}"))
        for sequence_name in self._SEQUENCES:
            session.execute(
                text(f'ALTER SEQUENCE IF EXISTS "{sequence_name}" RESTART WITH 1')
            )

    def _insert_seed_data(self, session: Session, data: SeedDataSchema) -> SeedLoadResult:
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        customer_row = session.execute(
            text(
                """
                INSERT INTO customers (name, email, phone, created_at, updated_at)
                VALUES (:name, :email, :phone, :created_at, :updated_at)
                RETURNING id, email
                """
            ),
            {
                "name": data.customer.name,
                "email": data.customer.email,
                "phone": data.customer.phone,
                "created_at": now,
                "updated_at": now,
            },
        ).one()
        customer_id = int(customer_row.id)
        customer_email = str(customer_row.email)

        product_id_by_ref: dict[str, int] = {}
        for product in data.products:
            row = session.execute(
                text(
                    """
                    INSERT INTO products (name, description, price, created_at, updated_at)
                    VALUES (:name, :description, :price, :created_at, :updated_at)
                    RETURNING id
                    """
                ),
                {
                    "name": product.name,
                    "description": product.description,
                    "price": Decimal(product.price),
                    "created_at": now,
                    "updated_at": now,
                },
            ).one()
            product_id_by_ref[product.ref] = int(row.id)

        inventory_count = 0
        for warehouse in data.warehouses:
            warehouse_row = session.execute(
                text(
                    """
                    INSERT INTO warehouses (name, address, latitude, longitude, created_at, updated_at)
                    VALUES (:name, :address, :latitude, :longitude, :created_at, :updated_at)
                    RETURNING id
                    """
                ),
                {
                    "name": warehouse.name,
                    "address": warehouse.address,
                    "latitude": warehouse.latitude,
                    "longitude": warehouse.longitude,
                    "created_at": now,
                    "updated_at": now,
                },
            ).one()
            warehouse_id = int(warehouse_row.id)

            for item in warehouse.inventory:
                session.execute(
                    text(
                        """
                        INSERT INTO warehouse_inventory
                            (warehouse_id, product_id, quantity, created_at, updated_at)
                        VALUES
                            (:warehouse_id, :product_id, :quantity, :created_at, :updated_at)
                        """
                    ),
                    {
                        "warehouse_id": warehouse_id,
                        "product_id": product_id_by_ref[item.product_ref],
                        "quantity": item.quantity,
                        "created_at": now,
                        "updated_at": now,
                    },
                )
                inventory_count += 1

        if customer_email != DEFAULT_CUSTOMER_EMAIL:
            raise SeedLoadError(
                f"seed customer email must be {DEFAULT_CUSTOMER_EMAIL}, got {customer_email}"
            )

        return SeedLoadResult(
            customer_id=customer_id,
            customer_email=customer_email,
            product_count=len(data.products),
            warehouse_count=len(data.warehouses),
            inventory_count=inventory_count,
        )
