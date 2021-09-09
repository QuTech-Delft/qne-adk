from pathlib import Path
from typing import Tuple


class RoundSetManager:
    def __init__(self) -> None:
        pass

    def process(self) -> None:
        pass

    def validate_asset(self, path: Path) -> Tuple[bool, str]:
        return True, 'Valid'

    def prepare_input(self, path: str) -> None:
        pass

    def terminate(self) -> None:
        pass
