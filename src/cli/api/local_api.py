import os
import shutil

from typing import List, Optional, Tuple
from pathlib import Path
from cli import utils
from cli.validators import validate_json_file, validate_json_schema
from cli.managers.config_manager import ConfigManager
from cli.managers.roundset_manager import RoundSetManager
from cli.output_converter import OutputConverter
from cli.type_aliases import (AppConfigType, ApplicationType, app_configNetworkType,
                              app_configApplicationType, assetApplicationType, assetNetworkType,
                              ExperimentType, ResultType, ErrorDictType)
from cli.settings import BASE_DIR
from cli.exceptions import ApplicationAlreadyExists, NoNetworkAvailable
from cli.utils import read_json_file, write_json_file, get_network_slug, get_channels_for_network, get_channel_info, \
    get_network_nodes, get_node_info, copy_files, get_templates


class LocalApi:
    def __init__(self, config_manager: ConfigManager) -> None:
        self.__config_manager = config_manager

    def create_application(self, application_name: str, roles: List[str], path: Path) -> None:
        """
        Creates the application by checking if the application name is unique with is_application_unique and calling
        create_application_structure.

        Args:
            application_name: name of the application
            roles: a list of roles
            path: the path where the application is stored

        Raises:
            ApplicationAlreadyExists: Raised when application name is not unique
        """

        if not self.__config_manager.check_config_exists():
            self.__config_manager.create_config()

        is_unique, existing_app_path = self.__is_application_unique(application_name)
        if is_unique:
            self.__create_application_structure(application_name, roles, path)
        else:
            raise ApplicationAlreadyExists(application_name, existing_app_path)

    def init_application(self, path: Path) -> None:
        pass

    def __create_application_structure(
        self, application_name: str, roles: List[str], path: Path
    ) -> None:
        """
        Creates the application directory structure. Each application will consist of a MANIFEST.INI and two
        directories: application and config. In the directory application, the files network.json, application.json and
        result.json will be generated. In the directory config, python files will be generated according to the value of
        the list roles.

        Args:
            application_name: name of the application
            roles: a list of roles
            path: the path where the application is stored
        """

        # code to create the local application in root dir
        app_src_path = path / application_name / "src"
        app_config_path = path / application_name / "config"
        app_src_path.mkdir(parents=True, exist_ok=True)
        app_config_path.mkdir(parents=True, exist_ok=True)

        for role in roles:
            utils.write_file(app_src_path / f"app_{role}.py", utils.get_py_dummy())

        # Network.json configuration
        networks = {"networks": [], "roles": roles}
        temp_list = []

        # Check if the network there are more network nodes available for this network compared to the
        # amount of roles given by the user
        for network in utils.get_network_nodes().items():
            if len(roles) <= len(network[1]):
                temp_list.append(network[0])

        networks["networks"] = temp_list

        # Remove already created application structure
        if not networks["networks"]:
            shutil.rmtree(path / application_name)
            raise NoNetworkAvailable()

        utils.write_json_file(app_config_path / "network.json", networks)

        # Application.json configuration
        data = utils.get_dummy_application(roles)
        utils.write_json_file(app_config_path / "application.json", data)

        # Result.json configuration
        utils.write_json_file(app_config_path / "result.json", [])

        # Manifest.ini configuration
        utils.write_file(path / application_name / "MANIFEST.ini", "")

        self.__config_manager.add_application(application_name, path)

    def __is_application_unique(self, application_name: str) -> Tuple[bool, str]:
        """
        Calls config_manager.application_exists() to check if the application name already exists in the
        .qne/application.json root file. Here, all application names are added when an application is created.
        If the application name doesn't equal one of the application names already existing in this root file, the
        application is unique. Therefore, application_unique() returns True when application_exists() returns False.


        Args:
            application_name: name of the application
        """

        is_unique, path = self.__config_manager.application_exists(application_name)
        return not is_unique, path

    def list_applications(self) -> List[ApplicationType]:
        """
        Function to list the applications

        Returns:
            A list of applications
        """
        local_applications = self.__config_manager.get_applications()
        return local_applications

    # Todo: Update confluence scenario diagram since application_unique() and structure_valid() are swapped
    def is_application_valid(self, application_name: str) -> ErrorDictType:
        """
        Function that checks if:
        - The application is valid by validating if it exists in .qne/application.json
        - The file and directory structure is correct
        - The json files in the config directory contain valid json
        - The json files passes against schema validation

        Args:
            application_name: Name of the application

        returns:
            Returns empty list when all validations passes
            Returns dict containing error messages of the validations that failed
        """
        error_dict: ErrorDictType = {"error": [], "warning": [], "info": []}
        is_unique, _ = self.__is_application_unique(application_name)
        if is_unique:
            error_dict['error'].append("Application does not exist")
        else:
            self.__is_structure_valid(application_name, error_dict)
            self.__is_config_valid(application_name, error_dict)

        return error_dict

    def get_application_config(self, application: str) -> AppConfigType:
        """
        Get the configuration containing input, network and roles information for the application

        Args:
            application: Name of the application for which to get the configuration

        Returns:
            A dictionary containing application configuration information

        """
        app_details = self.__config_manager.get_application(application)

    def __is_config_valid(self, application_name: str, error_dict: ErrorDictType) -> None:
        # Validate if json string is correct and validate against json schema's
        app_schema_path = Path(BASE_DIR) / "schema/applications"
        app_config_path = Path(self.__config_manager.get_application_path(application_name)) / "config"
        files_list = ["application.json", "network.json", "result.json"]

        for file in files_list:
            if os.path.isfile(app_config_path / file):
                json_valid, message = validate_json_file(app_config_path / file)
                if json_valid:
                    schema_valid, ve = validate_json_schema(app_config_path / file, app_schema_path / file)
                    if not schema_valid:
                        error_dict['error'].append(ve)
                else:
                    # application.json is checked earlier in the validation process, no need to add this message again
                    # to error_dict (duplicate)
                    if file != "application.json":
                        error_dict['error'].append(message)

    def __is_structure_valid(self, application_name: str, error_dict: ErrorDictType) -> None:
        app_dir_path = Path(self.__config_manager.get_application_path(application_name))
        app_config_path = app_dir_path / "config"
        app_src_path = app_dir_path / "src"

        # Validate that the config, src and MANIFEST.ini structure is correct
        if not os.path.exists(app_config_path) or \
           not os.path.exists(app_src_path) or \
           not os.path.isfile(app_dir_path / "MANIFEST.ini"):
            error_dict['warning'].append(f"{app_dir_path} should contain a 'MANIFEST.ini', 'src' directory and "
                                         f"'config' directory")

        # Check if the config directory is complete
        if os.path.exists(app_config_path):
            if not os.path.isfile(app_config_path / "application.json") or \
               not os.path.isfile(app_config_path / "network.json") or \
               not os.path.isfile(app_config_path / "result.json"):
                error_dict['warning'].append(f"{app_config_path} should contain the files 'network.json', result.json' "
                                             f"and 'application.json'")

        if os.path.exists(app_src_path) and os.path.isfile(app_config_path / "application.json"):
            valid, message = validate_json_file(app_config_path / "application.json")
            if valid:
                config_application_data = read_json_file(app_config_path / "application.json")
                config_application_roles = []

                for item in config_application_data:
                    for role in item["roles"]:
                        config_application_roles.append(role)

                # Add app_ and .py to each role in config/application.json so that it matches the python files listed
                # in the src directory
                application_file_names = ['app_' + role + '.py' for role in config_application_roles]

                # Get all the files in the src directory
                src_dir_files = os.listdir(app_src_path)

                # Check if the roles in the config/application.json double the file names in the src directory
                if not all(roles in src_dir_files for roles in application_file_names):
                    error_dict['warning'].append(
                        f"Not all the roles in {app_config_path / 'application.json'} double the file names in "
                        f"{app_src_path}")
            else:
                error_dict['error'].append(message)

    def get_application_config(self, application_name: str) -> AppConfigType:
        app_config_path = Path(self.__config_manager.get_application_path(application_name)) / 'config'
        application_json_path = app_config_path / 'application.json'
        network_json_path = app_config_path / 'network.json'

        app_config_application: app_configApplicationType = read_json_file(application_json_path)
        app_config_network: app_configNetworkType = read_json_file(network_json_path)

        app_config = {"application": app_config_application, "network": app_config_network}
        return app_config

    def experiments_create(self, name: str, app_config: AppConfigType, network_name: str,
                           path: Path, application: str) -> Tuple[bool, str]:
        """
        Create all the necessary resources for experiment creation
         - 1. Get the network data for the specified network_name
         - 2. Create the asset
         - 3. Create experiment.json containing the meta data and asset information

        Args:
            name: Name of the experiment
            app_config: A dictionary containing application configuration information
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

        all_network_nodes = get_network_nodes()
        channels_list = []
        nodes_list = []

        network_slug = get_network_slug(network_name)

        if network_slug:
            channels = get_channels_for_network(network_slug=network_slug)
            for channel in channels:
                channel_info = get_channel_info(channel)
                channels_list.append(channel_info)

            if network_slug in all_network_nodes:
                for node_slug in all_network_nodes[network_slug]:
                    nodes_list.append(get_node_info(node_slug=node_slug))

        return {
            "name": network_name,
            "slug": network_slug,
            "channels": channels_list,
            "nodes": nodes_list,
        }

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
        """
        Prepare the asset by filling the application input parameters with default values

        Args:
            app_config: A dictionary containing application configuration information

        Returns:
            Filled Application input parameters with default values

        """
        input_list = []
        if "application" in app_config:
            for input in app_config["application"]:
                item = {
                    "slug": input["slug"],
                    "roles": input["roles"],
                    "values": []
                }
                for value in input["values"]:
                    value_item = {
                        "name": value["name"],
                        "value": value["default_value"],
                        "scale_value": value["scale_value"]
                    }
                    item["values"].append(value_item)

            input_list.append(item)

        return input_list

    def create_asset_network(self,  network_data: assetNetworkType, app_config: AppConfigType) -> assetNetworkType:
        """
        Prepare the asset by filling the network parameters with default values

        Args:
            app_config: A dictionary containing application configuration information

        Returns:
            Filled Network parameters with default values

        """
        # {
        #     "name": network_name,
        #     "slug": network_slug,
        #     "channels": channels_list,
        #     "nodes": nodes_list,
        # }
        templates = get_templates()
        node_list = network_data["nodes"]
        channel_list = network_data["channels"]

        # Fill roles information
        network_data["roles"] = {}
        if "network" in app_config:
            if "roles" in app_config["network"]:
                role_list = app_config["network"]["roles"]
                for index, role in enumerate(role_list):
                    network_data["roles"][role] = node_list[index]["slug"]

        # Fill channel info (parameters)
        for channel in channel_list:
            channel["filled_parameters"] = []
            for param in channel["parameters"]:
                filled_parameter_item = {
                    "slug": param,
                    "values": []
                }
                template_data_value = templates[param]["values"]
                for val in template_data_value:
                    item = {
                        "name": val["name"],
                        "value": val["default_value"],
                        "scale_value": val["scale_value"]
                    }
                    filled_parameter_item["values"].append(item)

                channel["filled_parameters"].append(filled_parameter_item)

            channel["parameters"] = channel["filled_parameters"]
            del channel["filled_parameters"]

        # Fill Nodes info(Parameters)

        return network_data

    def __copy_input_files_from_application(self,  application: str, input_directory: Path) -> None:
        """
        Copy the input/source files of the 'application' to the 'input_directory'

        Args:
            application: The application name for which the input files need to be copied
            input_directory: The destination where application files need to be stored

        """
        application_exists, app_path = self.__config_manager.application_exists(application=application)
        app_path = Path(app_path)
        if application_exists:
            copy_files(app_path / "config", input_directory)
            copy_files(app_path / "src", input_directory)

    def is_network_available(self, network_name: str, app_config: AppConfigType) -> bool:
        """
        Check if the network_name is available for use in the application's app_config

        Args:
            network_name: The network name
            app_config: Application Configuration containing the available networks

        Returns:
            bool: True if the given network name is available in application configuration, False otherwise
        """
        network_slug = get_network_slug(network_name)
        if network_slug:
            if "network" in app_config:
                if network_slug in app_config["network"]:
                    return True

        return False

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
