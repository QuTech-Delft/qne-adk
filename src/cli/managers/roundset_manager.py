import os
from pathlib import Path
import shutil
import subprocess
from subprocess import CalledProcessError, TimeoutExpired
from typing import Any, cast, Dict, List, Optional

from cli.output_converter import OutputConverter
from cli.generators.network_generator import FullyConnectedNetworkGenerator
from cli.generators.result_generator import ErrorResultGenerator
from cli.generators.template_generator import RoleTemplate, RoleMappingTemplate, NetworkTemplate
from cli.type_aliases import AssetType, ErrorDictType, GeneratedResultType


class RoundSetManager:
    def __init__(self, round_set, asset: Dict[str, Any], path: Path) -> None:
        self.__round_set = round_set
        self.__asset = asset
        # self.__cache_dir = "./cache"
        self.__input_dir = str(path / "input")
        self.__log_dir = str(path / "raw_output")
        self.__output_dir = str(path / "LAST")
        self.__fully_connected_network_generator = FullyConnectedNetworkGenerator()
        self.__output_converter = OutputConverter(
            round_set=self.__round_set,
            log_dir=self.__log_dir,
            output_dir=self.__output_dir,
            instruction_converter=self.__fully_connected_network_generator
        )
        print("RoundsetManager initialized __init__")

    def process(self) -> Optional[List[GeneratedResultType]]:
        print("RoundsetManager process() called")
        self.__output_converter.prepare_output()
        round_failed = False
        round_number = 1
        result = None

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
            print("Error occurred while processing round %d", round_number)
            result = ErrorResultGenerator.generate(round_number, exception_type, message, trace)

            # Terminate will clear the output dir and log dir
            # self.__output_converter.terminate()
        else:
            # Experiment run was successful
            print("Round was successful")

        return result

    def validate_asset(self, path: Path, error_dict: ErrorDictType) -> Any:
        pass

    def prepare_input(self) -> None:

        # Clean will remove all files from input dir. We dont want that
        # self.__clean()

        role_mapping = self.__get_role_mapping(self.__asset)
        print(f"Role Mapping for the exp is {role_mapping}")
        # Example: {
        #         "role1": "amsterdam",
        #         "role2": "leiden"
        #       }

        # This step not needed as py files are aready present in the experiment folder / input dir
        # Create app_*.py files
        # self.resource_manager.prepare_resources(app_source)

        # Create *.yaml files
        for role_name in role_mapping.keys():
            self._create_role_file(self.__asset, role_name)
            print(f"Created yaml  role file for {role_name}")

        # Create network.yaml file
        self._create_network_file(self.__asset, role_mapping)
        print(f"Created Network yaml file for {role_mapping}")

        # Create roles.yaml file
        self._create_roles_file(role_mapping)
        print(f"Created roles.yaml file")

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
        # input_dir = self.__configuration.get('paths', 'input_dir')
        # log_dir = self.__configuration.get('paths', 'log_dir')
        # logging.info("Running application from %s", input_dir)
        # logging.info("Logging results to %s", log_dir)

        print("run_application called..")
        subprocess.run(
            ["netqasm", "simulate", "--app-dir", self.__input_dir, "--log-dir", self.__log_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True,
            timeout=60
        )
        print("run_application Finished")
        # logging.info("Finished running application. Logs available in %s", log_dir)

    @staticmethod
    def __get_role_mapping(asset: AssetType) -> Dict[str, str]:
        """Retrieve a mapping of roles with nodes they are performed on.

        In a quantum network, different nodes will have different roles. This method will extract a mapping
        role -> node. The node in this is the geographical location, while the role is a part of the algorithm that is
        run.

        Args:
            asset: user configuration for this specific run of the algorithm.

        Return:
            A dictionary of role -> node mappings.
        """
        network = cast(Dict[str, Dict[str, str]], asset["network"])
        return network["roles"]

    @staticmethod
    def _get_selected_network(asset: AssetType) -> Dict[str, Any]:
        """Get the network description from the Asset.

        The Asset contains the network that was selected by the end user. This network is returned by this method.

        Args:
            asset: user input for a specific run of an application.

        Return:
            The network the end user has selected.
        """
        network = cast(Dict[str, Any], asset["network"])
        return network

    def _create_role_file(self, asset: AssetType, role_name: str) -> None:
        """Create configuration file for a specific role.

        The various role in an application may or may not receive individual parameters. These parameters are stored
        in <role_name>.yaml files in the input_dir in yaml format.

        Args:
            role_name: Name of the role that is performed on the node.
            asset: user configuration that should be used.
        """
        template = RoleTemplate(self.__input_dir, role_name.lower())
        template.create_config(parameters=asset, role_name=role_name)
        template.render()

    def _create_network_file(self, asset: AssetType, role_mapping: Dict[str, Any]) -> None:
        """Create configuration file detailing the node - role mappings.

        The Quantum Network backend expects a description of the network that can be used by the backend. This
        description contains the nodes and channels with the appropriate weights (gate_fidelity, link_fidelity etc).
        This description and accompanying parameters are stored in the `network.yaml` file.

        Args:
            asset: user configuration that should be used.
            role_mapping: mapping of role on node.
        """
        network = self._get_selected_network(asset)
        template = NetworkTemplate(self.__input_dir, "network")
        template.create_config(network=network)
        template.make_network_fully_connected(role_mapping, self.__fully_connected_network_generator)
        template.render()

    def _create_roles_file(self, role_mapping: Dict[str, str]) -> None:
        """

        The Quantum Network backend expects a `roles.yaml` file which details the mapping of roles to nodes. This method
        stores this mapping in the appropriate file.

        Args:
            role_mapping: mapping of role on node.
        """
        template = RoleMappingTemplate(self.__input_dir, "roles")
        template.create_config(role_mapping=role_mapping)
        template.render()
