from pathlib import Path
from typing import Any, cast, Dict, List, Optional, Tuple, Union
import time

from apistar.exceptions import ErrorResponse

from adk import utils
from adk.api.qne_client import QneFrontendClient
from adk.exceptions import (ApiClientError, ApplicationNotFound, ExperimentFailed, ExperimentValueError,
                            JobTimeoutError)
from adk.generators.result_generator import ResultGenerator
from adk.managers.config_manager import ConfigManager
from adk.managers.auth_manager import AuthManager
from adk.managers.resource_manager import ResourceManager
from adk.type_aliases import (AppConfigType, AppResultType, AppSourceFilesType, AppSourceType, AppVersionType,
                              ApplicationType, ApplicationDataType, AssetType, assetNetworkType, ErrorDictType,
                              ExperimentType, FinalResultType, GenericNetworkData, ExperimentDataType, ResultType,
                              RoundSetType, round_resultType, cumulative_resultType, instructionsType, ChannelType,
                              parametersType, coordinatesType, listValuesType)
from adk.settings import BASE_DIR


class JobStatus:
    """ The status of the qne_job can be 'NEW', 'RUNNING', 'COMPLETE', 'FAILED' """
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


class RemoteApi:
    """
    Defines the methods used for remote communication with api-router
    """
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

        self.__resource_manager = ResourceManager()

    def __login_user(self, username: str, password: str, host: str) -> str:
        self.__refresh_token = None
        self.__base_uri = host
        self.__username = username
        self.__password = password

        self.__refresh_token = self.__qne_client.login(username, password, host)
        return self.__refresh_token

    def __login_anonymous(self) -> str:
        pass

    def login(self, username: str, password: str, host: str) -> None:
        """
        Login the user on host (uri) based upon the username/password values given
        """
        self.auth_manager.login(username, password, host)

    def __logout_user(self, host: str) -> None:
        self.__qne_client.logout(host)

    def logout(self, host: Optional[str]) -> bool:
        """
        Logout the user by deleting the entry in the resource
        """
        if not self.__qne_client.is_logged_in():
            return False
        self.auth_manager.logout(host)
        return True

    def get_active_host(self) -> str:
        """
        Get the host as base_uri the user is logged in
        """
        return self.__base_uri

    def list_applications(self) -> List[ApplicationType]:
        """
        Get the list of applications (public and enabled) from the api-router

        Returns:
             the list of applications
        """
        return self.__qne_client.list_applications()

    def delete_application(self, application_id: Optional[str]) -> bool:
        """
        Delete the remote application for the authenticated user

        Args:
            application_id is the application to delete.

        Returns:
            False when not found 404 or another error
            True when no error was raised
        """
        if application_id is not None and application_id.isdigit():
            try:
                self.__qne_client.destroy_application(application_id)
            except ErrorResponse:
                return False

            # application deleted successfully
            return True
        return False

    def clone_application(self, application_name: str, new_application_name: str,
                          new_application_path: Path) -> None:
        """
        Clone the application by copying the required files in the local application structure.

        Args:
            application_name: name of the application to be cloned
            new_application_name: name of the application after cloning
            new_application_path: location of application files

        """
        application = self.__get_application_by_slug(application_name)

        if application is None:
            raise ApplicationNotFound(new_application_name)

        new_application_name = new_application_name.lower()

        local_app_src_path = new_application_path / 'src'
        local_app_config_path = new_application_path / 'config'
        local_app_src_path.mkdir(parents=True, exist_ok=True)
        local_app_config_path.mkdir(parents=True, exist_ok=True)

        app_config = self.__qne_client.app_config_application(str(application["url"]))
        utils.write_json_file(local_app_config_path / 'network.json', app_config["network"])
        utils.write_json_file(local_app_config_path / 'application.json', app_config["application"])

        app_result = self.__qne_client.app_result_application(str(application["url"]))
        utils.write_json_file(local_app_config_path / 'result.json',
                              {"round_result_view": app_result["round_result_view"],
                               "cumulative_result_view": app_result["cumulative_result_view"],
                               "final_result_view": app_result["final_result_view"]
                               })

        app_source = self.__qne_client.app_source_application(str(application["url"]))
        # Create python files from tarball
        self.__resource_manager.generate_resources(self.__qne_client, app_source, new_application_path)

        # Manifest.json configuration
        utils.write_json_file(new_application_path / 'manifest.json', utils.get_default_manifest(new_application_name))

        self.__config_manager.add_application(application_name=new_application_name,
                                              application_path=new_application_path)

    def publish_application(self, application_data: ApplicationDataType) -> bool:
        """
        Publish the application by enabling the AppVersion.

        Args:
            application_data: application data from manifest.json

        Returns:
            True when published successfully, otherwise False
        """

        if "app_version" in application_data["remote"]:
            # check if application exists
            application = self.__get_application(application_data)

            # application must exist
            if application is not None:
                # update all remote info with latest data
                application_data["remote"]["application"] = application["url"]
                application_data["remote"]["application_id"] = application["id"]
                application_data["remote"]["slug"] = application["slug"]

                app_version = self.__partial_update_app_version(application_data, application)

                application_data["remote"]["app_version"]["app_version"] = app_version["url"]
                application_data["remote"]["app_version"]["app_config"] = app_version["app_config"]
                application_data["remote"]["app_version"]["app_result"] = app_version["app_result"]
                application_data["remote"]["app_version"]["app_source"] = app_version["app_source"]
                application_data["remote"]["app_version"]["enabled"] = not app_version["is_disabled"]
                application_data["remote"]["app_version"]["version"] = app_version["version"]

                return True
        return False

    def upload_application(self,  # pylint: disable=R0914
                           application_path: Path,
                           application_data: ApplicationDataType,
                           application_config: AppConfigType,
                           application_result: AppResultType,
                           application_source: List[str]) -> ApplicationDataType:
        """
        Upload the application to the remote server.

        Args:
            application_path: location of application files
            application_data: application data from manifest.json
            application_config: application configuration structure
            application_result: application result structure
            application_source: source files for application

        Returns:
            True when uploaded successfully, otherwise False
        """
        application = self.__get_application(application_data)

        if application is None:
            try:
                # create application data structure for remote
                application_data["remote"] = {"application": "",
                                              "application_id": 0,
                                              "slug": "",
                                              "app_version": {
                                                  "enabled": False,
                                                  "version": 0,
                                                  "app_version": "",
                                                  "app_config": "",
                                                  "app_result": "",
                                                  "app_source": ""
                                                  }
                                              }
                # create Application
                application = self.__create_application(application_data)

            except Exception as e:
                # rethrow exception
                raise e

        if application is not None:
            # update all remote info with latest data
            application_data["remote"]["application"] = application["url"]
            application_data["remote"]["application_id"] = application["id"]
            application_data["remote"]["slug"] = application["slug"]

        app_version: AppVersionType = {}
        try:
            # create AppVersion
            app_version = self.__create_app_version(application)
            application_data["remote"]["app_version"]["app_version"] = app_version["url"]
            application_data["remote"]["app_version"]["enabled"] = not app_version["is_disabled"]
            application_data["remote"]["app_version"]["version"] = app_version["version"]
            # new app_version reset registered application references
            application_data["remote"]["app_version"]["app_config"] = ''
            application_data["remote"]["app_version"]["app_result"] = ''
            application_data["remote"]["app_version"]["app_source"] = ''

        except ApiClientError as e:
            if "Please complete" in str(e) and "app_version" in application_data["remote"]["app_version"] and \
                                               application_data["remote"]["app_version"]["app_version"]:
                # The (incomplete) AppVersion already existed, use this one to connect the not yet registered objects
                app_version["url"] = application_data["remote"]["app_version"]["app_version"]
            else:
                # for now rethrow all other exceptions
                raise e
        try:
            if not application_data["remote"]["app_version"]["app_config"]:
                # create AppConfig
                app_config = self.__create_app_config(application_data, application_config, app_version)
                application_data["remote"]["app_version"]["app_config"] = app_config["url"]

            if not application_data["remote"]["app_version"]["app_result"]:
                # create AppResult
                app_result = self.__create_app_result(application_result, app_version)
                application_data["remote"]["app_version"]["app_result"] = app_result["url"]

            if not application_data["remote"]["app_version"]["app_source"]:
                # create AppSource
                app_source = self.__create_app_source(application_data, app_version,
                                                      application_source, application_path)
                application_data["remote"]["app_version"]["app_source"] = app_source["url"]

            # Update application when AppVersion and its components is uploaded
            application_to_update = self.__create_application_type(application_data)
            self.__qne_client.partial_update_application(str(application["id"]), application_to_update)

        except Exception as e:
            # Something went wrong, delete the (just created) AppVersion (currently not supported by api-router)
            # app_version_to_delete: AppVersionType = {
            #     "application": application["url"],
            #     "version": app_version["version"]
            # }
            # app_version = self.__qne_client.delete_app_version(app_version_to_delete)
            # for now rethrow exception
            raise e

        return application_data

    def __create_application(self, application_data: ApplicationDataType) -> ApplicationType:
        """
        Create and send an Application object to api-router
        """
        application_to_create = self.__create_application_type(application_data)
        application = self.__qne_client.create_application(application_to_create)

        return application

    @staticmethod
    def __create_application_type(application_data: ApplicationDataType) -> ApplicationType:
        application_name = application_data["application"]["name"] if "name" in application_data["application"] else ""
        application_description =\
            application_data["application"]["description"] if "description" in application_data["application"] else ""
        application_author =\
            application_data["application"]["author"] if "author" in application_data["application"] else ""
        application_email =\
            application_data["application"]["email"] if "email" in application_data["application"] else ""

        application: ApplicationType = {
            "name": application_name,
            "description": application_description,
            "author": application_author,
            "email": application_email
        }
        return application

    def __create_app_version(self, application: ApplicationType, version: int = 1) -> AppVersionType:
        """
        Create and send an AppVersion object to api-router
        """
        app_version_to_create = self.__create_app_version_type(application, version)
        app_version = self.__qne_client.create_app_version(app_version_to_create)

        return app_version

    @staticmethod
    def __create_app_version_type(application: ApplicationType, version: int = 1) -> AppVersionType:
        app_version: AppVersionType = {
            "application": application["url"],
            "is_disabled": True
        }
        return app_version

    def __create_app_config(self, application_data: ApplicationDataType, application_config: AppConfigType,
                            app_version: AppVersionType) -> AppConfigType:
        """
        Create and send an AppConfig object to api-router
        """
        app_config_to_create = self.__create_app_config_type(application_data, application_config, app_version)
        app_config = self.__qne_client.create_app_config(app_config_to_create)

        return app_config

    @staticmethod
    def __create_app_config_type(application_data: ApplicationDataType, application_config: AppConfigType,
                                 app_version: AppVersionType) -> AppConfigType:
        multi_round = application_data["application"]["multi_round"] if \
            "multi_round" in application_data["application"] else False
        app_config: AppConfigType = {
            "app_version": app_version["url"],
            "network": application_config["network"],
            "application": application_config["application"],
            "multi_round": multi_round
        }
        return app_config

    def __create_app_result(self, application_result: AppResultType, app_version: AppVersionType) -> AppResultType:
        """
        Create and send an AppResult object to api-router
        """
        app_result_to_create = self.__create_app_result_type(application_result, app_version)
        app_result = self.__qne_client.create_app_result(app_result_to_create)

        return app_result

    @staticmethod
    def __create_app_result_type(application_result: AppResultType, app_version: AppVersionType) -> AppResultType:
        app_result: AppResultType = {
            "app_version": app_version["url"],
            "round_result_view": application_result["round_result_view"],
            "cumulative_result_view": application_result["cumulative_result_view"],
            "final_result_view": application_result["final_result_view"]
        }
        return app_result

    def __create_app_source(self, application_data: ApplicationDataType, app_version: AppVersionType,
                            application_source: List[str], application_path: Path) -> AppSourceType:
        """
        Create and send an AppSource object to api-router
        """
        # create the resource
        resource_path, resource_file = self.__resource_manager.prepare_resources(application_data, application_path,
                                                                                 application_source)
        # send the resource
        with open(resource_path, 'rb') as tarball:
            app_source_files: AppSourceFilesType = {
                "source_files": (resource_file, tarball),  # pylint: disable=R1732
                "app_version": (None, app_version['url']),
                "output_parser": (None, '{}')
            }
            app_source = self.__qne_client.create_app_source(app_source_files)

        # delete the resource
        self.__resource_manager.delete_resources(application_data, application_path)

        return app_source

    @staticmethod
    def __partial_update_version_type(application: ApplicationType) -> AppVersionType:
        app_version: AppVersionType = {
            "application": application["url"],
            'is_disabled': False
        }
        return app_version

    def __partial_update_app_version(self, application_data: ApplicationDataType,
                                     application: ApplicationType) -> AppVersionType:
        """
        Create and send an AppVersion object to api-router for updating it
        """
        app_version_to_update = self.__partial_update_version_type(application)
        app_version_url = application_data["remote"]["app_version"]["app_version"]
        app_version = self.__qne_client.partial_update_app_version(app_version_url, app_version_to_update)

        return app_version

    def __get_application(self, application_data: ApplicationDataType) -> Optional[ApplicationType]:
        """
        Get the application object from api-router for this remote application

        Args:
            application_data: application information from manifest

        Returns:
            Application object or None when the application was not found remotely
        """
        application = None
        if "application_id" in application_data["remote"]:
            application_id = str(application_data["remote"]["application_id"])
            application = self.__get_application_by_id(application_id)
        if application is None and "slug" in application_data["remote"]:
            application_slug = str(application_data["remote"]["slug"])
            application = self.__get_application_by_slug(application_slug)

        return application

    def __get_application_by_id(self, application_id: Optional[str]) -> Optional[ApplicationType]:
        """
        Get the application object from api-router for this remote application

        Args:
            application_id: id of the application

        Returns:
            Application object or None when the application was not found remotely
        """
        if application_id is not None and application_id.isdigit():
            app_list = self.list_applications()
            for application in app_list:
                if application["id"] == int(application_id):
                    return application
        return None

    def __get_application_by_slug(self, application_slug: str) -> Optional[ApplicationType]:
        """
        Get the application object from api-router for this remote application.
        Returned applications are not disabled and either are public with enabled versions or are owned by user

        Args:
            application_slug: Slug of the application

        Returns:
            Application object or None when the application was not found remotely
        """
        app_list = self.list_applications()
        for application in app_list:
            if application["slug"] == application_slug.lower():
                return application
        return None

    def get_application_id(self, application_slug: str) -> Optional[int]:
        """
        Get the app id from api-router for this remote application

        Args:
            application_slug: Slug of the application

        Returns:
            id or None when the application was not found remotely
        """
        application = self.__get_application_by_slug(application_slug)
        if application is not None:
            return int(application["id"])
        return None

    def get_application_config(self, application_slug: str) -> Optional[AppConfigType]:
        """
        Get the app config for the relevant app_version from api-router for this remote application.
        For the author of the application this is the app_config linked to the highest numbered app_version (which can
        be disabled, because it is not yet published),
        For all the other users this will be the highest versioned enabled app_version

        Args:
            application_slug: Slug of the application

        Returns:
            App config or None when the application was not found remotely
        """
        application = self.__get_application_by_slug(application_slug)
        if application is not None:
            app_versions = self.__qne_client.app_versions_application(str(application["url"]))
            if len(app_versions) > 0:
                app_version = app_versions[0]
                app_config = self.__qne_client.app_config_appversion(str(app_version["url"]))
                if app_config["app_version"] is not None:
                    return app_config

        return None

    def validate_application(self, application_slug: str) -> ErrorDictType:
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
            error_dict["error"].append(f"Application '{application_slug}' does not exist, is not enabled, "
                                       f"is not public or is owned by someone else")

        return error_dict

    def delete_experiment(self, experiment_id: Optional[str]) -> bool:
        """
        Delete the remote experiment for the authenticated user
        Args:
            experiment_id: is the experiment to delete.

        Returns:
            False when not found 404 or another error occurs
            True when no error was raised. The experiment is deleted (including all assets/round_sets/results)
        """
        if experiment_id is not None and experiment_id.isdigit():
            try:
                self.__qne_client.destroy_experiment(experiment_id)
            except ErrorResponse:
                return False

            return True
        return False

    def experiments_list(self) -> List[ExperimentType]:
        """
        Get the remote experiments for the authenticated user from api-router
        """
        experiment_list = self.__qne_client.list_experiments()
        for experiment in experiment_list:
            app_version = self.__qne_client.retrieve_appversion(str(experiment["app_version"]))
            application = self.__qne_client.retrieve_application(str(app_version["application"]))
            experiment["name"] = application["slug"]

        return experiment_list

    def __create_experiment(self, application_slug: str, app_version: str) -> ExperimentType:
        """
        Create and send an experiment object to api-router
        """
        experiment_to_create = self.__create_experiment_type(application_slug, app_version)
        experiment = self.__qne_client.create_experiment(experiment_to_create)

        return experiment

    def __create_experiment_type(self, application_slug: str, app_version: str) -> ExperimentType:
        """
        Create and return an experiment object for sending to api-router
        """
        user = self.__qne_client.retrieve_user()
        if user is None:
            raise ExperimentValueError("Current logged in user not a valid remote user")
        application = self.__get_application_by_slug(application_slug)
        if application is None:
            raise ExperimentValueError(f"Application in experiment data '{application_slug}' is not a remote "
                                       f"application")
        app_config = self.get_application_config(application_slug)
        if app_config is None:
            raise ExperimentValueError(f"Application '{application_slug}' does not have a valid application "
                                       f"configuration")
        app_version_url = str(app_config["app_version"])

        if app_version != app_version_url:
            raise ExperimentValueError(f"App version in experiment data '{app_version}' is not equal to the "
                                       f"current remote version of the application '{app_version_url}'")
        user_url = user["url"]
        experiment: ExperimentType = {
            "app_version": app_version_url,
            "personal_note": "Experiment created by qne-adk",
            "is_marked": False,
            "owner": user_url
        }
        return experiment

    def __create_asset(self, experiment_asset: AssetType, experiment_url: str) -> AssetType:
        """
        Create and send an asset object to api-router
        """
        asset_to_create = self.__translate_asset(experiment_asset, experiment_url)
        asset = self.__qne_client.create_asset(asset_to_create)

        return asset

    @staticmethod
    def __translate_asset(asset_to_create: AssetType, experiment_url: str) -> AssetType:
        """
        Because of differences in channel definition for api-router networks and asset networks we need a fix to
        translate these (local) channels to a format that the backend expects.
        Also the asset needs an experiment entry with the experiment url
        """
        asset_network = cast(assetNetworkType, asset_to_create["network"])
        experiment_channels = asset_network["channels"]
        new_channels = []
        for channel in experiment_channels:
            new_channel = {"node_slug1": channel["node1"],
                           "node_slug2": channel["node2"],
                           "parameters": channel["parameters"]}
            new_channels.append(new_channel)

        asset_network["channels"] = new_channels
        asset_to_create["experiment"] = experiment_url
        return asset_to_create

    def __create_round_set(self, asset_url: str, number_of_rounds: int) -> RoundSetType:
        """
        Create and send a round set object to api-router
        """
        round_set_to_create = self.__create_round_set_type(asset_url, number_of_rounds)
        round_set = self.__qne_client.create_roundset(round_set_to_create)

        return round_set

    @staticmethod
    def __create_round_set_type(asset_url: str, number_of_rounds: int) -> RoundSetType:
        """
        Create and return a round set object for sending to api-router
        """
        round_set: RoundSetType = {
          "number_of_rounds": number_of_rounds,
          "status": "NEW",
          "input": asset_url
        }
        return round_set

    def run_experiment(self, experiment_data: ExperimentDataType) -> Tuple[str, str]:
        """
        Send the objects to api-router to run this experiment. The steps are:
        1. add an experiment for this app_version
        2. add an asset object that holds the app config
        3. add a round set for number_of_rounds rounds to run the experiment

        Args:
            experiment_data: which holds the experiment data needed to generate the experiment
        """
        application_slug = experiment_data["meta"]["application"]["slug"]
        app_version = experiment_data["meta"]["application"]["app_version"]
        experiment = self.__create_experiment(application_slug, app_version)
        experiment_asset = experiment_data["asset"]
        asset = self.__create_asset(experiment_asset, str(experiment["url"]))
        number_of_rounds = experiment_data["meta"]["number_of_rounds"]
        round_set = self.__create_round_set(str(asset["url"]), number_of_rounds)

        return str(round_set["url"]), str(experiment["id"])

    def get_results(self, round_set_url: str, block: bool = False, timeout: Optional[int] = None,
                    wait: int = 2) -> Optional[List[ResultType]]:
        """
        For a job running, get the results. When block is True, block the call for 'timeout' seconds until the result
        is received

        Args:
            round_set_url: which holds the results and status of the run of the remote experiment
            block: When True retry for a number of seconds
            timeout: retry for this number of seconds to get the result (None = no timeout)
            wait: number of seconds to wait between calls to api router for the results
        """
        start_time = time.time()
        round_set = self.__qne_client.retrieve_roundset(round_set_url)
        status = round_set["status"]
        while block and status not in QNE_JOB_FINAL_STATES:
            elapsed_time = time.time() - start_time
            if timeout is not None and elapsed_time > timeout:
                raise JobTimeoutError(f"Failed getting result for round set '{round_set_url}': timeout reached. "
                                      f"Try again later using command 'experiment results'")
            time.sleep(wait)
            round_set = self.__qne_client.retrieve_roundset(round_set_url)
            status = round_set["status"]

        return self.__get_results(round_set)

    def __get_results(self, round_set: RoundSetType) -> Optional[List[ResultType]]:
        """
        For a completed job, get the results

        Args:
            round_set: which holds the results and status of the run of the remote experiment
        """
        status = round_set["status"]
        round_set_url = round_set["url"]

        if status in QNE_JOB_FINAL_STATES:
            if status in QNE_JOB_SUCCESS_STATES:
                # round_set completed
                round_set_url = str(round_set["url"])
                results = self.__qne_client.results_roundset(round_set_url)

                result_list = []
                for result in results:
                    round_result = ResultGenerator.generate(round_set,
                                                            cast(int, result["round_number"]),
                                                            cast(round_resultType, result["round_result"]),
                                                            cast(instructionsType, result["instructions"]),
                                                            cast(cumulative_resultType, result["cumulative_result"]))
                    result_list.append(round_result)

                return result_list

            # round set failed
            raise ExperimentFailed(f"Experiment for round set '{round_set_url}' failed. No results available")

        return None

    def __get_final_result(self, round_set: RoundSetType) -> Optional[FinalResultType]:
        """
        For a completed job, get the final result.

        Args:
            round_set: which holds the results and status of the run of the remote experiment
        """
        status = round_set["status"]
        round_set_url = str(round_set["url"])

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

            # round set failed
            raise ExperimentFailed(f"Experiment for round set '{round_set_url}' failed. No results available")

        return None

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

        Args:
            entity_name: The type of the data to read
            network_data: The data to write
        """
        file_name = Path(BASE_DIR) / 'networks' / f'{entity_name}.json'
        utils.write_json_file(file_name, network_data)

    @staticmethod
    def __read_network_data(entity_name: str) -> GenericNetworkData:
        """ TODO: In local api the network is already read. It may be more efficient to use these values """
        file_name = Path(BASE_DIR) / 'networks' / f'{entity_name}.json'
        return cast(GenericNetworkData, utils.read_json_file(file_name))

    def __update_networks_networks(self, overwrite: bool) -> None:
        """
        Get the remote networks and update the local network definitions

        Args:
            overwrite: When True, replace the local files. Otherwise try to merge (keeping the new local network
            entities)
        """
        entity = "networks"
        networks_json = {}

        network_json = {} if overwrite else self.__read_network_data(entity)[entity]
        networks = self.__qne_client.list_networks()
        for network in networks:
            network_type_json: Dict[str, Union[str, List[str]]] = {}
            network_type = self.__qne_client.retrieve_network(str(network["url"]))
            network_type_json["name"] = str(network_type["name"])
            network_type_json["slug"] = str(network_type["slug"])
            network_type_channels: List[str] = []
            for channel in cast(List[ChannelType], network_type["channels"]):
                network_type_channels.append(str(channel["slug"]))

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
            for i, _ in enumerate(list_of_dict):
                if list_of_dict[i]["slug"] == dict_item["slug"]:
                    list_of_dict[i] = dict_item
                    found = True
                    break
            if not found:
                list_of_dict.append(dict_item)

    def __update_networks_channels(self, overwrite: bool) -> None:
        """
        Get the remote channels and update the local channel definitions

        Args:
            overwrite: When True, replace the local files. Otherwise try to merge (keeping the new local network
            entities)
        """
        entity = "channels"
        channels_json = {}
        channel_json = [] if overwrite else self.__read_network_data(entity)[entity]
        channels = self.__qne_client.list_channels()
        for channel in channels:
            channel_type_json: Dict[str, Union[str, List[str]]] = {"slug": str(channel["slug"])}
            node = self.__qne_client.retrieve_node(str(channel["node1"]))
            channel_type_json["node1"] = str(node["slug"])
            node = self.__qne_client.retrieve_node(str(channel["node2"]))
            channel_type_json["node2"] = str(node["slug"])
            channel_parameters: List[str] = []
            for parameter in cast(parametersType, channel["parameters"]):
                template = self.__qne_client.retrieve_template(parameter)
                channel_parameters.append(str(template["slug"]))
            channel_type_json["parameters"] = channel_parameters

            self.__update_list(channel_json, channel_type_json, overwrite)

        channels_json[entity] = channel_json
        self.__write_network_data(entity, channels_json)

    def __update_networks_nodes(self, overwrite: bool) -> None:
        """
        Get the remote nodes and update the local node definitions

        Args:
            overwrite: When True, replace the local files. Otherwise try to merge (keeping the new local network
            entities)
        """
        entity = "nodes"
        nodes_json = {}
        node_json = [] if overwrite else self.__read_network_data(entity)[entity]
        nodes = self.__qne_client.list_nodes()
        for node in nodes:
            node_type_json = {"name": node["name"], "slug": node["slug"],
                              "coordinates": {"latitude": cast(coordinatesType, node["coordinates"])["latitude"],
                                              "longitude": cast(coordinatesType, node["coordinates"])["longitude"]}}
            node_parameters: List[str] = []
            for parameter in cast(parametersType, node["node_parameters"]):
                template = self.__qne_client.retrieve_template(parameter)
                node_parameters.append(str(template["slug"]))
            node_type_json["node_parameters"] = node_parameters
            node_type_json["number_of_qubits"] = node["number_of_qubits"]
            qubit_parameters: List[str] = []
            for parameter in cast(parametersType, node["qubit_parameters"]):
                template = self.__qne_client.retrieve_template(parameter)
                qubit_parameters.append(str(template["slug"]))
            node_type_json["qubit_parameters"] = qubit_parameters

            self.__update_list(node_json, node_type_json, overwrite)

        nodes_json[entity] = node_json
        self.__write_network_data(entity, nodes_json)

    def __update_networks_templates(self, overwrite: bool) -> None:
        """
        Get the remote templates and update the local template definitions

        Args:
            overwrite: When True, replace the local files. Otherwise try to merge (keeping the new local network
            entities)
        """
        entity = "templates"
        templates_json = {}
        template_json = [] if overwrite else self.__read_network_data(entity)[entity]
        templates = self.__qne_client.list_templates()
        for template in templates:
            del template["id"]
            del template["url"]
            del template["description"]
            template_values = []
            for value in cast(listValuesType, template["values"]):
                value["unit"] = ""
                value["scale_value"] = 1.0
                template_values.append(value)

            self.__update_list(template_json, template, overwrite)

        templates_json[entity] = template_json
        self.__write_network_data(entity, templates_json)

    def update_networks(self, overwrite: bool) -> bool:
        """
        Get the remote networks and update the local network definitions

        Args:
            overwrite: When True replace the local files, otherwise try to merge (keeping the new local network
            entities)

        Returns:
            success (True) or not (False)
        """
        try:
            self.__update_networks_networks(overwrite)
            self.__update_networks_channels(overwrite)
            self.__update_networks_nodes(overwrite)
            self.__update_networks_templates(overwrite)
        except Exception:
            return False

        return True
