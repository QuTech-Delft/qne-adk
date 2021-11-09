import os.path
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from adk.utils import read_json_file, write_json_file
from adk.exceptions import ApplicationDoesNotExist, DirectoryIsFile


class ConfigManager:
    def __init__(self, config_dir: Path):
        """ Initializes config dir, creates config path and file if it doesn't exist. When the config directory
        happens to be a file raise an  Exception. Also does a sanity check on the content of the config """
        self.__config_dir = config_dir
        if os.path.isfile(str(self.__config_dir)):
            raise DirectoryIsFile(str(self.__config_dir))
        if not os.path.isdir(str(self.__config_dir)):
            self.__config_dir.mkdir(parents=True)
        self.applications_config = self.__config_dir / "applications.json"

        if not self.check_config_exists():
            self.__create_config()
        else:
            self.__cleanup_config()

    def check_config_exists(self) -> bool:
        """ Checks if the application.json config file exists in the .qne/ root directory. Returns True when it does
        exist, False if not.

        Returns:
            True if app_config_file exists, False otherwise
        """

        return self.applications_config.is_file()

    def __create_config(self) -> None:
        """ Creates the application.json config file in the .qne/ root directory"""
        write_json_file(self.applications_config, {})

    def add_application(self, application_name: str, path: Path) -> None:
        """
        Takes care of saving the application name in the .qne/application.json root file together with the application
        path.

        Args:
            application_name: name of the application
            path: the path where the application is stored

        """
        # Extra check to make sure application name is stored in lowercase
        application_name = application_name.lower()

        # Read json file
        applications = read_json_file(self.applications_config)

        # Store the app path
        applications[application_name] = {'path': os.path.join(str(path), application_name, '')}
        write_json_file(self.applications_config, applications)

    def delete_application(self, application_name: str) -> None:
        """
        Takes care of deleting the application from the .qne/application.json root file together with the application
        data.

        Args:
            application_name: name of the application

        """
        # application name is stored in lowercase
        application_name = application_name.lower()

        # Read json file
        applications = read_json_file(self.applications_config)

        # Remove the app and write
        if application_name in applications:
            del applications[application_name]

            write_json_file(self.applications_config, applications)

    def get_applications(self) -> List[Dict[str, Any]]:
        """
        Reads the applications.json config file for getting the local applications

        Returns:
            A list of applications available in the config file
        """
        application_list = []
        applications = read_json_file(self.applications_config)
        for application_name, application_data in applications.items():
            application_data['name'] = application_name
            application_list.append(application_data)

        return application_list

    def get_application(self, application_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details for an application

        Args:
            application_name: Name of the application

        Returns:
            If application exists, a dictionary containing application details (name, path)
            None otherwise.

        """
        applications = self.get_applications()

        for application in applications:
            if application["name"].lower() == application_name.lower():
                return application
        return None

    def get_application_path(self, application_name: str) -> Any:
        """
        Reads the applications.json config file for getting the path using the application_name.

        Args:
            application_name: Name of the application

        Returns:
           A string of the path where there application is stored. None if the path is not in config or doesn't exist
        """

        application = self.get_application(application_name)
        if application:
            if 'path' in application and os.path.exists(application['path']):
                return application['path']

        return None

    def get_application_from_path(self, path: Path) -> Tuple[str, Dict[str, str]]:
        applications = read_json_file(self.applications_config)

        for application_name in applications:
            application_path = self.get_application_path(application_name)
            if application_path is not None and application_path == os.path.join(str(path), ''):
                return application_name, applications[application_name]

        raise ApplicationDoesNotExist(str(path))

    def application_exists(self, application_name: str) -> Tuple[bool, Any]:
        """
        Checks if the application name already exists in .qne/application.json for unique purposes. Returns True when
        the application does exists. Else, return False.

        Args:
            application_name: name of the application

        """

        applications = read_json_file(self.applications_config)
        for key in applications:
            if key.lower() == application_name.lower():
                return True, self.get_application_path(application_name)

        return False, None

    def remote_application_exists(self, application_name: str) -> Any:
        """
        Check if the application is already created on remote
        by checking the remote_id field in the config file.
        Returns application id if application exists on remote
        else -1 if application does not exist on remote

        Args:
            application_name: name of the application
        """
        return -1

    def update_path(self, application: str, path: str) -> None:
        pass

    def update_remote_id(self, application: str, application_id: int) -> None:
        pass

    def get_config_dir(self) -> Path:
        return self.__config_dir

    def remote_experiment_exists(self, path: Path) -> Tuple[bool, int]:
        """
        Check if the experiment is created on remote
        by checking the experiment_id field in the meta attribute of experiment.json file.
        Returns True and experiment id if experiment exists on remote
        Returns False and -1 if experiment does not exist on remote
        """
        experiment_info = self.get_experiment(path)
        if 'experiment_id' in experiment_info['meta']:
            return True, int(experiment_info['experiment_id'])

        return False, -1

    def get_experiment(self, path: Path) -> Dict[str, str]:
        return {}

    def __cleanup_config(self) -> None:
        del_applications = []
        applications = read_json_file(self.applications_config)
        for application_name in applications:
            if not self.get_application_path(application_name):
                del_applications.append(application_name)

        # Delete applications without existing path
        for app in del_applications:
            del applications[app]

        if del_applications:
            write_json_file(self.applications_config, applications)
