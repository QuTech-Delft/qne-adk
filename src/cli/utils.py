import json
import logging
from pathlib import Path
from typing import Any

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
        logging.error('The file %s does not contain valid json. Error: %s',file, exception)
        raise MalformedJsonFile(exception) from exception

def write_json_file(file: Path, data: Any) -> None:
    """
    Open the 'file' & write the 'data' to the 'file'

    Args:
        file: Path specifying the json file to be written to
        data: Data to be written to file

    """
