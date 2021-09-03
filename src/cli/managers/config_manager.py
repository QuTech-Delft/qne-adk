from pathlib import Path
from typing import Dict, List, Tuple

class ConfigManager:
    def __init__(self, config_dir: Path):
        self.__config_dir = config_dir

    def add_application(self, application: str, path: str) -> None:
        pass

    def delete_application(self, application: str) -> None:
        pass

    def get_application(self, application: str) -> Dict[str, str]:
        return {}

    def get_application_from_path(self, path: Path) -> Tuple[str, Dict[str, str]]:
        return "key", {}

    def get_applications(self) -> List[Dict[str, str]]:
        return [{}]

    def application_exists(self, application: str) -> bool:
        return True

    def remote_application_exists(self, application: str) -> Tuple[bool, int]:
        """
        Check if the application is already created on remote
        by checking the remote_id field in the config file.
        Returns True and application id if application exists on remote
        Returns False and -1 if application does not exist on remote
        """
        application_info = self.get_application(application)
        if 'remote_id' in application_info:
            return True, int(application_info['remote_id'])

        return False, -1

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
