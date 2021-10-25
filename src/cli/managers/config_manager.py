import os.path
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from cli.utils import read_json_file, write_json_file
from cli.exceptions import ApplicationDoesNotExist, NoConfigFileExists


class ConfigManager:
    def __init__(self, config_dir: Path):
        self.__config_dir = config_dir
        self.applications_config = self.__config_dir / "applications.json"

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
        apps = read_json_file(self.applications_config)

        # Store the app path
        apps[application_name] = {'path': os.path.join(str(path), application_name, '')}
        write_json_file(self.applications_config, apps)

    def check_config_exists(self) -> bool:
        """ Checks if the application.json config file exists in the .qne/ root directory. Returns True when it does
        exist, False if not.

        Returns:
            True if app_config_file exists, False otherwise
        """

        return self.applications_config.is_file()

    def create_config(self) -> None:
        """ Creates the application.json config file in the .qne/ root directory"""
        write_json_file(self.applications_config, {})

    def delete_application(self, application_name: str) -> None:
        pass

    def get_application(self, application: str) -> Optional[Dict[str, Any]]:
        """
        Get details for an application

        Args:
            application: Name of the application

        Returns:
            If application exists, a dictionary containing application details (name, path)
            None otherwise.

        """
        all_applications = self.get_applications()

        for app in all_applications:
            if app["name"] == application.lower():
                return app
        return None

    def get_application_from_path(self, path: Path) -> Tuple[str, Dict[str, str]]:
        if not self.check_config_exists():
            self.create_config()

        data = read_json_file(self.applications_config)

        for app in data:
            if data[app]['path'].lower() == os.path.join(str(path), '').lower():
                return app, data[app]

        raise ApplicationDoesNotExist()

    def get_applications(self) -> List[Dict[str, Any]]:
        """
        Reads the applications.json config file for getting the local applications

        Returns:
            A list of applications available in the config file
        """
        # cleanup config file
        self.__cleanup_config()
        application_list = []
        applications = read_json_file(self.applications_config)
        for app_name, app_data in applications.items():
            app_data['name'] = app_name
            application_list.append(app_data)

        return application_list

    def get_application_path(self, application_name: str) -> Any:
        """
        Reads the applications.json config file for getting the path using the application_name

        Args:
            application_name: Name of the application

        Returns:
           A string of the path where there application is stored
        """

        return self.get_application(application_name)['path']

    def application_exists(self, application_name: str) -> Tuple[bool, Any]:
        """
        Checks if the application name already exists in .qne/application.json for unique purposes. Returns True when
        the application does exists. Else, return False.

        Args:
            application_name: name of the application

        """

        self.__cleanup_config()
        data = read_json_file(self.applications_config)
        for key in data:
            if key == application_name.lower():
                return True, data[key]['path']

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

    # TODO: Add __cleanup_config() to Confuence documentation
    def __cleanup_config(self) -> None:
        if self.check_config_exists():
            del_applications = []
            applications = read_json_file(self.applications_config)
            for app_name, app_data in applications.items():
                if not os.path.exists(app_data['path']):
                    del_applications.append(app_name)

            # Delete applications without existing path
            for app in del_applications:
                del applications[app]

            if del_applications:
                write_json_file(self.applications_config, applications)
        else:
            raise NoConfigFileExists(self.applications_config)
