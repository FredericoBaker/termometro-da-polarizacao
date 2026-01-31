from pathlib import Path
import os
import yaml
from dotenv import load_dotenv


_CONFIG_CACHE = None


def load_env():
    """Carrega variáveis de ambiente do arquivo .env."""
    root_dir = Path(__file__).parent.parent.parent.parent
    env_file = root_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)


def _get_config_path() -> Path:
    env_path = os.getenv("PIPELINE_CONFIG_PATH")
    if env_path:
        return Path(env_path)

    return Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    global _CONFIG_CACHE

    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    load_env()
    config_path = _get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path}."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        _CONFIG_CACHE = yaml.safe_load(f) or {}

    return _CONFIG_CACHE


def get(section: str, key: str | None = None, default=None):
    config = load_config()

    if section not in config:
        if default is not None:
            return default
        raise KeyError(f"Missing config section '{section}'")

    if key is None:
        return config[section]

    if key not in config[section]:
        if default is not None:
            return default
        raise KeyError(f"Missing config key '{section}.{key}'")

    return config[section][key]
