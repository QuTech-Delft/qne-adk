from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import time

from apistar import Client
from apistar.client.auth import TokenAuthentication
from apistar.exceptions import ErrorResponse

from adk import utils
from adk.api.qne_client import QneFrontendClient
from adk.exceptions import ExperimentFailed, JobTimeoutError
from adk.generators.result_generator import ResultGenerator
from adk.managers.config_manager import ConfigManager
from adk.managers.auth_manager import AuthManager
from adk.type_aliases import (AppConfigType, ApplicationType, AssetType, ErrorDictType, ExperimentType,
                              FinalResultType, GenericNetworkData, ExperimentDataType, ResultType, RoundSetType)
from adk.settings import BASE_DIR


# The status of the qne_job can be 'NEW', 'RUNNING', 'COMPLETE', 'FAILED'
class JobStatus:
    NEW: str = 'NEW'
    RUNNING: str = 'RUNNING'
    COMPLETE: str = 'COMPLETE'
    FAILED: str = 'FAILED'


# The final status of the qne_job, either successful or not
QNE_JOB_FINAL_STATES = (
    JobStatus.COMPLETE,
    JobStatus.FAILED,
)
# The status of the qne_job when it is executed successfully
QNE_JOB_SUCCESS_STATES = (
    JobStatus.COMPLETE,
)


class RemoteApi():
    def __init__(self, config_manager: ConfigManager) -> None:
        self.__config_manager: ConfigManager = config_manager
        config_dir = self.__config_manager.get_config_dir()
        self.auth_manager: AuthManager = AuthManager(config_dir,
                                                     self.__login_user, self.__login_anonymous, self.__logout_user)

        self.__qne_client = QneFrontendClient(self.auth_manager)
        self.__base_uri = self.auth_manager.get_active_host()
        self.__username: Optional[str] = self.auth_manager.get_username(self.__base_uri)
        self.__password: Optional[str] = self.auth_manager.get_password(self.__base_uri)
        self.__refresh_token: Optional[str] = self.auth_manager.load_token(self.__base_uri)

        self.__headers: Dict[str, str] = {}
        self.__openapi_client_class = Client
        self.__auth_class = TokenAuthentication
        self.__client: Client = None

    def __login_user(self, username: str, password: str, host: str) -> Optional[str]:
        self.__refresh_token = None
        self.__base_uri = host
        self.__username = username
        self.__password = password

        self.__refresh_token = self.__qne_client.login(username, password, host)
        return self.__refresh_token

    def __login_anonymous(self) -> str:
        pass

    def login(self, username: str, password: str, host: str) -> None:
        self.auth_manager.login(username, password, host)

    def __logout_user(self, host: str) -> None:
        self.__qne_client.logout(host)

    def logout(self, host: str) -> bool:
        if not self.__qne_client.is_logged_in():
            return False
        self.auth_manager.logout(host)
        return True

    def get_active_host(self) -> str:
        return self.__base_uri

    def list_applications(self) -> List[ApplicationType]:
        return self.__qne_client.list_applications()

    def delete_application(self, application_id: Optional[str]) -> bool:
        """experiment id is the experiment to delete. When not found 404 or another error return False
        return True when no error was raised
        """
        if application_id is not None and application_id.isdigit():
            try:
                self.__qne_client.destroy_application(f"/fake_url/{application_id}/")
            except ErrorResponse:
                return False

            # experiment deleted (inclusive all assets/round_sets and results)
            return True
        return False

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

    def __get_application_by_slug(self, application_slug: str) -> Optional[ApplicationType]:
        app_list = self.list_applications()
        for application in app_list:
            if application["slug"] == application_slug.lower():
                return application
        return None

    def get_application_config(self, application_slug: str) -> Optional[AppConfigType]:
        application = self.__get_application_by_slug(application_slug)
        if application is not None:
            return self.__qne_client.app_config_application(application["url"])
        return None

    def is_application_valid(self, application_slug: str) -> ErrorDictType:
        """
        Function that checks if:
        - The application is valid by validating if it exists remotely

        Args:
            application_slug: Slug of the application

        returns:
            Returns empty list when all validations passes
            Returns dict containing error messages of the validations that failed
        """
        error_dict: ErrorDictType = utils.get_empty_errordict()
        if None is self.__get_application_by_slug(application_slug):
            error_dict["error"].append(f"Application '{application_slug}' does not exist remotely")

        return error_dict

    def delete_experiment(self, experiment_id: Optional[str]) -> bool:
        """experiment id is the experiment to delete. When not found 404 or another error return False
        return True when no error was raised. The experiment is deleted (including all assets/round_sets/results)
        """
        if experiment_id is not None and experiment_id.isdigit():
            try:
                self.__qne_client.destroy_experiment(f"/fake_url/{experiment_id}/")
            except ErrorResponse:
                return False

            return True
        return False

    def experiments_list(self) -> List[ExperimentType]:
        experiment_list = self.__qne_client.list_experiments()
        for experiment in experiment_list:
            app_version = self.__qne_client.retrieve_appversion(experiment["app_version"])
            application = self.__qne_client.retrieve_application(app_version["application"])
            experiment["name"] = application["slug"]

        return experiment_list

    def __create_experiment(self, application_slug: str, app_version: str) -> Optional[ExperimentType]:
        user = self.__qne_client.retrieve_user()
        application = self.__get_application_by_slug(application_slug)
        if application is not None and user is not None:
            app_config = self.get_application_config(application_slug)
            app_version_url = app_config["app_version"]

            if app_version_url != app_version:
                # TODO error: app config based on another version of the application
                return None
            user_url = user["url"]
            experiment: ExperimentType = {
                "app_version": app_version_url,
                "personal_note": "Experiment created by qne-adk",
                "is_marked": False,
                "owner": user_url
            }
            return experiment

        return None

    def __create_round_set(self, asset_url: str, number_of_rounds: int) -> RoundSetType:
        round_set: RoundSetType = {
          "number_of_rounds": number_of_rounds,
          "status": "NEW",
          "input": asset_url
        }
        return round_set

    def __translate_asset(self, asset_to_create: AssetType, experiment_url: str) -> AssetType:
        experiment_channels = asset_to_create["network"]["channels"]
        new_channels = []
        for channel in experiment_channels:
            new_channel = {}
            new_channel["node_slug1"] = channel["node1"]
            new_channel["node_slug2"] = channel["node2"]
            new_channel["parameters"] = channel["parameters"]
            new_channels.append(new_channel)

        asset_to_create["network"]["channels"] = new_channels
        asset_to_create["experiment"] = experiment_url
        return asset_to_create

    def run_experiment(self, experiment_data: ExperimentDataType) -> Tuple[str, str]:
        application_slug = experiment_data["meta"]["application"]["slug"]
        app_version = experiment_data["meta"]["application"]["app_version"]
        experiment_to_create = self.__create_experiment(application_slug, app_version)
        experiment = self.__qne_client.create_experiment(experiment_to_create)
        asset_to_create = experiment_data["asset"]
        asset_to_create = self.__translate_asset(asset_to_create, experiment["url"])
        asset = self.__qne_client.create_asset(asset_to_create)
        number_of_rounds = experiment_data["meta"]["number_of_rounds"]
        round_set_to_create = self.__create_round_set(asset["url"], number_of_rounds)
        round_set = self.__qne_client.create_roundset(round_set_to_create)

        return round_set["url"], experiment["id"]

    def get_results(self, round_set_url: str, block: bool = False, wait: int = 2,
                    timeout: int = 30) -> Optional[List[ResultType]]:
        start_time = time.time()
        round_set = self.__qne_client.retrieve_roundset(round_set_url)
        status = round_set["status"]
        while block and status not in QNE_JOB_FINAL_STATES:
            elapsed_time = time.time() - start_time
            if timeout is not None and elapsed_time > timeout:
                raise JobTimeoutError(f"Failed getting result for round set '{round_set_url}': timeout reached. "
                                      f"Try again later using command 'experiment results'")
            time.sleep(wait)

        return self.__get_results(round_set)

    def __get_results(self, round_set: RoundSetType) -> Optional[List[ResultType]]:
        # For a finished job and completed job, get the results
        status = round_set["status"]
        round_set_url = round_set["url"]

        if status in QNE_JOB_FINAL_STATES:
            if status in QNE_JOB_SUCCESS_STATES:
                # round_set completed
                round_set_url = round_set["url"]
                results = self.__qne_client.results_roundset(round_set_url)

                result_list = []
                for result in results:
                    round_result = ResultGenerator.generate(round_set, result["round_number"], result["round_result"],
                                                            result["instructions"], result["cumulative_result"])
                    result_list.append(round_result)

                return result_list
            else:
                # round set failed
                raise ExperimentFailed(f"Experiment for round set '{round_set_url}' failed. No results available")

        return None

    def __get_final_result(self, round_set: RoundSetType) -> Optional[FinalResultType]:
        # For a finished job, get the final result
        status = round_set["status"]
        round_set_url = round_set["url"]

        if status in QNE_JOB_FINAL_STATES:
            if status in QNE_JOB_SUCCESS_STATES:
                # round_set completed
                final_result: FinalResultType = {}
                try:
                    final_result = self.__qne_client.final_results_roundset(round_set_url)
                except ErrorResponse:
                    # leave final_result empty
                    pass

                return final_result
            else:
                # round set failed
                raise ExperimentFailed(f"Experiment for round set '{round_set_url}' failed. No results available")

        return None

    def __results_exists(self, path: Path) -> bool:
        pass

    def list_networks(self) -> List[Dict[str, Any]]:
        """
        Function to list the networks

        Returns:
            A list of networks
        """
        return self.__qne_client.list_networks()

    @staticmethod
    def __write_network_data(entity_name: str, network_data: GenericNetworkData) -> None:
        """
            Writes the json file specified by the parameter 'entity_name'.
            entity_name can be 'networks', 'channels', 'nodes', 'templates'

            Params:
                entity_name: The type of the data to read
                network_data: The data to write

        """
        file_name = Path(BASE_DIR) / 'networks' / f'{entity_name}.json'
        utils.write_json_file(file_name, network_data)

    @staticmethod
    def __read_network_data(entity_name: str) -> GenericNetworkData:
        """ TODO: In local api the network is already read. It may be more efficient to use these values """
        file_name = Path(BASE_DIR) / 'networks' / f'{entity_name}.json'
        return utils.read_json_file(file_name)

    def __update_networks_networks(self, overwrite: bool) -> None:
        entity = "networks"
        networks_json = {}

        network_json = {} if overwrite else self.__read_network_data(entity)[entity]
        networks = self.__qne_client.list_networks()
        for network in networks:
            network_type_json = {}
            network_type = self.__qne_client.retrieve_network(network["url"])
            network_type_json["name"] = network_type["name"]
            network_type_json["slug"] = network_type["slug"]
            network_type_channels = []
            for channel in network_type["channels"]:
                network_type_channels.append(channel["slug"])

            network_type_json["channels"] = network_type_channels
            network_json[network["slug"]] = network_type_json

        networks_json[entity] = network_json
        self.__write_network_data(entity, networks_json)

    @staticmethod
    def __update_list(list_of_dict: List[Dict[str, Any]], dict_item: Dict[str, Any], overwrite: bool) -> None:
        if overwrite:
            list_of_dict.append(dict_item)
        else:
            # overwrite if it existed, otherwise append
            found = False
            for i in range(len(list_of_dict)):
                if list_of_dict[i]["slug"] == dict_item["slug"]:
                    list_of_dict[i] = dict_item
                    found = True
                    break
            if not found:
                list_of_dict.append(dict_item)

    def __update_networks_channels(self, overwrite: bool) -> None:
        entity = "channels"

        channels_json = {}
        channel_json = [] if overwrite else self.__read_network_data(entity)[entity]
        channels = self.__qne_client.list_channels()
        for channel in channels:
            channel_type_json = {"slug": channel["slug"]}
            node = self.__qne_client.retrieve_node(channel["node1"])
            channel_type_json["node1"] = node["slug"]
            node = self.__qne_client.retrieve_node(channel["node2"])
            channel_type_json["node2"] = node["slug"]
            channel_parameters = []
            for parameter in channel["parameters"]:
                template = self.__qne_client.retrieve_template(parameter)
                channel_parameters.append(template["slug"])
            channel_type_json["parameters"] = channel_parameters

            self.__update_list(channel_json, channel_type_json, overwrite)

        channels_json[entity] = channel_json
        self.__write_network_data(entity, channels_json)

    def __update_networks_nodes(self, overwrite: bool) -> None:
        entity = "nodes"
        nodes_json = {}
        node_json = [] if overwrite else self.__read_network_data(entity)[entity]
        nodes = self.__qne_client.list_nodes()
        for node in nodes:
            node_type_json = {"name": node["name"], "slug": node["slug"],
                              "coordinates": {"latitude": node["coordinates"]["latitude"],
                                              "longitude": node["coordinates"]["longitude"]}}
            node_parameters = []
            for parameter in node["node_parameters"]:
                template = self.__qne_client.retrieve_template(parameter)
                node_parameters.append(template["slug"])
            node_type_json["node_parameters"] = node_parameters
            node_type_json["number_of_qubits"] = node["number_of_qubits"]
            qubit_parameters = []
            for parameter in node["qubit_parameters"]:
                template = self.__qne_client.retrieve_template(parameter)
                qubit_parameters.append(template["slug"])
            node_type_json["qubit_parameters"] = qubit_parameters

            self.__update_list(node_json, node_type_json, overwrite)

        nodes_json[entity] = node_json
        self.__write_network_data(entity, nodes_json)

    def __update_networks_templates(self, overwrite: bool) -> None:
        entity = "templates"
        templates_json = {}
        template_json = [] if overwrite else self.__read_network_data(entity)[entity]
        templates = self.__qne_client.list_templates()
        for template in templates:
            del template["id"]
            del template["url"]
            del template["description"]
            template_values = []
            for value in template["values"]:
                value["unit"] = ""
                value["scale_value"] = 1.0
                template_values.append(value)

            self.__update_list(template_json, template, overwrite)

        templates_json[entity] = template_json
        self.__write_network_data(entity, templates_json)

    def update_networks(self, overwrite: bool) -> bool:
        """
        Function to get the remote networks and update the local network definitions

        Returns:
            success of not
        """
        try:
            self.__update_networks_networks(overwrite)
            self.__update_networks_channels(overwrite)
            self.__update_networks_nodes(overwrite)
            self.__update_networks_templates(overwrite)
        except Exception:
            return False

        return True
