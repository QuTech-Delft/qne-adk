from typing import Any, Callable, Dict, List, Union

ExperimentType = Dict[str, Any]
ResultType = Dict[str, Any]
ApplicationType = Dict[str, Any]
AppConfigType = Dict[str, Any]
app_configNetworkType = Dict[str, List[str]]
app_configApplicationType = List[Dict[str, Any]]
assetNetworkType = Dict[str, Any]
assetApplicationType = List[Dict[str, Any]]
NetworkData = Dict[str, Dict[str, Dict[str, Any]]]
ChannelData = Dict[str, List[Dict[str, Any]]]
NodeData = Dict[str, List[Dict[str, Any]]]

LoginFunctionType = Callable[[str, str, str], str]
FallbackFunctionType = Callable[[], str]
TokenFetchFunctionType = Union[LoginFunctionType, FallbackFunctionType]

ErrorDictType = Dict[str, List[str]]
