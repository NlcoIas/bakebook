from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "dev"
    database_url: str = "postgresql+asyncpg://bakebook:bakebook@localhost:5432/bakebook"
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "bakebook"
    auth_dev_email: str = "dev@local"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
