import os
from pathlib import Path
import shutil
import subprocess
from subprocess import CalledProcessError, TimeoutExpired
from typing import Any, Dict

from adk.parsers.input_parser import InputParser
from adk.parsers.output_converter import OutputConverter
from adk.generators.network_generator import FullyConnectedNetworkGenerator
from adk.generators.result_generator import ErrorResultGenerator
from adk.type_aliases import ResultType, RoundSetType


class RoundSetManager:
    """
    This class runs a single round of the application on the simulator.
    Uses the InputParser class to process the input and prepare it for running application on netqasm.
    Uses the OutputConverter class to process the output of netqasm and convert it to a result in QNE format.
    If the application run fails, then an error result is generated containing the reason for failure.
    """
    def __init__(self, round_set: RoundSetType, asset: Dict[str, Any], path: Path) -> None:
        self.__asset = asset
        self.__round_set = round_set
        self.__path = path
        self.__input_dir = str(path / "input")
        self.__log_dir = str(path / "raw_output")
        self.__output_dir = "LAST"
        self.__fully_connected_network_generator = FullyConnectedNetworkGenerator()
        self.__input_parser = InputParser(
            input_dir=str(path / "input"),
            network_generator=self.__fully_connected_network_generator
        )
        self.__output_converter = OutputConverter(
            round_set=self.__round_set,
            log_dir=self.__log_dir,
            output_dir=self.__output_dir,
            instruction_converter=self.__fully_connected_network_generator
        )

    def process(self) -> ResultType:
        """
        Process a round by running the application on simulator.

        Returns:
            The result of the application run
        """
        round_failed = False
        round_number = 1
        self.__input_parser.prepare_input(self.__asset)
        self.__output_converter.prepare_output()

        try:
            self._run_application()
        except CalledProcessError as exc:
            exception_type = type(exc).__name__
            message = f"NetQASM returned with exit status {exc.returncode}."
            trace = exc.stderr.decode() if exc.stderr is not None else None
            round_failed = True
        except TimeoutExpired as exc:
            exception_type = type(exc).__name__
            message = f"Call to simulator timed out after {exc.timeout} seconds."
            trace = exc.stderr.decode() if exc.stderr is not None else None
            round_failed = True
        except Exception as exc:
            exception_type = type(exc).__name__
            trace = None
            message = str(exc)
            round_failed = True

        if round_failed:
            result = ErrorResultGenerator.generate(self.__round_set, round_number, exception_type, message, trace)
        else:
            result = self.__output_converter.convert(round_number)

        return result

    def __clean(self) -> None:
        """Cleans up all files in the input directory.

        Given that the source files provided by the application developer can have any format (not just app_*.py, but
        also src/*.py) all pythons need to be deleted. Furthermore, all *.yaml files need to be removed. Given that the
        directory is automatically created, all files can be safely deleted.

        Note: Keep in mind never to point the input or cache directory to an actual source folder.
        """
        if os.path.isdir(self.__input_dir):
            shutil.rmtree(self.__input_dir)
        os.makedirs(self.__input_dir)

    def terminate(self) -> None:
        """Clean up everything that the InputParser/RoundsetManager has created."""
        self.__clean()

    def _run_application(self) -> None:
        """Execute the subprocess that runs the application on squidasm.

        Squidasm reads the directory that contains both the source and configuration files for an application. This
        method will trigger a subprocess running squidasm with a prepared directory containing these files.

        Raises:
            CalledProcessError: If the application has failed, an exception is raised.
            TimeoutExpired: If the application runs longer than expected.
        """

        subprocess.run(
            ["netqasm", "simulate", "--app-dir", self.__input_dir, "--log-dir", self.__log_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True,
            timeout=60
        )
