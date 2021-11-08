from pathlib import Path
from typing import Any
from cli.type_aliases import ErrorDictType


class RoundSetManager:
    def __init__(self) -> None:
        pass

    def process(self) -> None:
        pass

    def validate_asset(self, path: Path, error_dict: ErrorDictType) -> Any:
        pass

    def prepare_input(self, path: Path) -> None:
        pass

    def terminate(self) -> None:
        pass
