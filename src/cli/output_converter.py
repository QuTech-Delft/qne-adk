import os
import shutil
from typing import List, Optional

from cli.generators.network_generator import FullyConnectedNetworkGenerator
from cli.type_aliases import ResultType


class OutputConverter:
    def __init__(self, round_set, log_dir: str, output_dir: str,
                 instruction_converter: Optional[FullyConnectedNetworkGenerator] = None):
        self._log_dir = log_dir
        self._output_dir = output_dir
        self._instruction_converter = instruction_converter

    def prepare_output(self) -> None:
        if not os.path.isdir(self._log_dir):
            os.makedirs(self._log_dir)
        print("OutputCOnverter prepare_output() called")

    def convert(self, round_number: int, result_list: List[ResultType]) -> ResultType:
        pass

    def __clean(self) -> None:
        """Cleans all files from the log directory.

        All yaml files and instructions json file have to be deleted. Given that the directory is automatically created,
        all files can be safely deleted.

        Note: Keep in mind never to point the output or cache directory to an actual source folder.
        """
        if os.path.isdir(self._log_dir):
            shutil.rmtree(self._log_dir)
        os.makedirs(self._log_dir)

    def terminate(self) -> None:
        """Terminate this OutputConverter."""
        self.__clean()
