from pathlib import Path
from typing import Any, cast, Dict, List, Optional

from adk.api.local_api import LocalApi
from adk.api.remote_api import RemoteApi
from adk.decorators import log_function
from adk.exceptions import (ApplicationNotFound, DirectoryAlreadyExists, NetworkNotAvailableForApplication,
                           ResultDirectoryNotAvailable)
from adk.type_aliases import ApplicationType, ExperimentType, ErrorDictType, NetworkType, ResultType
from adk import utils

class CommandProcessor:
    def __init__(self, remote_api: RemoteApi, local_api: LocalApi):
        self.__remote = remote_api
        self.__local = local_api

    @log_function
    def login(self, host: str, username: str, password: str) -> None:
        self.__remote.login(username=username, password=password, host=host)

    @log_function
    def logout(self, host: str) -> bool:
        return self.__remote.logout(host=host)

    def applications_create(
        self, application_name: str, roles: List[str], application_path: Path
    ) -> None:
        self.__local.create_application(application_name, roles, application_path)

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
    def applications_delete(self, application_name: Optional[str], application_path: Path) -> bool:
        """get the remote application id before we delete the local application"""
        application_id = self.__local.get_remote_id_application(application_name, application_path)
        # be sure to call both local and remote
        deleted_completely_remote = self.__remote.delete_application(application_id)
        deleted_completely_local = self.__local.delete_application(application_name, application_path)

        return deleted_completely_local and deleted_completely_remote

    @log_function
    def applications_publish(self, application_name: str) -> None:
        self.__remote.publish_application(application_name)

    @log_function
    def applications_validate(self, application_name: str, local: bool = True) -> ErrorDictType:
        if local:
            return self.__local.is_application_valid(application_name)
        else:
            return self.__remote.is_application_valid(application_name)

    @log_function
    def __is_application_local(self, application_name: str) -> bool:
        pass

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
        experiment_name = experiment_name.lower()
        experiment_path = path / experiment_name

        # check if experiment path is already an existing dir/file
        if experiment_path.exists():
            raise DirectoryAlreadyExists('Experiment', str(experiment_path))

        if local:
            app_config = self.__local.get_application_config(application_name)
        else:
            app_config = self.__remote.get_application_config(application_name)

        if app_config:
            if self.__local.is_network_available(network_name, app_config):
                self.__local.experiments_create(experiment_name=experiment_name,
                                                application_name=application_name,
                                                network_name=network_name,
                                                local=local,
                                                path=path,
                                                app_config=app_config)
            else:
                raise NetworkNotAvailableForApplication(network_name, application_name)

        else:
            raise ApplicationNotFound(application_name)

    @log_function
    def experiments_list(self) -> List[ExperimentType]:
        """Get the remote experiments for the authenticated user"""
        return self.__remote.experiments_list()

    @log_function
    def experiments_validate(self, path: Path) -> ErrorDictType:
        """Validate the local experiment files"""
        return self.__local.validate_experiment(path)

    @log_function
    def experiments_delete(self, experiment_name: Optional[str], experiment_path: Path) -> bool:
        """get the remote experiment id before we delete the local experiment"""
        experiment_id = self.__local.get_experiment_id(experiment_name, experiment_path)
        deleted_completely_remote =\
            self.__remote.delete_experiment(experiment_id) if experiment_id is not None else True
        deleted_completely_local = self.__local.delete_experiment(experiment_name, experiment_path)


        return deleted_completely_local and deleted_completely_remote

    @log_function
    def experiments_run(self, experiment_path: Path, block: bool = True) -> Optional[List[ResultType]]:
        """Run the experiment and get the results. When running a remote experiment depending on the parameter block
        we wait for the results, otherwise None is returned (results not yet available).
        With qne experiment results a next try can be done to get the results

        Returns:
            None if remote results are not yet available, otherwise True
        """
        local = self.__local.is_experiment_local(experiment_path=experiment_path)
        if local:
            results = self.__local.run_experiment(experiment_path)
        else:
            experiment_data = self.__local.get_experiment_data(experiment_path)
            round_set, experiment_id = self.__remote.run_experiment(experiment_data)
            self.__local.set_experiment_id(experiment_id, experiment_path)
            self.__local.set_experiment_round_set(round_set, experiment_path)
            results = self.__remote.get_results(round_set, block)

        if results is not None:
            self.__store_results(results, experiment_path)
        return results

    @log_function
    def experiments_results(self, all_results: bool, experiment_path: Path) -> Optional[List[ResultType]]:
        """Get the experiment results
        Returns:
            None if remote results are not yet available, otherwise True
        """
        remote = not self.__local.is_experiment_local(experiment_path=experiment_path)
        if remote:
            round_set = self.__local.get_experiment_round_set(experiment_path)
            if not self.__results_available(round_set, experiment_path):
                results = self.__remote.get_results(round_set)
                if results is not None:
                    self.__store_results(results, experiment_path)
            else:
                results = self.__get_results(experiment_path=experiment_path)
        else:
            results = self.__get_results(experiment_path=experiment_path)

        return results

    @log_function
    def __results_available(self, round_set_url: str, experiment_path: Path) -> bool:
        processed_result_json_file = experiment_path / 'results' / 'processed.json'
        if processed_result_json_file.exists():
            results = self.__get_results(experiment_path=experiment_path)
            if results[0]["round_set"] == round_set_url:
                return True
        return False

    @log_function
    def __store_results(self, results: List[ResultType], experiment_path: Path) -> None:
        processed_results_directory = experiment_path / "results"
        if not processed_results_directory.exists():
            processed_results_directory.mkdir(parents=True)

        processed_result_json_file = processed_results_directory / 'processed.json'
        utils.write_json_file(processed_result_json_file, results, encoder_cls=utils.ComplexEncoder)

    @log_function
    def __get_results(self, experiment_path: Path) -> List[ResultType]:
        processed_results_directory = experiment_path / "results"
        if not processed_results_directory.exists():
            raise ResultDirectoryNotAvailable(str(processed_results_directory))

        processed_result_json_file = processed_results_directory / 'processed.json'
        return cast(List[ResultType], utils.read_json_file(processed_result_json_file))

    @log_function
    def list_networks(self, remote: bool, local: bool) -> Dict[str, List[Dict[str, Any]]]:
        """
        List the networks available to the user on remote/local/both

        Args:
            remote: Boolean flag for listing remote networks
            local: Boolean flag for listing local networks

        Returns:
            A dictionary containing 'remote' & 'local' keys with
            value as list of networks available to the user

        """
        network_list = {}
        if remote:
            network_list['remote'] = self.__remote.list_networks()

        if local:
            network_list['local'] = self.__local.list_networks()

        return network_list

    @log_function
    def update_networks(self, overwrite: bool) -> bool:
        """
        Get the remote networks and store them in ./networks

        Args:
            overwrite: Boolean flag for overwriting the local networks with the remote networks otherwise merge

        Returns:
            True if all went right

        """
        return self.__remote.update_networks(overwrite=overwrite)
