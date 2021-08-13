from typing import Any, Callable, Dict, Union

ExperimentType = Dict[str, Any]
ResultType = Dict[str, Any]
ApplicationType = Dict[str, Any]
AppConfigType = Dict[str, Any]

LoginFunctionType = Callable[[str, str, str], str]
FallbackFunctionType = Callable[[], str]
TokenFetchFunctionType = Union[LoginFunctionType, FallbackFunctionType]
