from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    database_url_sync: str
    rate_limit_enabled: bool = True
    rate_limit_orders: str = "10/minute;100/hour"
    rate_limit_products: str = "60/minute"

    class Config:
        env_file = ".env"
    
settings = Settings()