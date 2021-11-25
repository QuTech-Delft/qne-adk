from pathlib import Path
from typing import cast, Dict, List, Optional

from adk.api.local_api import LocalApi
from adk.api.remote_api import RemoteApi
from adk.decorators import log_function
from adk.exceptions import (ApplicationNotFound, DirectoryAlreadyExists, NetworkNotAvailableForApplication,
                           ResultDirectoryNotAvailable)
from adk.type_aliases import ApplicationType, ExperimentType, ErrorDictType, ResultType
from adk import utils

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
    def applications_delete(self, application_name: Optional[str], path: Path) -> bool:
        # be sure to call both local and remote
        deleted_completely_local = self.__local.delete_application(application_name, path)
        deleted_completely_remote = self.__remote.delete_application(application_name, path)

        return deleted_completely_local and deleted_completely_remote

    @log_function
    def applications_publish(self, application_name: str) -> None:
        self.__remote.publish_application(application_name)

    @log_function
    def applications_validate(self, application_name: str) -> ErrorDictType:
        return self.__local.is_application_valid(application_name)

    @log_function
    def experiments_create(self, experiment_name: str, application_name: str, network_name: str, local: bool,
                           path: Path) -> None:
        """
        Create the experiment directory with files at the given path for the application
        using the specified network.

        Args:
            experiment_name: Name of the directory where experiment will be created
            application_name: Name of the application for which to create the experiment
            network_name: Name of the network to use for creating the experiment
            local: Boolean flag specifying whether experiment is local or remote
            path: Location where the experiment (directory) will be created

        Raises:
            DirectoryAlreadyExists: Raised when directory (or file) experiment_name already exists

        """
        if local:
            experiment_name = experiment_name.lower()
            experiment_path = path / experiment_name

            # check if experiment path is already an existing dir/file
            if experiment_path.exists():
                raise DirectoryAlreadyExists('Experiment', str(experiment_path))

            app_config = self.__local.get_application_config(application_name)
            if app_config:
                if self.__local.is_network_available(network_name, app_config):
                    self.__local.experiments_create(experiment_name=experiment_name, app_config=app_config,
                                                    network_name=network_name, path=path,
                                                    application_name=application_name)
                else:
                    raise NetworkNotAvailableForApplication(network_name, application_name)

            else:
                raise ApplicationNotFound(application_name)

    @log_function
    def experiments_delete(self, experiment_name: Optional[str], path: Path) -> bool:
        # be sure to call both local and remote
        deleted_completely_local = self.__local.delete_experiment(experiment_name, path)
        deleted_completely_remote = self.__remote.delete_experiment(experiment_name, path)

        return deleted_completely_local and deleted_completely_remote

    @log_function
    def __is_application_local(self, application_name: str) -> bool:
        pass

    @log_function
    def experiments_run(self, experiment_name: str, path: Path, block: bool) -> Optional[ResultType]:
        path = path / experiment_name if experiment_name is not None else path

        results = None
        is_local = self.__local.is_experiment_local(path)

        if is_local:
            results = self.__local.run_experiment(path)
            self.__store_results(results, path)

        return results

    @log_function
    def experiments_list(self) -> List[ExperimentType]:
        return self.__remote.list_experiments()

    @log_function
    def experiments_validate(self, experiment_name: str, path: Path) -> ErrorDictType:
        return self.__local.validate_experiment(experiment_name, path)

    @log_function
    def experiments_results(
        self, experiment_name:str,  all_results: bool, path: Path
    ) -> ResultType:
        path = path / experiment_name if experiment_name is not None else path
        results: ResultType = self.__get_results(path=path)
        return results

    @log_function
    def __store_results(self, results: ResultType, path: Path) -> None:
        processed_results_directory = path / "results"
        if not processed_results_directory.exists():
            processed_results_directory.mkdir(parents=True)

        processed_result_json_file = processed_results_directory / 'processed.json'
        utils.write_json_file(processed_result_json_file, results, encoder_cls=utils.ComplexEncoder)

    @log_function
    def __get_results(self, path: Path) -> ResultType:
        processed_results_directory = path / "results"
        if not processed_results_directory.exists():
            raise ResultDirectoryNotAvailable(str(processed_results_directory))

        processed_result_json_file = processed_results_directory / 'processed.json'
        return cast(ResultType, utils.read_json_file(processed_result_json_file))
