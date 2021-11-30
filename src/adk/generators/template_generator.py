import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

import yaml

from adk.generators.network_generator import FullyConnectedNetworkGenerator
from adk.type_aliases import TemplateType

class BaseTemplate(ABC):
    """Base template for creating necessary config files for NetSquid.

    For the execution of a Quantum Network algorithm, configuration files are needed. These configuration files are
    generated based on the asset that the end user provides. This base template provides elementary functions for the
    generation of those files.

    Args:
         config_dir: directory where the configuration files should be saved.
         file_name: name of the configuration file - will be appended by `.yaml`.
    """

    def __init__(self, config_dir: str, file_name: str):
        self._config_dir = config_dir
        self._file_name = file_name
        self._config: Dict[str, Any] = {}

    @abstractmethod
    def create_config(self, *args: Any, **kwargs: Any) -> None:
        """Method that converts user input from an asset to a configuration representation.

        Args:
            args: position based arguments.
            kwargs: keyword arguments.
        """
        raise NotImplementedError("This method has not been implemented yet.")

    def render(self) -> None:
        """Write a configuration to the appropriate file."""
        config_file_path = os.path.join(self._config_dir, f"{self._file_name}.yaml")
        with open(config_file_path, 'w', encoding='utf-8') as config_file:
            yaml.dump(self._config, config_file)

    @staticmethod
    def _unpack_template(templates: TemplateType, param_key: str, role: Optional[str] = None) -> Dict[str, Any]:
        """Method to unpack a list of templates.

        By design, templates are contained in a list. Every template has a values list that contains all
        values of that template. This method unpacks all values and from the listed templates and combines them on root
        level in a dictionary.

        Args:
            templates: Object that contains a list of templates.
            param_key: key for the list of templates.
            role: optional role for which to filter.

        Returns:
            A flattened list of template values of this object.
        """
        return {
            content['name']: content['value']
            for template in templates[param_key]
            for content in template['values']
            if role is None or role in template['roles']
        }


class RoleTemplate(BaseTemplate):
    def create_config(self, *args: Any, **kwargs: Any) -> None:
        """Convert role specific parameters to a configuration.

        Users of an application can specify parameters that should be set for a role. These parameters should be
        collected and stored in a `<role>.yaml` file. This method takes care of the collection part.

        Args:
             role_name: the name of the role that should be collected.
             parameters: the application parameters.
        """
        role_name = str(kwargs['role_name'])
        parameters = kwargs['parameters']
        self._config = self._unpack_template(parameters, 'application', role_name)


class NetworkTemplate(BaseTemplate):
    def create_config(self, *args: Any, **kwargs: Any) -> None:
        """Convert network specific parameters to a configuration.

        Users can tweak the network that is used for the run of the application. The values that are set for the
        network should be collected and stored in a configuration that can be saved in `network.yaml`. This method
        takes care of collecting the `nodes` and `links` that represent this network and the flattening of the
        parameter list.

        Args:
              network: The network object that represents the actual network.
        """
        network = kwargs['network']

        network_description: Dict[str, List[Any]] = {
            "nodes": [],
            "links": []
        }
        for node in network["nodes"]:
            network_description['nodes'].append(self.__create_node_config(node))
        for channel in network["channels"]:
            network_description["links"].append(self.__create_link_config(channel))
        self._config = network_description

    def make_network_fully_connected(self, role_mapping: Dict[str, Any],
                                     network_generator: Optional[FullyConnectedNetworkGenerator] = None) -> None:
        if network_generator is not None:
            self._config = network_generator.generate(self._config, role_mapping)

    def __create_node_config(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Create the node representation.

        Args:
              node: A single node from the network description.

        Returns:
              Configuration specific to this node.
        """
        node_dict = {
            "name": node['slug'],
        }
        node_dict.update(self._unpack_template(node, 'node_parameters'))
        node_dict['qubits'] = []
        for qubit in node['qubits']:
            node_dict['qubits'].append(self.__create_qubit_config(qubit))
        return node_dict

    def __create_qubit_config(self, qubit: Dict[str, Any]) -> Dict[str, Any]:
        """Create configuration for a specific qubit.

        Every node contains one or multiple qubits. This method takes care of converthing these qubits into dictionary
        representations that can be stored in the `network.yaml` file.

        Args:
            qubit: A single qubit for a specific node.

        Returns:
            Configuration specific to this qubit.
        """
        qubit_dict = {
            'id': qubit['qubit_id']
        }
        qubit_dict.update(self._unpack_template(qubit, 'qubit_parameters'))
        return qubit_dict

    def __create_link_config(self, link: Dict[str, Any]) -> Dict[str, Any]:
        """Create configuration for a specific link.

        A link is a quantum connection between two nodes that travels over a physical connection (i.e. a channel). This
        method converts the data about that link to an actual configuration.

        Args:
            link: A single link that connects two nodes.

        Returns:
            Configuration specific to this link.
        """
        # Temporarily added to cover the noise_type as well.
        link['parameters'].append(self.__get_noise_type())
        link_dict = {
            'name': f"{link['node1']}-{link['node2']}",
            'node_name1': link['node1'],
            'node_name2': link['node2'],
        }
        link_dict.update(self._unpack_template(link, 'parameters'))
        return link_dict

    @staticmethod
    def __get_noise_type() -> Dict[str, Any]:
        """Temporary function for the addition of a noise_type."""
        return {
            'slug': 'link_noise_type',
            'values': [{
                'name': 'noise_type',
                'value': 'Depolarise'
            }]
        }


class RoleMappingTemplate(BaseTemplate):
    def create_config(self, *args: Any, **kwargs: Any) -> None:
        """Convert mapping of roles onto specific nodes to a configuration.

        Users can map roles onto selected nodes. This method converts this mapping into a configuration that can be
        used by the simulator. This should always be of the form `{lower_case_role: lower_case_node }`.

        Args:
            role_mapping: A mapping of roles on nodes.
        """
        role_mapping = kwargs['role_mapping']
        self._config = {
            role.lower(): node.lower()
            for role, node in role_mapping.items()
        }
