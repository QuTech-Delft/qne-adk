from pathlib import Path

from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    config_dir: Path = Path.home() / ".qne"
