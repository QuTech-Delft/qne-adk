from pathlib import Path
from typing import List, Optional

from cli.managers.config_manager import ConfigManager
from cli.types import AppConfigType, ApplicationType, ResultType


class RemoteApi:
    def __init__(self, config_manager: ConfigManager) -> None:
        self.__config_manager = config_manager

    def login(self, username: str, password: str, host: str) -> None:
        pass

    def __login_user(self, username: str, password: str, host: str) -> str:
        pass

    def __login_anonymous(self) -> str:
        pass

    def logout(self) -> None:
        pass

    def list_applications(self) -> List[ApplicationType]:
        pass

    def delete_application(self, application: str) -> None:
        pass

    def upload_application(self, application: str) -> None:
        pass

    def __application_exists(self, application_id: int) -> bool:
        pass

    def __create_application_version(self, application_id: int) -> int:
        pass

    def __create_application_config(self, application_version_id: int) -> None:
        pass

    def __create_application_source(self, application_version_id: int) -> None:
        pass

    def __create_application_result(self, application_version_id: int) -> None:
        pass

    def publish_application(self, application: str) -> None:
        pass

    def get_application_config(self, application: str) -> AppConfigType:
        pass

    def delete_experiment(self, experiment_id: int) -> None:
        pass

    def list_experiments(self) -> None:
        pass

    def run_experiment(self, block: bool) -> Optional[List[ResultType]]:
        pass

    def get_results(
        self, path: str, all_results: bool, block: bool, timeout: int
    ) -> List[ResultType]:
        pass

    def __results_exists(self, path: Path) -> bool:
        pass

    def __get_local_results(
        self,
    ) -> List[ResultType]:
        pass
