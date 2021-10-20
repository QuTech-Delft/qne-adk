from pathlib import Path
from typing import Any
from cli.utils import read_json_file
from cli.settings import BASE_DIR
from cli.validators import validate_json_string, validate_json_schema


class RoundSetManager:
    def __init__(self) -> None:
        pass

    def process(self) -> None:
        pass

    def validate_asset(self, path: Path) -> Any:
        experiment_path = path / 'experiment.json'
        experiment_schema = Path(BASE_DIR + "/schema/experiments/experiment.json")

        json_valid, message = validate_json_string(experiment_path)
        if json_valid:
            schema_valid, ve = validate_json_schema(experiment_path, experiment_schema)
            if not schema_valid:
                return schema_valid, ve
        if not json_valid:
            return None, None
        else:
            return None, None

    def prepare_input(self, path: Path) -> None:
        pass

    def terminate(self) -> None:
        pass
