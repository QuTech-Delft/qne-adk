from pathlib import Path


class RoundSetManager:
    def __init__(self) -> None:
        pass

    def process(self) -> None:
        pass

    def validate_asset(self, path: Path) -> bool:
        return True

    def prepare_input(self, path: str) -> None:
        pass

    def terminate(self) -> None:
        pass
