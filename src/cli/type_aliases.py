from typing import Any, Callable, Dict, List, Union
from typing_extensions import TypedDict

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
TemplateData = Dict[str, List[Dict[str, Any]]]
GenericNetworkData = Dict[str, Any]

LoginFunctionType = Callable[[str, str, str], str]
FallbackFunctionType = Callable[[], str]
TokenFetchFunctionType = Union[LoginFunctionType, FallbackFunctionType]

ErrorDictType = Dict[str, List[str]]
DefaultPayloadType = Union[int, str]
LinkType = Dict[str, Union[str, float]]
QuantumStateType = List[List[Dict[str, float]]]


class DijkstraNode(TypedDict):
    effective_fidelity: float
    channels: List[str]
    final: bool


RoundResultType = Dict[str, Any]
CumulativeResultType = Dict[str, Any]
InstructionType = Dict[str, Any]
LogEntryType = Dict[str, Any]
NetworkType = Dict[str, List[Dict[str, Any]]]
GeneratedResultType = Dict[str, Union[DefaultPayloadType, RoundResultType, CumulativeResultType, List[InstructionType]]]
TemplatesType = Dict[str, List[Dict[str, Any]]]
AssetType = Dict[str, Union[DefaultPayloadType, assetNetworkType, assetApplicationType]]
