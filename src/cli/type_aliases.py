from typing import Any, Callable, Dict, List, Union

ExperimentType = Dict[str, Any]
ResultType = Dict[str, Any]
ApplicationType = Dict[str, Any]
AppConfigType = Dict[str, Any]
app_configNetworkType = Dict[str, List[str]]
app_configApplicationType = List[Dict[str, Any]]

LoginFunctionType = Callable[[str, str, str], str]
FallbackFunctionType = Callable[[], str]
TokenFetchFunctionType = Union[LoginFunctionType, FallbackFunctionType]
