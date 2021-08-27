from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
from cli.utils import read_json_file


class ConfigManager:
    def __init__(self, config_dir: Path):
        self.__config_dir = config_dir

    def add_application(self, application: str, path: Path) -> None:
        """
        Takes care of saving the application name in the .qne/application.json root file together with the application
        path.

        Args:
            application: the application name
            roles: a list of roles
            path: the path where the application is stored

        """

        app_config_file = self.__config_dir / "applications.json"

        # Read json file
        with app_config_file.open(mode="r") as fp:
            apps = json.load(fp)

        # Store the app path
        apps[application] = {'path': str(path)}
        with app_config_file.open(mode="w") as fp:
            json.dump(apps, fp, indent=4)

    def __check_and_create_config(self) -> bool:
        app_config_file = Path.home() / ".qne/applications.json"
        if not app_config_file.exists():
            with app_config_file.open(mode="w") as fp:
                json.dump({}, fp, indent=4)
            return True
        return False

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

    def application_exists(self, application: str) -> bool:
        """
        Checks if the application name already exists in .qne/application.json for unique purposes. If the file is
        non-existing, the application won't exist and returns True. If it does exist, return False, else True.

        Args:
            application: the application name

        """

        # Loop through .qne/applications.json to see if name exists

        app_config_file = Path.home() / ".qne/applications.json"
        with app_config_file.open(mode="r") as application_json:
            data = application_json.read()
            data = json.loads(data)

        for key in data:
            if key == application:
                return False

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
