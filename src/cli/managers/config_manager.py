import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from cli.exceptions import MalformedJsonFile


class ConfigManager:
    def __init__(self, config_dir: Path):
        self.__config_dir = config_dir

    def add_application(self, application: str, path: Path) -> None:
        pass

    def delete_application(self, application: str) -> None:
        pass

    def get_application(self, application: str) -> Dict[str, Any]:
        return {}

    def get_application_from_path(self, path: Path) -> Tuple[str, Dict[str, str]]:
        return "key", {}

    def get_applications(self) -> List[Dict[str, Any]]:
        """
        Reads the applications.json config file for getting the local applications

        Returns:
            A list of applications available in the config file

        Raises:
            MalformedJsonFile: If the config file contains invalid json
        """
        applications_config = self.__config_dir / 'applications.json'
        application_list = []
        if applications_config.is_file():
            try:
                with open(applications_config) as fp:
                    applications = json.load(fp)
                    for app_name, app_data in applications.items():
                        app_data['name'] = app_name
                        application_list.append(app_data)
                    return application_list
            except json.decoder.JSONDecodeError as exception:
                logging.error('The file %s does not contain valid json. Error: %s', applications_config, exception)
                raise MalformedJsonFile(exception) from exception
        else:
            logging.info('The configuration file %s was not found. '
                         'Maybe, you haven\'t created any local applications yet?', applications_config)
            return application_list

    def application_exists(self, application: str) -> bool:
        return True

    def remote_application_exists(self, application: str) ->  int:
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
