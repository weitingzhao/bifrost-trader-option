"""Configuration management for the application."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # IB Connection Settings
    IB_HOST: str = os.getenv("IB_HOST", "127.0.0.1")
    IB_PORT: int = int(os.getenv("IB_PORT", "7497"))
    IB_CLIENT_ID: int = int(os.getenv("IB_CLIENT_ID", "1"))
    
    # Application Settings
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Cache Settings
    OPTIONS_CACHE_TTL: int = int(os.getenv("OPTIONS_CACHE_TTL", "60"))
    
    # Default Filter Criteria
    DEFAULT_MIN_PROFIT: float = 0.0
    DEFAULT_MIN_RISK_REWARD: float = 0.0
    DEFAULT_MIN_PROBABILITY: float = 0.0
    
    # Strategy Parameters
    DEFAULT_STOCK_QUANTITY: int = 100  # Standard lot size


config = Config()


