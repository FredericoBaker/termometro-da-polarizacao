import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv


def load_env():
    current = Path(__file__).resolve()
    for parent in current.parents:
        env_file = parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return


def get_db_config() -> Dict[str, Any]:
    load_env()
    
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'user': os.getenv('POSTGRES_USER', 'admin'),
        'password': os.getenv('POSTGRES_PASSWORD', 'admin'),
        'database': os.getenv('POSTGRES_DB', 'termopol'),
    }
    
    return db_config


def get_schema() -> str:
    return os.getenv('POSTGRES_SCHEMA', 'termopol')
