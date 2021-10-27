import os
from cli.exceptions import ApplicationAlreadyExists, NoNetworkAvailable, NetworkNotFound
from cli import utils
from typing import Any, cast, Dict, List, Optional
from pathlib import Path
import shutil
from cli import utils
from cli.exceptions import (ApplicationAlreadyExists, DirectoryAlreadyExists, JsonFileNotFound, NetworkNotFound,
                            NoNetworkAvailable, PackageNotComplete)
from cli.managers.config_manager import ConfigManager
from cli.managers.roundset_manager import RoundSetManager
from cli.output_converter import OutputConverter
from cli.settings import BASE_DIR
from cli.type_aliases import (AppConfigType, ApplicationType, app_configNetworkType,
                              app_configApplicationType, assetApplicationType, assetNetworkType,
                              ExperimentType, ErrorDictType, GenericNetworkData, ResultType,
                              ChannelData, NetworkData, NodeData, TemplateData)
from cli.validators import validate_json_file, validate_json_schema
from cli.utils import (read_json_file, write_json_file, get_py_dummy, write_file,
                       get_dummy_application)


class LocalApi:
    def __init__(self, config_manager: ConfigManager) -> None:
        self.__config_manager = config_manager
        self.__read_network_data()

    def __read_network_data(self) -> None:
        """
            Initialize the data for 'networks', 'channels', 'nodes', 'templates'
        """
        self.__networks_data: NetworkData = self.__read_generic_data("networks")
        self.__channels_data: ChannelData = self.__read_generic_data("channels")
        self.__nodes_data: NodeData = self.__read_generic_data("nodes")
        self.__templates_data: TemplateData = self.__read_generic_data("templates")

    def __read_generic_data(self, entity_name: str) -> GenericNetworkData:
        """
            Reads the json file specified by the parameter 'entity_name'.
            entity_name can be 'networks', 'channels', 'nodes', 'templates'

            Params:
                entity_name: The type of the data to read

            Returns:
                Data read from the json file
        """
        file_name = Path(BASE_DIR) / f"networks/{entity_name}.json"
        try:
            generic_data: GenericNetworkData = utils.read_json_file(file_name)
        except JsonFileNotFound:
            raise PackageNotComplete(str(file_name)) from None

        return generic_data

    def _get_network_info(self, identifier_value: str, identifier_type: str = "slug") -> Optional[Dict[str, Any]]:
        """
        Get the network information containing name, slug and channel list

        Args:
            identifier_value: Value of the identifier used to select/match the network
            identifier_type: Possible values for identifier_type are slug, name. Default is slug

        Returns:
            Network information containing name, slug, and channel list
        """

        for _, data in self.__networks_data["networks"].items():
            if data[identifier_type].lower() == identifier_value.lower():
                return data

        return None

    def _get_network_slug(self, network_name: str) -> Optional[str]:
        """
        Get the slug associated with the network based on the name of the network

        Args:
            network_name: Name of the network

        Returns:
            The slug for the given network
        """
        network_data = self._get_network_info(identifier_value=network_name, identifier_type="name")
        if network_data:
            if 'slug' in network_data:
                return str(network_data['slug'])

        return None

    def _get_network_name(self, network_slug: str) -> Optional[str]:
        """
        Get the name associated with the network based on the slug of the network

        Args:
            network_slug: Slug of the network

        Returns:
            The Name for the given network
        """
        network_data = self._get_network_info(network_slug)
        if network_data:
            if 'name' in network_data:
                return str(network_data['name'])

        return None

    def _get_qne_network_name(self, network_name: str) -> Optional[str]:
        """
        Get the case-sensitive name of the network as defined in the networks.json

        Args:
            network_name: Provided name of the network (can be in any case)

        Returns:
            The Name for the given network as available in the networks.json
        """
        network_data = self._get_network_info(identifier_value=network_name, identifier_type="name")
        if network_data:
            if 'name' in network_data:
                return str(network_data['name'])

        return None

    def _get_channels_for_network(self, network_slug: str) -> Optional[List[str]]:
        """
        Get the list of channels available in the network

        Args:
            network_slug: Slug of the network

        Returns:
            List of channels
        """
        network_data = self._get_network_info(network_slug)
        if network_data:
            if 'channels' in network_data:
                return cast(List[str], network_data['channels'])

        return None

    def _get_channel_info(self, channel_slug: str) -> Optional[Dict[str, Any]]:
        """
        Get the channel information containing node & parameter information

        Args:
            channel_slug: Slug of the channel

        Returns:
            Channel information containing node & parameter information
        """

        for channel in self.__channels_data["channels"]:
            if channel["slug"] == channel_slug:
                return channel

        return None

    def _get_node_info(self, node_slug: str) -> Optional[Dict[str, Any]]:
        """
        Get the node information containing node parameters & qubit information

        Args:
            node_slug: Slug of the Node

        Returns:
            Node information containing node parameters & information
        """

        for node in self.__nodes_data["nodes"]:
            if node["slug"] == node_slug:
                return node

        return None

    def _get_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all the templates information

        Returns:
            A dictionary containing key as template slug and value as template information
        """
        return {template["slug"]: template for template in self.__templates_data["templates"]}


    def _get_nodes(self) -> Dict[str, List[str]]:
        """
        Loops trough all the networks in networks/networks.json and gets all the nodes within this network.
        returns:
        Returns a dict of networks, each having their own list including the nodes:
        E.g.: {"randstad": ["leiden", "amsterdam", "the_hague"], "the-netherlands": ["etc..",]}
        """
        networks_file = Path(BASE_DIR) / "networks/networks.json"
        channels_file = Path(BASE_DIR) / "networks/channels.json"

        # Read network
        network_nodes: Dict[str, List[str]] = {}

        data_networks = read_json_file(networks_file)
        data_channels = read_json_file(channels_file)

        for network in data_networks["networks"]:
            for channel in data_channels["channels"]:
                if channel["slug"] in data_networks["networks"][network]["channels"]:
                    if data_networks["networks"][network]["slug"] not in network_nodes:
                        network_nodes[data_networks["networks"][network]["slug"]] = []
                    lst = network_nodes[data_networks["networks"][network]["slug"]]
                    if channel["node1"] not in lst:
                        lst.append(channel["node1"])
                    if channel["node2"] not in lst:
                        lst.append(channel["node2"])

        return network_nodes

    def _get_network_nodes(self, network_slug: str) -> List[str]:

        """
        Loops trough all the networks in networks/networks.json and returns all the nodes belonging to network
        specified as 'network_slug'.
        returns:
        Returns a dict of a network, containing all nodes belonging to this network:
        E.g.: {"randstad": ["leiden", "amsterdam", "the_hague"]}
        """

        # Read network and see which are available
        network_nodes: List[str] = []

        data_networks = self.__networks_data
        data_channels = self.__channels_data

        for network in data_networks["networks"]:
            if data_networks["networks"][network]['slug'] == network_slug:
                for channel in data_channels["channels"]:
                    if channel["slug"] in data_networks["networks"][network]["channels"]:
                        if channel["node1"] not in network_nodes:
                            network_nodes.append(channel["node1"])
                        if channel["node2"] not in network_nodes:
                            network_nodes.append(channel["node2"])

        return network_nodes

    def create_application(self, application_name: str, roles: List[str], path: Path) -> None:
        """
        Creates the application by checking if the application name does not exist and calling
        create_application_structure.

        Args:
            application_name: name of the application
            roles: a list of roles
            path: the path where the application is stored

        Raises:
            ApplicationAlreadyExists: Raised when application name is not unique
        """
        application_exists, existing_application_path = self.__config_manager.application_exists(application_name)
        if application_exists:
            raise ApplicationAlreadyExists(application_name, existing_application_path)

        self.__create_application_structure(application_name, roles, path)

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
        Raises:
            DirectoryAlreadyExists: Raised when directory (or file) application_name already exists
        """
        application_name = application_name.lower()

        # check if application path is already an existing dir/file
        application_path = path / application_name
        if application_path.exists():
            raise DirectoryAlreadyExists('Application', str(application_path))

        # code to create the local application in root dir
        app_src_path = application_path / "src"
        app_config_path = application_path / "config"
        app_src_path.mkdir(parents=True, exist_ok=True)
        app_config_path.mkdir(parents=True, exist_ok=True)

        for role in roles:
            utils.write_file(app_src_path / f"app_{role}.py", utils.get_py_dummy())


        # Network.json configuration
        networks = {"networks": [], "roles": roles}
        temp_list = []

        # Check if the network there are more network nodes available for this network compared to the
        # amount of roles given by the user

        for network in self._get_nodes().items():
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

    def list_applications(self) -> List[ApplicationType]:
        """
        Function to list the applications

        Returns:
            A list of applications
        """
        local_applications = self.__config_manager.get_applications()
        return local_applications

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
        application_exists, _ = self.__config_manager.application_exists(application_name)
        if application_exists:
            self.__is_structure_valid(application_name, error_dict)
            self.__is_config_valid(application_name, error_dict)
        else:
            error_dict['error'].append(f"Application '{application_name}' does not exist")

        return error_dict

    def get_application_config(self, application_name: str) -> Optional[AppConfigType]:
        """
        Get the configuration containing input, network and roles information for the application

        Args:
            application_name: Name of the application for which to get the configuration

        Returns:
            A dictionary containing application configuration information

        """
        app_details = self.__config_manager.get_application(application_name)

        if app_details and 'path' in app_details:
            app_config_path = Path(app_details['path']) / 'config'
            application_json_path = app_config_path / 'application.json'
            network_json_path = app_config_path / 'network.json'

            app_config_application: app_configApplicationType = utils.read_json_file(application_json_path)
            app_config_network: app_configNetworkType = utils.read_json_file(network_json_path)

            app_config = {"application": app_config_application, "network": app_config_network}
            return app_config

        return None

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

    def __get__config_file_names(self) -> List[str]:
        return ['application.json', 'network.json', 'result.json']

    def __get_role_file_names(self, app_config_path: Path) -> List[str]:
        config_network_data = read_json_file(app_config_path / "network.json")
        config_application_roles = config_network_data['roles'] if 'roles' in config_network_data else []

        # Add app_ and .py to each role in config/network.json so that it matches the python files listed
        # in the src directory
        application_file_names = ['app_' + role + '.py' for role in config_application_roles]
        return application_file_names

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
                application_file_names = self.__get_role_file_names(app_config_path)

                # Get all the files in the src directory
                src_dir_files = os.listdir(app_src_path)

                # Check if the roles in the config/application.json double the file names in the src directory
                if not all(roles in src_dir_files for roles in application_file_names):
                    error_dict['warning'].append(
                        f"Not all the roles in {app_config_path / 'application.json'} double the file names in "
                        f"{app_src_path}")
            else:
                error_dict['error'].append(message)

    def experiments_create(self, experiment_name: str, app_config: AppConfigType, network_name: str,
                           path: Path, application_name: str) -> None:
        """
        Create all the necessary resources for experiment creation
         - 1. Get the network data for the specified network_name
         - 2. Create the asset
         - 3. Create experiment.json containing the meta data and asset information

        Args:
            experiment_name: Name of the experiment
            app_config: A dictionary containing application configuration information
            network_name: Name of the network to use
            path: Location where the experiment directory is to be created
            application_name: Name of the application for which to create experiment

        """
        network_data: assetNetworkType = self.get_network_data(network_name=network_name)
        asset_network: assetNetworkType = self.create_asset_network(network_data=network_data,
                                                                    app_config=app_config)

        self.create_experiment(experiment_name=experiment_name, app_config=app_config, asset_network=asset_network,
                               path=path, application_name=application_name)

    def get_network_data(self, network_name: str) -> assetNetworkType:
        """
        Fetch the data for the specified network_name from the json files in networks folder
        Args:
            network_name: Name of the network whose data needs to be fetched
        Returns:
            The complete network information with channels & nodes
        """

        channels_list = []
        nodes_list = []

        network_slug = self._get_network_slug(network_name)

        if network_slug:
            channels = self._get_channels_for_network(network_slug=network_slug)
            if channels:
                for channel_slug in channels:
                    channel_info = self._get_channel_info(channel_slug=channel_slug)
                    channels_list.append(channel_info)

            all_network_nodes = self._get_network_nodes()
            if network_slug in all_network_nodes:
                for node_slug in all_network_nodes[network_slug]:
                    nodes_list.append(self._get_node_info(node_slug=node_slug))
            else:
                raise NetworkNotFound(network_name)

            qne_network_name = self._get_qne_network_name(network_name)

            return {
                "name": qne_network_name,
                "slug": network_slug,
                "channels": channels_list,
                "nodes": nodes_list,
            }

        raise NetworkNotFound(network_name)

    def create_experiment(
        self, experiment_name: str, app_config: AppConfigType, asset_network: assetNetworkType, path: Path,
            application_name: str) -> None:
        """
        Create experiment.json with meta and asset information

        Args:
            experiment_name: Name of the directory where experiment.json will be created
            app_config: A dictionary containing application configuration information
            asset_network: Filled Network parameters with default values
            path: Location where experiment directory needs to be created
            application_name: Name of the application for which to create the experiment

        """

        experiment_path = path / experiment_name
        experiment_path.mkdir(parents=True)

        input_directory = experiment_path / 'input'
        input_directory.mkdir(parents=True)
        self.__copy_input_files_from_application(application_name, input_directory)

        experiment_json_file = experiment_path / 'experiment.json'
        experiment_meta = {
            "backend": {
                "location": "local",
                "type": "local_netsquid"
            },
            "number_of_rounds": 1,
            "description": f"{experiment_name}: experiment description"
        }

        asset_application = self.__create_asset_application(app_config)
        asset = {"network": asset_network, "application": asset_application}

        experiment_data = {'meta': experiment_meta, 'asset': asset}
        utils.write_json_file(experiment_json_file, experiment_data)

    def __create_asset_application(self, app_config: AppConfigType) -> assetApplicationType:
        """
        Prepare the asset by filling the application input parameters with default values

        Args:
            app_config: A dictionary containing application configuration information

        Returns:
            Filled Application input parameters with default values

        """
        input_list = []
        if "application" in app_config:
            for input_param in app_config["application"]:
                item = {
                    "roles": input_param["roles"],
                    "values": []
                }
                for value in input_param["values"]:
                    value_item = {
                        "name": value["name"],
                        "value": value["default_value"],
                        "scale_value": value["scale_value"]
                    }
                    item["values"].append(value_item)

                input_list.append(item)

        return input_list

    def create_asset_network(self, network_data: assetNetworkType, app_config: AppConfigType) -> assetNetworkType:
        """
        Prepare the asset by filling the network parameters with default values

        Args:
            network_data: Network information containing channels and nodes list
            app_config: A dictionary containing application configuration information

        Returns:
            Filled Network parameters with default values

        """
        # pylint: disable-msg=too-many-locals

        templates = {template["slug"]: template for template in self.__templates_data["templates"]}
        node_list = network_data["nodes"]
        channel_list = network_data["channels"]

        # Fill roles information
        network_data["roles"] = {}
        if "network" in app_config:
            if "roles" in app_config["network"]:
                for index, role in enumerate(app_config["network"]["roles"]):
                    network_data["roles"][role] = node_list[index]["slug"]

        # Fill channel information (parameters)
        for channel in channel_list:
            filled_params_channel = []
            for param in channel["parameters"]:
                filled_parameter_item = self.__get_filled_template_parameter(param=param, templates=templates)
                filled_params_channel.append(filled_parameter_item)

            channel["parameters"] = filled_params_channel

        # Fill Nodes information (parameters)
        for node in node_list:
            filled_params_node = []
            for param in node["node_parameters"]:
                filled_parameter_item = self.__get_filled_template_parameter(param=param, templates=templates)
                filled_params_node.append(filled_parameter_item)

            node["node_parameters"] = filled_params_node

            number_of_qubits = node["number_of_qubits"]
            node["qubits"] = []
            for qubit_number in range(number_of_qubits):
                qubit_item: Dict[str, Any] = {
                    "qubit_id": qubit_number,
                    "qubit_parameters": []
                }
                for param in node["qubit_parameters"]:
                    filled_parameter_item = self.__get_filled_template_parameter(param=param, templates=templates)
                    qubit_item["qubit_parameters"].append(filled_parameter_item)

                node["qubits"].append(qubit_item)

            del node["number_of_qubits"]
            del node["qubit_parameters"]

        return network_data

    def __get_filled_template_parameter(self, param: str, templates: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepare the template parameter by filling it with default values

        Args:
            param: Name of the template parameter
            templates: A dictionary containing information for all template parameters

        Returns:
            Filled Template parameter with default values

        """
        filled_parameter_item: Dict[str, Any] = {
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

        return filled_parameter_item


    def __copy_input_files_from_application(self, application_name: str, input_directory: Path) -> None:
        """
        Copy the input/source files of the 'application' to the 'input_directory'

        Args:
            application_name: The application name for which the input files need to be copied
            input_directory: The destination where application files need to be stored

        """
        application_exists, app_path = self.__config_manager.application_exists(application_name=application_name)
        if application_exists:
            app_path = Path(app_path)
            utils.copy_files(app_path / "config", input_directory, files_list=self.__get__config_file_names())
            utils.copy_files(app_path / "src", input_directory,
                             files_list=self.__get_role_file_names(app_config_path=app_path / "config"))

    def is_network_available(self, network_name: str, app_config: AppConfigType) -> bool:
        """
        Check if the network_name is available for use in the application's app_config

        Args:
            network_name: The network name
            app_config: Application Configuration containing the available networks

        Returns:
            bool: True if the given network name is available in application configuration, False otherwise
        """
        network_slug = self._get_network_slug(network_name)
        if network_slug:
            if "network" in app_config:
                if "networks" in app_config["network"]:
                    if network_slug in app_config["network"]["networks"]:
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
        round_set_manager = RoundSetManager()
        round_set_manager.prepare_input(path)
        round_set_manager.process()
        round_set_manager.terminate()
        return []

    def get_experiment(self, name: str) -> ExperimentType:
        pass

    def get_results(self, path: Path, all_results: bool) -> List[ResultType]:
        output_converter = OutputConverter('log_dir', 'output_dir')

        result_list: List[ResultType] = []
        output_result: List[ResultType] = []

        total_rounds = self.get_experiment_rounds(path)
        if all_results:
            for round_number in range(1, total_rounds + 1):
                output_result.append(output_converter.convert(round_number, result_list))
        else:
            output_result.append(output_converter.convert(total_rounds, result_list))

        return output_result

    def validate_experiment(self, path: Path) -> ErrorDictType:
        # TODO: Add any other validation which should be done
        """
        Validates the experiment by checking:
        - if the structure is correct and consists of an experiment.json
        - (For local run) experiment directory contains an input directory with the correct files
        - content of experiment.json is valid JSON
        - asset in the experiment.json validated against a schema validator.
        - if the network used in experiment.json is existing
        - if the nodes and channels used in experiment.json are correct and valid for that network
<<<<<<< HEAD
=======

>>>>>>> commit for rebase
        Args:
            path: The location of the experiment
        Returns:
            ErrorDictType: Dict[str, List[str]]: Dictionary containing error, warning and info messages of the
            validations that failed
        """

        experiment_json = path / 'experiment.json'
        local = True
        error_dict: ErrorDictType = {"error": [], "warning": [], "info": []}

        # Check if experiment.json exists
        if not experiment_json.is_file():
            error_dict['error'].append(f'File not found: {experiment_json} does not exist')

        # Check if experiment is local or remote
        if experiment_json.is_file():
            is_valid, message = validate_json_file(experiment_json)
            if is_valid:
                experiment = read_json_file(experiment_json)
                if not experiment['meta']['backend']['location'] == "local":
                    local = False
            else:
                error_dict['error'].append(message)

        self.validate_experiment_structure(path=path, local=local, error_dict=error_dict)
        self.validate_experiment_json_files(path=path, error_dict=error_dict)

        return error_dict

    # TODO: Update confluence sequence diagram with new function
    def validate_experiment_structure(self, path: Path, local: bool, error_dict: ErrorDictType) -> None:
        """
        Validates if the experiment file structures contains a:
        - experiment.json
        - (Only local) input directory containing network.yaml, roles.yaml, role1.yaml, role2.yaml, ...,
        app_role1.py, app_role2.py, ...
        Args:
            path: The location of the experiment
            local: If the experiment is a local or not
            error_dict: Dictionary containing error and warning messages of the validations that failed
        """

        experiment_input_path = path / 'input'
        network_schema_path = Path(os.path.join(BASE_DIR, 'schema', 'applications', 'network.json', ''))
        is_network_json_valid = False
        is_network_schema_valid = False

        if (experiment_input_path / 'network.json').is_file():
            is_network_json_valid, _ = validate_json_file(experiment_input_path / 'network.json')
            if is_network_json_valid:
                is_network_schema_valid, _ = validate_json_schema(experiment_input_path / 'network.json',
                                                                  network_schema_path)
        else:
            error_dict['warning'].append(f"File not found. {experiment_input_path / 'network.json'} does not exist")

        if is_network_json_valid and is_network_schema_valid:
            application_network_data = read_json_file(experiment_input_path / 'network.json')

            # Get the roles from network.json
            roles = []
            for role in application_network_data['roles']:
                roles.append(role.lower())

            # Local validation
            if local:
                if not experiment_input_path.exists():
                    error_dict['warning'].append(f"Directory not found. {experiment_input_path} does not exist")

                # TODO: Update Confluence with json files instead of yaml files (network.json, application.json and
                #  result.json
                # network.json is checked in an earlier validation, so no need to check again
                if experiment_input_path.exists():
                    if not (experiment_input_path / 'application.json').exists() \
                        or not (experiment_input_path / 'result.json').exists():
                        error_dict['warning'].append(f"{experiment_input_path} needs to contain the files "
                                                     f"'network.json', 'application.json' and 'result.json'")

                    # Check if the roles from network.json exist in the experiment/input directory
                    missing_files = []
                    for item in ['app_' + s + '.py' for s in roles]:
                        if not (experiment_input_path / item).is_file():
                            missing_files.append(item)

                    if missing_files:
                        error_dict['warning'].append(f"{experiment_input_path} is missing the files: {missing_files}")

    # TODO:
    #  - Update confluence sequence diagram with new function
    #  - Roundsetmanager validate_asset() should be used in the future when multiple rounds are used.
    def validate_experiment_json_files(self, path: Path, error_dict: ErrorDictType) -> None:
        """
        This function validates if experiment.json contains valid json and if it passes schema validation.
        Args:
            path: The location of the experiment
            error_dict: Dictionary containing error and warning messages of the validations that failed
        """

        experiment_file_path = path / 'experiment.json'
        experiment_input_path = path / 'input'

        # Validate experiment.json
        if os.path.isfile(experiment_file_path):
            experiment_schema = Path(os.path.join(BASE_DIR, 'schema', 'experiments', 'experiment.json', ''))

            json_valid, message = validate_json_file(experiment_file_path)
            if json_valid:
                schema_valid, ve = validate_json_schema(experiment_file_path, experiment_schema)
                if not schema_valid:
                    error_dict['error'].append(ve)

                experiment_data = read_json_file(experiment_file_path)
                experiment_network_slug = experiment_data['asset']['network']['slug']

                # Check if the chosen network exists
                if self._get_network_info(experiment_network_slug):
                    # Validate experiment nodes
                    self.validate_experiment_nodes(experiment_file_path, experiment_data, error_dict)
                    # Validate experiment channels
                    self.validate_experiment_channels(experiment_file_path, experiment_data, error_dict)
                else:
                    error_dict['warning'].append(f"In file {experiment_file_path}: network '{experiment_network_slug}' "
                                                 f"does not exist")

                self.validate_experiment_application(path, experiment_data, error_dict)

        # Validate application.json, network.json and result.json
        if os.path.exists(experiment_input_path):
            app_schema_path = Path(os.path.join(BASE_DIR), 'schema', 'applications', '')
            files_list = ["application.json", "network.json", "result.json"]

            for file in files_list:
                if os.path.isfile(experiment_input_path / file):
                    json_valid, message = validate_json_file(experiment_input_path / file)
                    if json_valid:
                        schema_valid, ve = validate_json_schema(experiment_input_path / file, app_schema_path / file)
                        if not schema_valid:
                            error_dict['error'].append(ve)
                    else:
                        error_dict['error'].append(message)

    def validate_experiment_nodes(self, experiment_file_path: Path, experiment_data: Dict[str, Any], error_dict:
                                  ErrorDictType) -> None:
        """
        Validate if the amount of nodes (defined in the experiment.json file) are valid for 'network_slug' and if
        all the nodes exist and belong to this network.
        Args:
            experiment_file_path: The location of the experiment.json file
            experiment_data: contents of the experiment.json file
            error_dict: Dictionary containing error and warning messages of the validations that failed
        """
        experiment_network_slug = experiment_data['asset']['network']['slug']

        # Check if the amount of nodes are valid for this network
        experiment_nodes = experiment_data['asset']['network']['nodes']
        network_nodes = self._get_network_nodes(experiment_network_slug)
        if len(experiment_nodes) > len(network_nodes):
            error_dict['warning'].append(f"In file {experiment_file_path}: too many nodes used in network "
                                         f"'{experiment_network_slug}'. Maximum amount of nodes that can be used: "
                                         f"{len(network_nodes)}")

        # Check if all nodes exist and belong to this network
        invalid_nodes = []
        for node in experiment_nodes:
            if node['slug'] not in network_nodes:
                invalid_nodes.append(node['slug'])
        if invalid_nodes:
            if len(invalid_nodes) > 1:
                error_dict['warning'].append(
                    f"In file {experiment_file_path}: {invalid_nodes} do not exist or do not belong to"
                    f" the network '{experiment_network_slug}'")
            elif len(invalid_nodes) == 1:
                error_dict['warning'].append(f"In file {experiment_file_path}: {invalid_nodes} does not exist or does "
                                             f"not belong to the network '{experiment_network_slug}'")

    def validate_experiment_channels(self, experiment_file_path: Path, experiment_data: Dict[str, Any], error_dict:
                                     ErrorDictType):
        """
        Validate if the amount of channels (defined in the experiment.json file) are valid for 'network_slug' and if
        all the channels exist and belong to this network.

        Args:
            experiment_file_path: The location of the experiment.json file
            experiment_data: contents of the experiment.json file
            error_dict: Dictionary containing error and warning messages of the validations that failed
        """

        # Check if the amount of channels are valid for this network
        experiment_network_slug = experiment_data['asset']['network']['slug']
        experiment_channels = experiment_data['asset']['network']['channels']
        network_channels = self._get_channels_for_network(experiment_network_slug)

        if len(experiment_channels) > len(network_channels):
            error_dict['warning'].append(f"In file {experiment_file_path}: too many channels used in network "
                                         f"'{experiment_network_slug}'. Maximum amount of channels that can be used: "
                                         f"{len(network_channels)}")

        # Check if the channels exist and belong to this network
        invalid_channels = []
        for channel in experiment_channels:
            # Replace '_' with '-'. Eg: the_hague can be written this way in experiment.json while the comparison is
            # done with the-hague defined in network/channels.json
            node_slug1 = channel['node_slug1'].replace('_', '-')
            node_slug2 = channel['node_slug2'].replace('_', '-')
            if not node_slug1 + '-' + node_slug2 in network_channels:
                if not node_slug2 + '-' + node_slug1 in network_channels:
                    invalid_channels.append([channel['node_slug1'], channel['node_slug2']])

        if invalid_channels:
            if len(invalid_channels) > 1:
                error_dict['warning'].append(f"In file {experiment_file_path}: {invalid_channels} do not exist or are "
                                             f"not valid channels for network '{experiment_network_slug}'")
            elif len(invalid_channels) == 1:
                error_dict['warning'].append(f"In file {experiment_file_path}: {invalid_channels} does not exist or is "
                                             f"not a valid channel for network '{experiment_network_slug}'")

    def validate_experiment_application(self, path: Path, experiment_data: Dict[str, Any],
                                        error_dict: ErrorDictType) -> None:
        """
        Validate the ['application'] key defined in the asset of experiment.json. Check if the roles double the roles
        that are defined in input/network.json

        Args:
            path: The location of the experiment
            experiment_data: contents of the experiment.json file
            error_dict: Dictionary containing error and warning messages of the validations that failed
        """

        experiment_application_data = experiment_data['asset']['application']
        experiment_input_path = path / 'input'
        network_schema_path = Path(os.path.join(BASE_DIR, 'schema', 'applications', 'network.json', ''))

        # Check if the roles defined in experiment.json ['application'] double the roles defined in input/network.json
        if (experiment_input_path / 'network.json').is_file():
            is_network_json_valid, _ = validate_json_file(experiment_input_path / 'network.json')
            if is_network_json_valid:
                is_network_schema_valid, _ = validate_json_schema(experiment_input_path / 'network.json',
                                                                  network_schema_path)
                if is_network_schema_valid:
                    application_network_data = read_json_file(experiment_input_path / 'network.json')
                    for item in experiment_application_data:
                        experiment_roles = item["roles"]
                        application_roles = application_network_data['roles']
                        if not all(role in experiment_roles for role in application_roles):
                            error_dict['warning'].append(f"In file {path / 'experiment.json'}: experiment roles "
                                                         f"{experiment_roles} does not double with the roles "
                                                         f"{application_roles}' in "
                                                         f"{experiment_input_path / 'network.json'}")

