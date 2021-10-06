from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cli.api.local_api import LocalApi
from cli.api.remote_api import RemoteApi
from cli.decorators import log_function
from cli.type_aliases import ApplicationType, ExperimentType, ResultType, ErrorDictType


class CommandProcessor:
    def __init__(self, remote_api: RemoteApi, local_api: LocalApi):
        self.__remote = remote_api
        self.__local = local_api

    @log_function
    def login(self, host: str, username: str, password: str) -> None:
        self.__remote.login(username=username, password=password, host=host)

    @log_function
    def logout(self, host: str) -> None:
        self.__remote.logout(host=host)

    def applications_create(
        self, application_name: str, roles: List[str], path: Path
    ) -> None:
        self.__local.create_application(application_name, roles, path)

    @log_function
    def applications_init(self, path: Path) -> None:
        self.__local.init_application(path)

    @log_function
    def applications_upload(self, application_name: str) -> None:
        self.__remote.upload_application(application_name)

    @log_function
    def applications_list(self, remote: bool, local: bool) -> Dict[str, List[ApplicationType]]:
        """
        List the applications available to the user on remote/local/both

        Args:
            remote: Boolean flag for listing remote applications
            local: Boolean flag for listing local applications

        Returns:
            A dictionary containing 'remote' & 'local' keys with
            value as list of applications available to the user

        """
        app_list = {}
        if remote:
            app_list['remote'] = self.__remote.list_applications()

        if local:
            app_list['local'] = self.__local.list_applications()

        return app_list

    @log_function
    def applications_delete(self, application_name: str) -> None:
        self.__remote.delete_application(application_name)

    @log_function
    def applications_publish(self, application_name: str) -> None:
        self.__remote.publish_application(application_name)

    @log_function
    def applications_validate(self, application_name: str) -> ErrorDictType:
        return self.__local.is_application_valid(application_name)

    @log_function
    def experiments_create(self, name: str, application: str, network_name: str, local: bool, path: Path) \
        -> Tuple[bool, str]:
        if local:
            app_config = self.__local.get_application_config(application)
            if app_config:
                if self.__local.is_network_available(network_name, app_config):
                    return self.__local.experiments_create(name=name, app_config=app_config, network_name=network_name,
                                                    path=path, application=application)

                return False, f"The specified network '{network_name}' does not exist."

            return False, f"Application '{application}' was not found."

        return False, 'Remote experiment creation is not yet enabled.'

    @log_function
    def experiments_delete(self, path: Path) -> None:
        self.__remote.delete_experiment(path)
        self.__local.delete_experiment(path)

    @log_function
    def __is_application_local(self, application_name: str) -> bool:
        pass

    @log_function
    def experiments_run(self, path: Path, block: bool) -> Optional[List[ResultType]]:

        results = None
        is_local = self.__local.is_experiment_local(path)

        if is_local:
            results = self.__local.run_experiment(path)
        else:
            results = self.__remote.run_experiment(block)

        if results:
            self.__store_results(results)

        return results

    @log_function
    def experiments_list(self) -> List[ExperimentType]:
        return self.__remote.list_experiments()

    @log_function
    def experiments_validate(self, path: Path) -> Tuple[bool, str]:
        return self.__local.validate_experiment(path)

    @log_function
    def experiments_results(
        self, all_results: bool, show: bool, path:Path
    ) -> Optional[List[ResultType]]:
        results = None
        is_local = self.__local.is_experiment_local(path)

        if is_local:
            results = self.__local.get_results(path, all_results)
        else:
            results = self.__remote.get_results('path', all_results, block=True, timeout=100)

        if show:
            return results

        self.__store_results(results)
        return None

    @log_function
    def __store_results(self, results: List[ResultType]) -> None:
        pass
