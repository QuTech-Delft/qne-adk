import json
import os
from pathlib import Path
import shutil
from typing import Any, Dict, List

from cli.exceptions import MalformedJsonFile, InvalidPathName
from cli.settings import BASE_DIR


def read_json_file(file: Path, encoding: str = 'utf-8') -> Any:
    """
    Open the 'file' in 'encoding' format & read the data from the file

    Args:
        file: Path specifying the json file to be read
        encoding: Encoding format in which to open the file

    Returns:
        The data read from json file

    Raises:
        MalformedJsonFile: If the file contains invalid json
    """

    try:
        with open(file, encoding=encoding) as fp:
            return json.load(fp)
    except json.decoder.JSONDecodeError as exception:
        raise MalformedJsonFile(file, exception) from exception


def write_json_file(file: Path, data: Any, encoding: str = 'utf-8') -> None:
    """
    Open the 'file' & write the 'data' to the 'file'

    Args:
        file: Path specifying the json file to be written to
        data: Data to be written to file
        encoding: Encoding format in which to open the file

    """

    with open(file, mode="w", encoding=encoding) as fp:
        json.dump(data, fp, indent=2)

def write_file(file: Path, data: Any, encoding: str = 'utf-8') -> None:
    """
     Open the 'file' & write the 'data' to the 'file'

    Args:
        file: Path specifying the file to be written to
        data: Data to be written to file
        encoding: Encoding format in which to open the file
    """

    with open(file, mode="w", encoding=encoding) as fp:
        fp.write(data)


def reorder_data(original_data: List[Dict[str, Any]], desired_order: List[str]) -> List[Dict[str, Any]]:
    """
    Reorder keys in each dictionary of the original_data so that they are in the order
    specified in the desired_order parameter

    Args:
        original_data: A list containing dictionaries whose keys need to be reordered
        desired_order: A list with key names, specified in the desired order


    Returns:
        A List of dictionaries where each dictionary contains keys in the desired order
    """
    reordered_data = []
    for item in original_data:
        reordered_item = {key: item.get(key, '-') for key in desired_order}
        reordered_data.append(reordered_item)
    return reordered_data

def get_network_nodes() -> Dict[str, List[str]]:
    """
    Loops trough all the networks in networks/networks.json and gets all the nodes within this network.

    returns:
    Returns a dict of networks, each having their own list including the nodes:
    E.g.: {"randstad": ["leiden", "amsterdam", "the_hague"], "the-netherlands": ["etc..",]}

    """
    networks_file = Path(BASE_DIR) / "networks/networks.json"
    channels_file = Path(BASE_DIR) / "networks/channels.json"

    # Read network and see which are available
    network_nodes: Dict[str, List[str]] = {}

    data_networks = read_json_file(networks_file)
    data_channels = read_json_file(channels_file)

    for network in data_networks["networks"]:
        for channel in data_channels["channels"]:
            if channel["slug"] in data_networks["networks"][network]["channels"]:
                if data_networks["networks"][network]["slug"] not in network_nodes:
                    network_nodes[data_networks["networks"][network]["slug"]] = []
                lst = network_nodes[data_networks["networks"][network]["slug"]]
                if channel["node1"] not in lst:
                    lst.append(channel["node1"])
                if channel["node2"] not in lst:
                    lst.append(channel["node2"])

    return network_nodes


def get_dummy_application(roles: List[Any]) -> List[Dict[str, Any]]:
    dummy_application = [
      {
        "title": "Title for this application",
        "description": "Description of this application",
        "values": [
          {
            "name": "x",
            "default_value": 0,
            "minimum_value": 0,
            "maximum_value": 1,
            "unit": "",
            "scale_value": 1.0
          }
        ],
        "input_type": "number",
        "roles": roles
      }
    ]

    return dummy_application


def get_py_dummy() -> str:
    dummy_main = 'def main():\n    # Put your code here\n    return {}\n\n\nif __name__ == "__main__": \n    main()\n'

    return dummy_main


def validate_path_name(obj: str, name: str) -> None:
    """ Checks if the name of a certain object, can be used as part of a path.
    An Exception is raised when name contains an incompatible character.
    """
    invalid_chars = ['/', '\\', '*', ':', '?', '"', '<', '>', '|']
    if any(char in name for char in invalid_chars):
        raise InvalidPathName(obj)

def get_network_slug(network_name: str) -> str:
    """
    Get the slug associated with the network based on the name of the network

    Args:
        network_name: Name of the network

    Returns:
        The slug for the given network
    """
    return ''


def get_network_name(network_slug: str) -> str:
    """
    Get the name associated with the network based on the slug of the network

    Args:
        network_slug: Slug of the network

    Returns:
        The Name for the given network
    """
    return ''


def get_channels_for_network(network_slug: str) -> List[str]:
    """
    Get the list of channels available in the network

    Args:
        network_slug: Slug of the network

    Returns:
        List of channels
    """
    return [
        "amsterdam-leiden",
        "leiden-the-hague",
        "delft-the-hague",
        "delft-rotterdam"
      ]


def get_channel_info(channel_slug: str) -> Dict[str, Any]:
    """
    Get the channel information containing node & parameter information

    Args:
        channel_slug: Slug of the channel

    Returns:
        Channel information containing node & parameter information
    """
    return {
      "slug": "amsterdam-leiden",
      "node1": "amsterdam",
      "node2": "leiden",
      "parameters": [
        "elementary-link-fidelity"
      ]
    }

def get_node_info(node_slug: str) -> Dict[str, Any]:
    """
    Get the node information containing node parameters & qubit information

    Args:
        node_slug: Slug of the Node

    Returns:
        Node information containing node parameters & information
    """
    return {
      "name": "Amsterdam",
      "slug": "amsterdam",
      "coordinates": {
        "latitude": 52.3667,
        "longitude": 4.8945
      },
      "node_parameters": [
        "gate-fidelity"
      ],
      "number_of_qubits": 3,
      "qubit_parameters": [
        "relaxation-time",
        "dephasing-time"
      ]
    }

def get_templates() -> Dict[str, Dict[str, Any]]:
    """
    Get all the templates information

    Returns:
        A dictionary containing key as template slug and value as template information
    """
    return {
        "elementary-link-fidelity" : {
              "title": "Elementary Link Fidelity",
              "slug": "elementary-link-fidelity",
              "values": [
                {
                  "name": "fidelity",
                  "default_value": 1.0,
                  "minimum_value": 0.5,
                  "maximum_value": 1.0,
                  "unit": "",
                  "scale_value": 1.0
                }
              ],
              "input_type": "fidelity_slider"
            }
    }


def copy_files(source_dir: Path, destination_dir: Path) -> None:
    """
    Copy all the files from source directory to destination directory
    No sub directories are copied

    Args:
        source_dir: directory from where files need to be copied
        destination_dir: directory where files need to be copied to

    """
    for file_name in os.listdir(source_dir):
        full_file_name = os.path.join(source_dir, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, destination_dir)
