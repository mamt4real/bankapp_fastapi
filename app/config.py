from pydantic import BaseSettings


class Settings(BaseSettings):
    database_host: str
    database_port: str
    database_name: str
    database_user: str
    database_pass: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_expires_in: int

    class Config:
        env_file = ".env"


settings = Settings()
