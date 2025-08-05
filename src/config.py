"""
Configuration management for Google Trends Website Builder
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    name: str = os.getenv('DB_NAME', 'trends_db')
    user: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD', 'password')
    
    @property
    def url(self) -> str:
        """Get database URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', '6379'))
    db: int = int(os.getenv('REDIS_DB', '0'))
    password: Optional[str] = os.getenv('REDIS_PASSWORD')
    
    @property
    def url(self) -> str:
        """Get Redis URL"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


@dataclass
class APIConfig:
    """API configuration"""
    host: str = os.getenv('API_HOST', '0.0.0.0')
    port: int = int(os.getenv('API_PORT', '8000'))
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    secret_key: str = os.getenv('SECRET_KEY', 'dev-secret-key')


@dataclass
class ScrapingConfig:
    """Web scraping configuration"""
    request_delay: float = float(os.getenv('REQUEST_DELAY', '1.0'))
    max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
    timeout: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    user_agent: str = os.getenv('USER_AGENT', 'Mozilla/5.0 (compatible; TrendsBot/1.0)')


@dataclass
class AppConfig:
    """Main application configuration"""
    database: DatabaseConfig
    redis: RedisConfig
    api: APIConfig
    scraping: ScrapingConfig
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.api = APIConfig()
        self.scraping = ScrapingConfig()


# Global configuration instance
config = AppConfig()