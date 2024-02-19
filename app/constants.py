import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    project_name: str = os.getenv('PROJECT_NAME')
    redis_host: str = os.getenv('REDIS_HOST')
    redis_port: str = os.getenv('REDIS_PORT')
    db_user: str = os.getenv('DB_USER')
    db_password: str = os.getenv('DB_PASSWORD')
    db_host: str = os.getenv('DB_HOST')
    db_name: str = os.getenv('DB_NAME')
    db_port: str = os.getenv('DB_PORT')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
