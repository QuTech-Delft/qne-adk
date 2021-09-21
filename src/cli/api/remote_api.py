from pathlib import Path
from typing import Any, List, Optional

from cli.managers.config_manager import ConfigManager
from cli.managers.auth_manager import AuthManager
from cli.type_aliases import AppConfigType, ApplicationType, ExperimentType, ResultType


class RemoteApi:
    def __init__(self, config_manager: ConfigManager) -> None:
        self.__config_manager: ConfigManager = config_manager
        config_dir = self.__config_manager.get_config_dir()
        self.auth_manager:AuthManager = AuthManager(str(config_dir.resolve()),
                                                    self.__login_user, self.__login_anonymous)

    def login(self, username: str, password: str, host: str) -> None:
        pass

    def __login_user(self, username: str, password: str, host: str) -> str:
        pass

    def __login_anonymous(self) -> str:
        pass

    def logout(self, host: str) -> None:
        pass

    def list_applications(self) -> List[ApplicationType]:
        pass

    def delete_application(self, application: str) -> None:
        pass

    def upload_application(self, application: str) -> None:
        pass

    def __create_application(self, token: str, application: str) -> int:
        return 0

    def __create_application_version(self, token: str, application_id: int) -> int:
        return 0

    def __create_application_config(self, token: str, application_version_id: int) -> None:
        pass

    def __create_application_source(self, token: str, application_version_id: int) -> None:
        pass

    def __create_application_result(self, token: str, application_version_id: int) -> None:
        pass

    def publish_application(self, application: str) -> None:
        pass

    def get_application_config(self, application: str) -> Optional[AppConfigType]:
        pass

    def create_experiment(
        self, name: str, app_config: AppConfigType, path: Path
    ) -> None:
        pass

    def delete_experiment(self, path: Path) -> None:
        pass

    def list_experiments(self) -> List[ExperimentType]:
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

    def _action(self, operation_name: str, params: Any) -> Any:
        """Run an arbitrary action on the api-router schema."""
        return {}
