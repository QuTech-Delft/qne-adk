from pathlib import Path
from typing import Any, Dict, List
import json
import logging
from cli.exceptions import MalformedJsonFile


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
        logging.error('The file %s does not contain valid json. Error: %s', file, exception)
        raise MalformedJsonFile(exception) from exception


def write_json_file(file: Path, data: Any) -> None:
    """
    Open the 'file' & write the 'data' to the 'file'

    Args:
        file: Path specifying the json file to be written to
        data: Data to be written to file

    """


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
    networks_file = Path.cwd() / "src/cli/networks/networks.json"
    channels_file = Path.cwd() / "src/cli/networks/channels.json"

    # Read network and see which are available
    network_nodes: Dict[str, List[str]] = {}
    with open(networks_file, "r", encoding="utf-8") as networks_fp:
        data_networks = json.load(networks_fp)
        with open(channels_file, "r", encoding="utf-8") as channels_fp:
            data_channels = json.load(channels_fp)
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
                        network_nodes[data_networks["networks"][network]["slug"]] = lst

    return network_nodes


def get_dummy_application() -> Dict[str, Any]:
    dummy_application = {
        "application": [
            {
                "title": "Title for this input parameter",
                "slug": "slug_for_this_input",
                "description": "Description of this input",
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
                "roles": [
                    "role1_given_in_command"
                ]
            }
        ]
    }

    return dummy_application


def get_py_dummy() -> str:
    dummy_main = 'def main():\n    # Put your code here\n    pass\n\n\nif __name__ == "__main__": \n    main()\n'

    return dummy_main
