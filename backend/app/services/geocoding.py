import hashlib


class GeocodingService:
    async def geocode(self, address: str) -> tuple[float, float]:
        
        h = hashlib.sha256(address.strip().lower().encode("utf-8")).digest()

        lat_u32 = int.from_bytes(h[0:4], "big")
        lon_u32 = int.from_bytes(h[4:8], "big")

        lat = (lat_u32 / 2**32) * 100.0 - 90.0
        lon = (lon_u32 / 2**32) * 360.0 - 180.0

        return (lat, lon)