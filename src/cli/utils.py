import json
import os
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional

from cli.exceptions import MalformedJsonFile, InvalidPathName


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


def copy_files(source_dir: Path, destination_dir: Path, files_list: Optional[List[str]] = None) -> None:
    """
    Copy all the files from source directory to destination directory.
    No sub directories are copied.

    Args:
        source_dir: directory from where files need to be copied
        destination_dir: directory where files need to be copied to
        files_list: A list of file names which need to be copied. If None, all files in directory are copied.

    """
    if not files_list:
        files_list = os.listdir(source_dir)
    for file_name in files_list:
        full_file_name = os.path.join(source_dir, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, destination_dir)
