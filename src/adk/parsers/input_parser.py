import os
import shutil
from typing import Any, Dict, Optional, cast

from adk.generators.network_generator import FullyConnectedNetworkGenerator
from adk.generators.template_generator import RoleTemplate, NetworkTemplate, RoleMappingTemplate
from adk.type_aliases import AssetType


class InputParser:
    def __init__(self, input_dir: str, network_generator: Optional[FullyConnectedNetworkGenerator] = None) -> None:
        self._input_dir = input_dir
        self._network_generator = network_generator

    def prepare_input(self, asset: AssetType) -> None:
        """Create input yaml files for the application.

        An application requires various files for running: app_<node>.py, <node>.yaml and network.yaml. This function
        unwraps the asset and stores the appropriate data in the YAML files.

        Args:
            asset: user input for a specific run of an application.
        """
        role_mapping = self.__get_role_mapping(asset)

        # Create *.yaml files
        for role_name in role_mapping.keys():
            self._create_role_file(asset, role_name)

        # Create network.yaml file
        self._create_network_file(asset, role_mapping)

        # Create roles.yaml file
        self._create_roles_file(role_mapping)

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
        template = RoleTemplate(self._input_dir, role_name.lower())
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
        template = NetworkTemplate(self._input_dir, "network")
        template.create_config(network=network)
        template.make_network_fully_connected(role_mapping, self._network_generator)
        template.render()

    def _create_roles_file(self, role_mapping: Dict[str, str]) -> None:
        """

        The Quantum Network backend expects a `roles.yaml` file which details the mapping of roles to nodes. This method
        stores this mapping in the appropriate file.

        Args:
            role_mapping: mapping of role on node.
        """
        template = RoleMappingTemplate(self._input_dir, "roles")
        template.create_config(role_mapping=role_mapping)
        template.render()

    def __clean(self) -> None:
        """Cleans up all files in the input directory.

        Given that the source files provided by the application developer can have any format (not just app_*.py, but
        also src/*.py) all pythons need to be deleted. Furthermore, all *.yaml files need to be removed. Given that the
        directory is automatically created, all files can be safely deleted.

        Note: Keep in mind never to point the input or cache directory to an actual source folder.
        """
        if os.path.isdir(self._input_dir):
            shutil.rmtree(self._input_dir)
        os.makedirs(self._input_dir)

    def terminate(self) -> None:
        """Clean up everything that the InputParser has created."""
        self.__clean()
