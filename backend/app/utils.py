import math
from decimal import Decimal

from app.core.constants import EARTH_RADIUS_KM
from app.models.product import Product
from app.schemas.orders import OrderItemCreateDTO


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def aggregate_quantities(items: list[OrderItemCreateDTO]) -> dict[int, int]:
    quantities_by_product_id: dict[int, int] = {}
    for item in items:
        quantities_by_product_id[item.product_id] = quantities_by_product_id.get(
            item.product_id, 0
        ) + int(item.quantity)
    return quantities_by_product_id


def calculate_total(
    products_by_id: dict[int, Product],
    quantities_by_product_id: dict[int, int],
) -> Decimal:
    total = Decimal("0.00")
    for product_id, quantity in quantities_by_product_id.items():
        unit_price = Decimal(str(products_by_id[product_id].price))
        total += unit_price * quantity
    return total
