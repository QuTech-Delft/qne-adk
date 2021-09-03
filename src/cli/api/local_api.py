from pathlib import Path
from typing import List, Optional

from cli.managers.config_manager import ConfigManager
from cli.managers.roundset_manager import RoundSetManager
from cli.output_converter import OutputConverter
from cli.types import (AppConfigType, ApplicationType, ExperimentType,
                       ResultType)


class LocalApi:
    def __init__(self, config_manager: ConfigManager) -> None:
        self.__config_manager = config_manager

    def create_application(self, application: str, roles: List[str], app_path: Path) -> None:
        if self.__is_application_unique(application):
            self.__create_application_structure(application, roles, app_path)
        else:
            pass

    def init_application(self, path: Path) -> None:
        # Find out application name & roles from the files in 'path'
        application = ''
        roles = ['', '']

        if self.__is_application_unique(application):
            self.__create_application_structure(application, roles, path)


    def __create_application_structure(
        self, application: str, roles: List[str], path: Path
    ) -> None:
        self.__config_manager.add_application(application, path)

    def list_applications(self) -> List[ApplicationType]:
        return self.__config_manager.get_applications()

    def __is_application_unique(self, application: str) -> bool:
        return self.__config_manager.application_exists(application)

    def is_application_valid(self, application: str) -> bool:
        return self.__is_structure_valid(application) and \
               self.__is_application_unique(application) and \
               self.__is_config_valid(application)

    def __is_structure_valid(self, application: str) -> bool:
        pass

    def __is_config_valid(self, application: str) -> bool:
        pass

    def get_application_config(self, application: str) -> AppConfigType:
        pass

    def create_experiment(
        self, name: str, app_config: AppConfigType, local: bool
    ) -> None:
        pass

    def delete_experiment(self, path: Path) -> None:
        pass


    def run_experiment(self, path: Path, block: bool) -> Optional[List[ResultType]]:
        roundSetManager = RoundSetManager()
        roundSetManager.prepare_input(str(path.resolve()))
        roundSetManager.process()
        roundSetManager.terminate()
        return []

    def get_experiment(self, name: str) -> ExperimentType:
        pass

    def get_results(self, name: str) -> List[ResultType]:
        outputConverter = OutputConverter('log_dir', 'output_dir')
        round_number = 1
        result_list: List[ResultType] = []
        output_result: List[ResultType] = []
        output_result.append(outputConverter.convert(round_number, result_list))
        return output_result

    def validate_experiment(self, path: Path) -> bool:
        roundSetManager = RoundSetManager()
        return roundSetManager.validate_asset(path)

