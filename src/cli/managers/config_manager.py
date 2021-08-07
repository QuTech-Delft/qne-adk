from pathlib import Path
from typing import Dict, List, Tuple


class ConfigManager:
    def __init__(self, config_dir: str):
        self.__config_dir = config_dir

    def add_application(self, application: str, path: str) -> None:
        pass

    def delete_application(self, application: str) -> None:
        pass

    def get_application(self, application: str) -> Dict[str, str]:
        pass

    def get_application_from_path(self, path: Path) -> Tuple[str, Dict[str, str]]:
        return "key", {}

    def get_applications(self) -> List[Dict[str, str]]:
        return [{}]

    def application_exists(self, application: str) -> bool:
        return True

    def update_path(self, application: str, path: str) -> None:
        pass
