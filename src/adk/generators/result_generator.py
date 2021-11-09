from typing import List

from adk.type_aliases import ResultType, RoundSetType, RoundResultType, CumulativeResultType, InstructionType


class ResultGenerator:
    @staticmethod
    def generate(round_set: RoundSetType, round_number: int, round_result: RoundResultType,
                 instructions: List[InstructionType], cumulative_result: CumulativeResultType) -> ResultType:
        return {
            'round_number': round_number,
            'round_set': str(round_set['url']),
            'round_result': round_result,
            'instructions': instructions,
            'cumulative_result': cumulative_result
        }


class ErrorResultGenerator:
    @staticmethod
    def generate(round_set: RoundSetType, round_number: int, exception: str, message: str, trace: str) -> ResultType:
        round_result = {
            "error": {
                "exception": exception,
                "message": message,
                "trace": trace,
            }
        }
        return {
            'round_number': round_number,
            'round_set': str(round_set['url']),
            'round_result': round_result,
            'instructions': [],
            'cumulative_result': {}
        }
