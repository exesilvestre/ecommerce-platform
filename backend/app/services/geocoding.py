import hashlib

# Demo addresses → coords near a warehouse (mock geocoder).
_KNOWN_ADDRESSES: dict[str, tuple[float, float]] = {
    "1 apple park way, cupertino, ca 95014, usa": (37.3349, -122.0090),
    "100 congress ave, austin, tx 78701, usa": (30.2672, -97.7431),
    "350 5th ave, new york, ny 10118, usa": (40.7484, -73.9857),
    "1001 ocean dr, miami beach, fl 33139, usa": (25.7907, -80.1300),
}


class GeocodingService:
    async def geocode(self, address: str) -> tuple[float, float]:
        key = address.strip().lower()
        if key in _KNOWN_ADDRESSES:
            return _KNOWN_ADDRESSES[key]

        h = hashlib.sha256(key.encode("utf-8")).digest()
        lat_u32 = int.from_bytes(h[0:4], "big")
        lon_u32 = int.from_bytes(h[4:8], "big")
        lat = (lat_u32 / 2**32) * 100.0 - 90.0
        lon = (lon_u32 / 2**32) * 360.0 - 180.0
        return (lat, lon)
