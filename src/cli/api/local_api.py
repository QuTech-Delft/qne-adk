
from typing import List, Optional, Tuple
from pathlib import Path
import json

import cli.utils as utils
from cli.managers.config_manager import ConfigManager
from cli.managers.roundset_manager import RoundSetManager
from cli.output_converter import OutputConverter
from cli.type_aliases import (AppConfigType, ApplicationType, app_configNetworkType,
                              app_configApplicationType, assetApplicationType, assetNetworkType,
                              ExperimentType, ResultType)
from cli.utils import read_json_file, write_json_file


class LocalApi:
    def __init__(self, config_manager: ConfigManager) -> None:
        self.__config_manager = config_manager

    def create_application(self, application: str, roles: List[str], path: Path) -> None:

        # code to add the application to .qne/application.json if it doesn't exist
        app_config_file = utils.check_if_config_exists()

        # Check if application already exists
        if self.__is_application_unique(application):
            # code to create the local application in root dir
            app_dir = path / "src/cli/applications" / application / "application"
            config_dir = path / "src/cli/applications" / application / " config"
            app_dir.mkdir(parents=True, exist_ok=True)
            config_dir.mkdir(parents=True, exist_ok=True)

            for role in roles:
                py_file = app_dir / f"app_{role}.py"
                with open(py_file, 'w') as _:
                    pass

            for config in ["network", "application", "result"]:
                config_file = config_dir / f"{config}.json"
                with open(config_file, "w") as fp:
                    json.dump({}, fp, indent=4)

            manifest_file = path / "MANIFEST.ini"
            with open(manifest_file, "w") as fp:
                pass

            # Read json file
            with app_config_file.open(mode="r") as fp:
                data = fp.read()
                apps = json.loads(data)

            # Store the app path
            apps[application] = {'path': str(path), 'application_id': 'None'}
            with app_config_file.open(mode="w") as fp:
                json.dump(apps, fp, indent=4)

        else:
            raise Exception('Application name is not unique.')

    def init_application(self, path: Path) -> None:
        # Find out application name & roles from the files in 'path'
        application = ''
        roles = ['', '']

        if self.__is_application_unique(application):
            self.__create_application_structure(application, roles, path)

    def __create_application_structure(
        self, application: str, roles: List[str], path: Path
    ) -> None:
        self.__config_manager.add_application(application, path)

    def __is_application_unique(self, application: str) -> bool:

        """
        Calls config_manager.application_exists() to check if the application name already exists in the
        .qne/application.json root file. Here, all application names are added when an application is created.
        If the application name doesn't equal one of the application names already existing in this root file, the
        application is unique. Therefore, application_unique() returns True when application_exists() returns False.

        Args:
            application: application name
        """
        return not self.__config_manager.application_exists(application)

    def list_applications(self) -> List[ApplicationType]:
        """
        Function to list the applications

        Returns:
            A list of applications
        """
        local_applications = self.__config_manager.get_applications()
        return local_applications

    # Todo: Update confluence scenario diagram since application_unique() and structure_valid() are swapped
    def is_application_valid(self, application: str) -> Tuple[bool, str]:
        if self.__is_application_unique(application) and \
           self.__is_structure_valid(application) and \
           self.__is_config_valid(application):
            return True, "Valid"

        return False, "Invalid"

    def __is_structure_valid(self, application: str) -> bool:
        pass

    def __is_config_valid(self, application: str) -> bool:
        pass

    def get_application_config(self, application: str) -> AppConfigType:
        app_details = self.__config_manager.get_application(application)

        app_config_path = Path(app_details['path']) / 'config'
        application_json_path = app_config_path / 'application.json'
        network_json_path = app_config_path / 'network.json'

        app_config_application: app_configApplicationType = read_json_file(application_json_path)
        app_config_network: app_configNetworkType = read_json_file(network_json_path)

        app_config = {"application": app_config_application, "network": app_config_network}
        return app_config

    def experiments_create(self, name: str, app_config: AppConfigType , network_name: str,
                           path: Path, application:str)-> Tuple[bool, str]:
        """
        Create all the necessary resources for experiment creation
         - 1. Get the network data for the specified network_name
         - 2. Create the asset
         - 3. Create experiment.json containing the meta data and asset information

        Args:
            name: Name of the experiment
            app_config:
            network_name: Name of the network to use
            path: Location where the experiment directory is to be created
            application: Name of the application for which to create experiment

        Returns:
            Returns (False, reason for failure) if experiment creation failed,
            (True, Success) if experiment was created successfully

        """
        network_data: assetNetworkType = self.get_network_data(network_name=network_name)
        asset_network: assetNetworkType = self.create_asset_network(network_data=network_data,
                                                                    app_config=app_config)

        return self.create_experiment(name=name, app_config=app_config, asset_network=asset_network, path=path,
                                application=application)

    def get_network_data(self, network_name: str)-> assetNetworkType:
        """
        Fetch the data for the specified network_name from the json files in networks folder

        Args:
            network_name: Name of the network whose data needs to be fetched

        Returns:
            The complete network information with channels & nodes

        """
        return {}

    def create_experiment(
        self, name: str, app_config: AppConfigType, asset_network: assetNetworkType, path: Path, application: str
    ) -> Tuple[bool, str]:

        experiment_directory = path / name
        if experiment_directory.is_dir():
            return False, f'Experiment directory {name} already exists.'

        experiment_directory.mkdir(parents=True)

        input_directory = experiment_directory / 'input'
        input_directory.mkdir(parents=True)
        self.__copy_input_files_from_application(application, input_directory)

        experiment_json_file = experiment_directory / 'experiment.json'
        experiment_meta = {
            "backend": {
                "location": "local",
                "type": "local_netsquid"
             },
            "number_of_rounds": 1,
            "description": f"{name}: experiment description"
        }

        asset_application = self.__create_asset_application(app_config)
        asset = {"network": asset_network, "application": asset_application}

        experiment_data = {'meta': experiment_meta, 'asset': asset}
        write_json_file(experiment_json_file, experiment_data)

        return True, "Success"

    def __create_asset_application(self,  app_config: AppConfigType) -> assetApplicationType:
        return []

    def create_asset_network(self,  network_data: assetNetworkType, app_config: AppConfigType) ->  assetNetworkType:
        return {}

    def __copy_input_files_from_application(self,  application: str, input_directory: Path) -> None:
        """
        Copy the input/source files of the 'application' to the 'input_directory'

        Args:
            application: The application name for which the input files need to be copied
            input_directory: The destination where application files need to be stored

        """

    def is_network_available(self, network_name: str, app_config: AppConfigType) -> bool:
        """
        Check if the network_name is available for use in the application's app_config

        Args:
            network_name: The network name
            app_config: Application Configuration containing the available networks

        Returns:
            bool: True if the given network name is available in application configuration, False otherwise
        """
        return True

    def is_experiment_local(self, path: Path) -> bool:
        """
        Check if the experiment at the 'path' is remote or local

        Args:
            path: The location of the experiment

        Returns:
            bool: True if the experiment at given path is local, False otherwise
        """
        # read experiment.json and check the meta->backend->location attribute
        return True

    def get_experiment_rounds(self, path: Path) -> int:
        """
        Get the number of rounds in an experiment

        Args:
            path: The location of the experiment

        Returns:
            int: Value of the number of rounds
        """
        # read experiment.json and check the meta->number_of_rounds attribute
        return 1

    def delete_experiment(self, path: Path) -> None:
        pass

    def run_experiment(self, path: Path) -> Optional[List[ResultType]]:
        roundSetManager = RoundSetManager()
        roundSetManager.prepare_input(path)
        roundSetManager.process()
        roundSetManager.terminate()
        return []

    def get_experiment(self, name: str) -> ExperimentType:
        pass

    def get_results(self, path: Path, all_results: bool) -> List[ResultType]:
        outputConverter = OutputConverter('log_dir', 'output_dir')

        result_list: List[ResultType] = []
        output_result: List[ResultType] = []

        total_rounds = self.get_experiment_rounds(path)
        if all_results:
            for round_number in range(1, total_rounds + 1):
                output_result.append(outputConverter.convert(round_number, result_list))
        else:
            output_result.append(outputConverter.convert(total_rounds, result_list))

        return output_result

    def validate_experiment(self, path: Path) -> Tuple[bool, str]:
        # TODO: Add any other validation which should be done
        """
        Validates the experiment by checking:
        - if the structure is correct and consists of an experiment.json
        - (For local run) experiment directory contains an input directory with the correct files
        - (For local run) check the python & yaml files for correct syntax (possible?)
        - content of experiment.json is valid JSON
        - asset in the experiment.json validated against a schema validator.
        """

        experiment_json = path / 'experiment.json'
        if not experiment_json.is_file():
            return False, 'File experiment.json not found in the current working directory'

        roundSetManager = RoundSetManager()
        return roundSetManager.validate_asset(path)
