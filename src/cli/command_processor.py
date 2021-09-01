from pathlib import Path
from typing import List, Optional

from cli.api.local_api import LocalApi
from cli.api.remote_api import RemoteApi
from cli.decorators import log_function
from cli.types import ApplicationType, ExperimentType, ResultType


class CommandProcessor:
    def __init__(self, remote_api: RemoteApi, local_api: LocalApi):
        self.__remote = remote_api
        self.__local = local_api

    @log_function
    def login(self, host: str, username: str, password: str) -> None:
        self.__remote.login(host, username, password)

    @log_function
    def logout(self, host: str) -> None:
        self.__remote.logout(host)

    @log_function
    def applications_create(
        self, application: str, roles: List[str], path: Path
    ) -> None:
        self.__local.create_application(application, roles, path)

    @log_function
    def applications_init(self, path: Path) -> None:
        self.__local.init_application(path)

    @log_function
    def applications_upload(self, application: str) -> None:
        self.__remote.upload_application(application)

    @log_function
    def applications_list(self, remote: bool, local: bool) -> List[ApplicationType]:
        app_list = []
        if remote:
            app_list.extend(self.__remote.list_applications())

        if local:
            app_list.extend(self.__local.list_applications())

        return app_list

    @log_function
    def applications_delete(self, application: str) -> None:
        self.__remote.delete_application(application)

    @log_function
    def applications_publish(self, application: str) -> None:
        self.__remote.publish_application(application)

    @log_function
    def applications_validate(self, application: str) -> None:
        self.__local.is_application_valid(application)

    @log_function
    def experiments_create(self, name: str, application: str, local: bool) -> None:
        if local:
            self.__local.get_application_config(application)
        else:
            self.__remote.get_application_config(application)

    @log_function
    def experiments_delete(self, path: Path) -> None:
        self.__remote.delete_experiment(path)
        self.__local.delete_experiment(path)

    @log_function
    def __is_application_local(self, application: str) -> bool:
        pass

    @log_function
    def experiments_run(self, path: Path, block: bool) -> Optional[List[ResultType]]:

        local = True # check if the experiment is local or remote

        if local:
            results = self.__local.run_experiment(path, block)
        else:
            results = self.__remote.run_experiment(block)

        if results:
            self.__store_results(results)

        return results

    @log_function
    def experiments_list(self) -> List[ExperimentType]:
        return self.__remote.list_experiments()

    @log_function
    def experiments_validate(self, path: Path) -> None:
        self.__local.validate_experiment(path)

    @log_function
    def experiments_results(
        self, all_results: bool, show: bool
    ) -> Optional[List[ResultType]]:

        local = True # check if the experiment is local or remote

        if local:
            results = self.__local.get_results('name')
        else:
            results = self.__remote.get_results('path', all_results, block=True, timeout=100)

        if show:
            return results

        self.__store_results(results)
        return None

    @log_function
    def __store_results(self, results: List[ResultType]) -> None:
        pass
