import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "segredo-super-seguro")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
settings = Settings()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
