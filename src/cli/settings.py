import os
from pathlib import Path
from pydantic import BaseSettings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    config_dir: Path = Path.home() / ".qne"
