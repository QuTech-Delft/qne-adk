from typing import List

from cli.type_aliases import ResultType


class OutputConverter:
    def __init__(self, log_dir: str, output_dir: str):
        self.__log_dir = log_dir
        self.__output_dir = output_dir

    def convert(self, round_number: int, result_list: List[ResultType]) -> ResultType:
        pass

    def terminate(self) -> None:
        pass
