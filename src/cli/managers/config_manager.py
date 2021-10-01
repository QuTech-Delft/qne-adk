import os.path
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from cli.utils import read_json_file, write_json_file
from cli.exceptions import ApplicationDoesntExist, JSONValidationError
from cli.validators import validate_json_string


class ConfigManager:
    def __init__(self, config_dir: Path):
        self.__config_dir = config_dir
        self.app_config_file = self.__config_dir / "applications.json"

    def add_application(self, application: str, path: Path) -> None:
        """
        Takes care of saving the application name in the .qne/application.json root file together with the application
        path.

        Args:
            application: the application name
            roles: a list of roles
            path: the path where the application is stored

        """

        # Read json file
        apps = read_json_file(self.app_config_file)

        # Store the app path
        apps[application] = {'path': os.path.join(str(path), application, '')}
        write_json_file(self.app_config_file, apps)

    def check_config_exists(self) -> bool:
        """ Checks if the application.json config file exists in the .qne/ root directory. Returns True when it does
        exist, False if not.

        Returns:
            True if app_config_file exists, False otherwise
        """
        return self.app_config_file.is_file()

    def create_config(self) -> None:
        """ Creates the application.json config file in the .qne/ root directory"""
        write_json_file(self.app_config_file, {})

    def delete_application(self, application: str) -> None:
        pass

    def get_application(self, application: str) -> Dict[str, Any]:
        return {}

    def get_application_from_path(self, path: Path) -> Tuple[str, Dict[str, str]]:
        application_path = Path.home() / ".qne/applications.json"

        if not os.path.isfile(application_path):
            raise ApplicationDoesntExist()

        with open(application_path) as json_file:
            # if validate_json_string(str(json_file)):
            data = json.load(json_file)
            if not data:
                raise ApplicationDoesntExist()
            for app in data:
                if data[app]['path'] == os.path.join(str(path) + "/"):
                    return app, data[app]

            raise ApplicationDoesntExist()

    def get_applications(self) -> List[Dict[str, Any]]:
        """
        Reads the applications.json config file for getting the local applications

        Returns:
            A list of applications available in the config file
        """
        applications_config = self.__config_dir / 'applications.json'
        application_list = []
        if applications_config.is_file():
            applications = read_json_file(applications_config)
            for app_name, app_data in applications.items():
                app_data['name'] = app_name
                application_list.append(app_data)
        else:
            logging.info('The configuration file %s was not found. '
                     'Maybe, you haven\'t created any local applications yet?', applications_config)

        return application_list

    def application_exists(self, application: str) -> Tuple[bool, Any]:
        """
        Checks if the application name already exists in .qne/application.json for unique purposes. Returns True when
        the application does exists. Else, return False.

        Args:
            application: the application name

        """

        data = read_json_file(self.app_config_file)

        for key in data:
            if key == application:
                return True, data[key]['path']

        return False, None

    def remote_application_exists(self, application: str) -> int:
        """
        Check if the application is already created on remote
        by checking the remote_id field in the config file.
        Returns application id if application exists on remote
        else -1 if application does not exist on remote
        """
        application_info = self.get_application(application)
        return application_info.get('remote_id', -1)

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
