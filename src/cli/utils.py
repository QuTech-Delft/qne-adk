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
