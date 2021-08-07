from typing import List, Optional

from cli.managers.config_manager import ConfigManager
from cli.types import (AppConfigType, ApplicationType, ExperimentType,
                       ResultType)


class LocalApi:
    def __init__(self, config_manager: ConfigManager) -> None:
        self.__config_manager = config_manager

    def create_application(self, application: str, roles: List[str]) -> None:
        pass

    def init_application(self) -> None:
        pass

    def __create_application_structure(
        self, application: str, roles: List[str]
    ) -> None:
        pass

    def __is_application_unique(self, application: str) -> bool:
        pass

    def list_applications(self) -> List[ApplicationType]:
        pass

    def is_application_valid(self, application: str) -> bool:
        pass

    def __is_structure_valid(self, application: str) -> bool:
        pass

    def __is_config_valid(self, application: str) -> bool:
        pass

    def get_application_config(self, application: str) -> AppConfigType:
        pass

    def create_experiment(
        self, name: str, app_config: AppConfigType, local: bool
    ) -> None:
        pass

    def delete_experiment(self, path: str) -> None:
        pass

    def run_experiment(self, path: str, block: bool) -> Optional[List[ResultType]]:
        pass

    def get_experiment(self, name: str) -> ExperimentType:
        pass

    def get_results(self, name: str) -> List[ResultType]:
        pass

    def validate_experiment(self, path: str) -> bool:
        pass
