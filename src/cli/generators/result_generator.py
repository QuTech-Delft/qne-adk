from typing import List

from cli.type_aliases import GeneratedResultType, RoundResultType, CumulativeResultType, InstructionType


class ResultGenerator:
    @staticmethod
    def generate(round_number: int, round_result: RoundResultType,
                 instructions: List[InstructionType], cumulative_result: CumulativeResultType) -> GeneratedResultType:
        return {
            'round_number': round_number,
            'round_result': round_result,
            'instructions': instructions,
            'cumulative_result': cumulative_result
        }


class ErrorResultGenerator:
    @staticmethod
    def generate(round_number: int, exception: str, message: str, trace: str) -> GeneratedResultType:
        round_result = {
            "error": {
                "exception": exception,
                "message": message,
                "trace": trace,
            }
        }
        return {
            'round_number': round_number,
            'round_result': round_result,
            'instructions': [],
            'cumulative_result': {}
        }
