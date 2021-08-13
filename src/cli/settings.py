from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    config_dir: Path = Path.home() / ".qne"
