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
        pass

    @log_function
    def logout(self, host: str) -> None:
        pass

    @log_function
    def applications_create(
        self, application: str, roles: List[str], path: Path
    ) -> None:
        pass

    @log_function
    def applications_init(self, path: Path) -> None:
        pass

    @log_function
    def applications_upload(self, application: str) -> None:
        pass

    @log_function
    def applications_list(self, remote: bool, local: bool) -> List[ApplicationType]:
        return []

    @log_function
    def applications_delete(self, application: str) -> None:
        pass

    @log_function
    def applications_publish(self, application: str) -> None:
        pass

    @log_function
    def applications_validate(self, application: str) -> None:
        pass

    @log_function
    def experiments_create(self, name: str, application: str, local: bool) -> None:
        pass

    @log_function
    def experiments_delete(self, path: Path) -> None:
        pass

    @log_function
    def __is_application_local(self, application: str) -> bool:
        pass

    @log_function
    def experiments_run(self, path: Path, block: bool) -> Optional[List[ResultType]]:
        return []

    @log_function
    def experiments_list(self) -> List[ExperimentType]:
        pass

    @log_function
    def experiments_validate(self, path: Path) -> None:
        pass

    @log_function
    def experiments_results(
        self, all_results: bool, show: bool
    ) -> Optional[List[ResultType]]:
        return []

    @log_function
    def __store_results(self, results: List[ResultType]) -> None:
        pass
