from pathlib import Path
import time
from typing import Any, List, Optional, cast

from cli.managers.config_manager import ConfigManager
from cli.managers.auth_manager import AuthManager
from cli.types import AppConfigType, ApplicationType, ExperimentType, ResultType


class RemoteApi:
    def __init__(self, config_manager: ConfigManager) -> None:
        self.__config_manager: ConfigManager = config_manager
        config_dir = self.__config_manager.get_config_dir()
        self.auth_manager:AuthManager = AuthManager(str(config_dir.resolve()),
                                                    self.__login_user, self.__login_anonymous)

    def login(self, username: str, password: str, host: str) -> None:
        self.auth_manager.login(username, password, host)

    def __login_user(self, username: str, password: str, host: str) -> str:
        pass

    def __login_anonymous(self) -> str:
        pass

    def logout(self, host: str) -> None:
        if host is None:
            host = self.auth_manager.get_active_host()

        self.auth_manager.delete_token(host)

    def list_applications(self) -> List[ApplicationType]:
        token = self.auth_manager.load_token()
        self._action('listApplications', {'token': token})
        return []

    def delete_application(self, application: str) -> None:
        app = self.__config_manager.get_application(application)
        token = self.auth_manager.load_token()
        self._action('delete', {'token': token, 'id': app})

    def upload_application(self, application: str) -> None:
        token = self.auth_manager.load_token()
        application_exists, application_id = self.__config_manager.remote_application_exists(application)

        if not application_exists:
            application_id = self.__create_application(token, application)
            self.__config_manager.update_remote_id(application, application_id)

        app_version_id = self.__create_application_version(token, application_id)
        self.__create_application_config(token, app_version_id)
        self.__create_application_source(token, app_version_id)
        self.__create_application_result(token, app_version_id)

    def __create_application(self, token: str, application: str) -> int:
        self._action('createApplication', {'token': token, 'body': application})
        return 0

    def __create_application_version(self, token: str, application_id: int) -> int:
        self._action('createApplicationVersion', {'token': token, 'id': application_id})
        return 0

    def __create_application_config(self, token: str, application_version_id: int) -> None:
        self._action('createApplicationConfig', {'token': token, 'id': application_version_id})

    def __create_application_source(self, token: str, application_version_id: int) -> None:
        self._action('createApplicationSource', {'token': token, 'id': application_version_id})

    def __create_application_result(self, token: str, application_version_id: int) -> None:
        self._action('createApplicationResult', {'token': token, 'id': application_version_id})

    def publish_application(self, application: str) -> None:
        application_exists, application_id = self.__config_manager.remote_application_exists(application)
        if application_exists:
            token = self.auth_manager.load_token()
            self._action('publishApplication', {'token': token, 'id': application_id})
        else:
            pass # Please upload application before publishing

    def get_application_config(self, application: str) -> Optional[AppConfigType]:
        application_exists, application_id = self.__config_manager.remote_application_exists(application)

        if application_exists:
            token = self.auth_manager.load_token()
            response = self._action('getAppConfig', {'token': token, 'id': application_id})
            return cast(AppConfigType, response)

        return None # Application does not exist on remote

    def delete_experiment(self, path: Path) -> None:
        experiment_exists, experiment_id = self.__config_manager.remote_experiment_exists(path)

        if experiment_exists:
            token = self.auth_manager.load_token()
            self._action('deleteExperiment', {'token': token, 'id': experiment_id})

    def list_experiments(self) -> List[ExperimentType]:
        token = self.auth_manager.load_token()
        self._action('listExperiments', {'token': token})
        return []

    def run_experiment(self, block: bool) -> Optional[List[ResultType]]:
        token = self.auth_manager.load_token()
        self._action('createExperiment', {'token': token, 'body': 'body'})
        self._action('createRoundSet', {'token': token, 'body': 'body'})

        if block:
            while True:
                results_response = self._action('getResults', {'token': token, 'body': 'body'})
                results_respone_available = True # check if the result is available

                if results_respone_available:
                    return cast(List[ResultType], results_response)

                # Sleep for some configurable number of seconds and try again!
                time.sleep(10)
        else:
            return None



    def get_results(
        self, path: str, all_results: bool, block: bool, timeout: int
    ) -> List[ResultType]:
        if self.__results_exists(Path(path)):
            return self.__get_local_results()

        token = self.auth_manager.load_token()
        results = self._action('getResults', {'token': token, 'body': 'body'})
        return cast(List[ResultType], results)

    def __results_exists(self, path: Path) -> bool:
        pass

    def __get_local_results(
        self,
    ) -> List[ResultType]:
        pass

    def _action(self, operation_name: str, params: Any) -> Any:
        """Run an arbitrary action on the api-router schema."""
        return {}
