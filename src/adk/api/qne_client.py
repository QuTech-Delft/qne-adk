from datetime import datetime, timezone
import re
from typing import Any, cast, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import jwt
import requests
from requests.models import Response
from requests.auth import AuthBase

from apistar import Client
from apistar.client.auth import TokenAuthentication
from apistar.exceptions import ErrorResponse, ClientError

from adk.exceptions import ApiClientError, NotLoggedIn
from adk.managers.auth_manager import AuthManager
from adk.parsers.encoders import JSONEncoder
from adk.type_aliases import (ActionsType, ParametersType, TemplateType, NodeType, ChannelType, NetworkType,
                              ApplicationType, AppVersionType, AppSourceType, AppConfigType, AppResultType,
                              RoundSetType, AssetType, ExperimentType, ResultType, FinalResultType, BackendType,
                              NetworkListType, UserType, BackendTypeType, TokenType)


class QneClient:
    """Client to connect to the api-router.

    A client to make a connection to the api-router via OpenAPI. For each user a specific client is created with user
    credentials.

    Args:
        auth_manager: authentication manager
    """
    def __init__(self, auth_manager: AuthManager) -> None:
        self.__auth_manager = auth_manager
        self.__base_uri = self.__auth_manager.get_active_host()
        self.__username: Optional[str] = self.__auth_manager.get_username(self.__base_uri)
        self.__password: Optional[str] = self.__auth_manager.get_password(self.__base_uri)
        self.__refresh_token: Optional[str] = self.__auth_manager.load_token(self.__base_uri)

        self.__headers: Dict[str, str] = {}
        self.__openapi_client_class = Client
        self.__auth_class = TokenAuthentication
        self.__client: Client = None

    def _set_open_api_client(self, auth: Optional[AuthBase] = None) -> None:
        """Sets or updates the open api client mainly because of access tokens changing.

        The reason we do not override __client is because _call_with_retries might be "keeping" a reference
        to the previous in callable_. For example, if we reached here because of an access token refresh
        the callable_ still holds the action that raised the initial 401 with a reference of __client with
        an invalid access token. If we don't "fix" that reference the retried action will raise a 401 again.
        """
        encoders = [JSONEncoder]

        if self.__client:
            self.__client.transport = self.__client.init_transport(encoders=encoders,
                                                                   headers=self.__headers,
                                                                   auth=auth)
        else:
            schema_url = urljoin(self.__base_uri, 'schema/')
            schema = self._client_get(schema_url, headers=self.__headers).json()
            self.__client = self.__openapi_client_class(schema=schema,
                                                        encoders=encoders,
                                                        headers=self.__headers,
                                                        auth=auth)

    def _refresh_token_expired(self) -> None:
        """Checks and sets to None the refresh token if it is expired."""

        if not self.__refresh_token:
            return

        decoded = jwt.decode(self.__refresh_token, options={"verify_signature": False})
        exp = int(decoded['exp'])
        # https://github.com/jpadilla/pyjwt/issues/321#issuecomment-354126200
        now = int(datetime.utcnow().replace(tzinfo=timezone.utc).timestamp())

        if exp <= now:
            self.__refresh_token = None

    def _authentication_access_token(self) -> str:
        """Get the JWT access token for the user either by authenticating with the provided credentials or using the
        refresh token from earlier authentication.
        """

        self._refresh_token_expired()

        jwt_url = urljoin(self.__base_uri, 'jwt/')

        if self.__refresh_token:
            jwt_url = urljoin(jwt_url, 'refresh/')
            payload = {'refresh': self.__refresh_token}
        else:
            payload = {
                'username': self.__username,
                'password': self.__password
            }

        response = self._client_post(jwt_url, data=payload).json()
        self.__refresh_token = response.get("refresh", self.__refresh_token)
        self.__auth_manager.set_token(self.__base_uri, self.__refresh_token)

        return str(response['access'])

    def _authenticate(self) -> None:

        self.__headers = {}
        access_token = self._authentication_access_token()
        self.__headers = {'Authorization': f'JWT {access_token}'}

        auth_mech = TokenAuthentication(access_token, scheme="JWT")
        self._set_open_api_client(auth_mech)

    def login(self, username: str, password: str, host: str) -> Optional[str]:
        self.__refresh_token = None
        self.__base_uri = host
        self.__username = username
        self.__password = password

        self._authenticate()
        return self.__refresh_token

    def logout(self, host: str) -> None:
        self.__client = None
        self.__base_uri = self.__auth_manager.get_active_host()
        self.__username = None
        self.__password = None

    def is_logged_in(self) -> bool:
        if self.__client is None:
            if self.__username is None or self.__password is None:
                return False
        return True

    @staticmethod
    def _client_get(url: str, **params: ParametersType) -> Any:
        result = requests.get(url, **params)
        if isinstance(result, Response):
            result.raise_for_status()
        return result

    @staticmethod
    def _client_post(url: str, **params: ParametersType) -> Any:
        result = requests.post(url, **params)
        if isinstance(result, Response):
            result.raise_for_status()
        return result

    def _action(self, operation_id: ActionsType, **params: ParametersType) -> Any:
        if self.__client is None:
            if self.__username is not None and self.__password is not None:
                self._authenticate()
            else:
                raise NotLoggedIn()
        try:
            return self.__client.request(operation_id, **params)
        except ClientError as error:
            message_text = ''
            for message in error.messages:
                message_text += f"API ClientError ({message.code}): {message.text} {str(message.index) if message.index is not None else ''}\n"
            raise ApiClientError(message_text)
        except ErrorResponse as error:
            if error.status_code != 401:
                message_text = f"API ClientError ({error.status_code}): {error.content}"
                raise ApiClientError(message_text)

            self._authenticate()
            return self.__client.request(operation_id, **params)

    @staticmethod
    def _cast_parameter_type(param_set1: Dict[str, Any],
                             param_set2: Optional[Dict[str, Any]] = None) -> ParametersType:
        """Helper function that merges and casts two dictionaries into a proper parameter dictionary.

        Args:
            param_set1: Set of parameters to be send to the api-router.
            param_set2: Optional set of parameters.

        Returns:
            To parameters_type cast set of parameters.
        """
        if param_set2 is None:
            param_set2 = {}
        return cast(ParametersType, {**param_set1, **param_set2})

    @staticmethod
    def parse_url(url: str) -> Tuple[str, str]:
        """Parse an API url to extract the resource type and id.

        Example: parse_url("http://localhost/api/backends/1/") returns the tuple ("backends", "1").

        Args:
            url: the URL to parse.

        Returns:
            A tuple of the type of endpoint and the corresponding id.
        """
        matches = re.match(r'.*/([^/]+)/([0-9]+)/', url)
        if matches is None:
            raise ValueError("unable to parse url")
        return matches.group(1), matches.group(2)


class QneFrontendClient(QneClient):  # pylint: disable-msg=R0904
    """
        For testing front end functionality.
        All possible endpoints are implemented which can be reached by a front end.
    """
    def create_token(self) -> TokenType:
        response = self._action('createToken')
        return cast(TokenType, response)

    def retrieve_user(self) -> UserType:
        response = self._action('retrieveMeAPIUser')
        return cast(UserType, response)

    def list_applications(self) -> List[ApplicationType]:
        response = self._action('listApplications')
        return cast(List[ApplicationType], response)

    def retrieve_application(self, application_url: str) -> ApplicationType:
        _, application_id = QneClient.parse_url(application_url)
        response = self._action('retrieveApplication', id=application_id)
        return cast(ApplicationType, response)

    def destroy_application(self, application_url: str) -> None:
        _, application_id = QneClient.parse_url(application_url)
        self._action('destroyApplication', id=application_id)

    def app_config_application(self, application_url: str) -> AppConfigType:
        _, application_id = QneClient.parse_url(application_url)
        response = self._action('appConfigApplication', id=application_id)
        return cast(AppConfigType, response)

    def app_result_application(self, application_url: str) -> AppResultType:
        _, application_id = QneClient.parse_url(application_url)
        response = self._action('appResultApplication', id=application_id)
        return cast(AppResultType, response)

    def retrieve_appversion(self, appversion_url: str) -> AppVersionType:
        _, appversion_id = QneClient.parse_url(appversion_url)
        response = self._action('retrieveAppVersion', id=appversion_id)
        return cast(AppVersionType, response)

    def app_config_appversion(self, appversion_url: str) -> AppConfigType:
        _, appversion_id = QneClient.parse_url(appversion_url)
        response = self._action('appConfigAppVersion', id=appversion_id)
        return cast(AppConfigType, response)

    def app_result_appversion(self, appversion_url: str) -> AppResultType:
        _, appversion_id = QneClient.parse_url(appversion_url)
        response = self._action('appResultAppVersion', id=appversion_id)
        return cast(AppResultType, response)

    def retrieve_appconfig(self, appconfig_url: str) -> AppConfigType:
        _, appconfig_id = QneClient.parse_url(appconfig_url)
        response = self._action('retrieveAppConfig', id=appconfig_id)
        return cast(AppConfigType, response)

    def retrieve_appresult(self, appresult_url: str) -> AppResultType:
        _, appresult_id = QneClient.parse_url(appresult_url)
        response = self._action('retrieveAppResult', id=appresult_id)
        return cast(AppResultType, response)

    def create_asset(self, asset: AssetType) -> AssetType:
        params = self._cast_parameter_type(asset)
        response = self._action('createAsset', asset=params)
        return cast(AssetType, response)

    def retrieve_asset(self, asset_url: str) -> AssetType:
        _, asset_id = QneClient.parse_url(asset_url)
        response = self._action('retrieveAsset', id=asset_id)
        return cast(AssetType, response)

    def update_asset(self, asset_url: str, asset: AssetType) -> AssetType:
        _, asset_id = QneClient.parse_url(asset_url)
        params = self._cast_parameter_type(asset)
        response = self._action('updateAsset', id=asset_id, asset=params)
        return cast(AssetType, response)

    def partial_update_asset(self, asset_url: str, asset: AssetType) -> AssetType:
        _, asset_id = QneClient.parse_url(asset_url)
        params = self._cast_parameter_type({
            'network': asset['network'],
            'application': asset['application']
        })
        response = self._action('partialUpdateAsset', id=asset_id, asset=params)
        return cast(AssetType, response)

    def list_default_backendtypes(self) -> List[BackendTypeType]:
        response = self._action('listDefaultBackendTypes')
        return cast(List[BackendTypeType], response)

    def list_backendtypes(self) -> List[BackendTypeType]:
        response = self._action('listBackendTypes')
        return cast(List[BackendTypeType], response)

    def retrieve_backendtypes(self, backendtype_url: str) -> BackendTypeType:
        _, backendtype_id = QneClient.parse_url(backendtype_url)
        response = self._action('retrieveBackendType', id=backendtype_id)
        return cast(BackendTypeType, response)

    def list_backends(self) -> List[BackendType]:
        response = self._action('listBackends')
        return cast(List[BackendType], response)

    def retrieve_backend(self, backend_url: str) -> BackendType:
        _, backend_id = QneClient.parse_url(backend_url)
        response = self._action('retrieveBackend', id=backend_id)
        return cast(BackendType, response)

    def list_experiments(self) -> List[ExperimentType]:
        response = self._action('listExperiments')
        return cast(List[ExperimentType], response)

    def create_experiment(self, experiment: ExperimentType) -> ExperimentType:
        params = self._cast_parameter_type(experiment)
        response = self._action('createExperiment', experiment=params)
        return cast(ExperimentType, response)

    def retrieve_experiment(self, experiment_url: str) -> ExperimentType:
        _, experiment_id = QneClient.parse_url(experiment_url)
        response = self._action('retrieveExperiment', id=experiment_id)
        return cast(ExperimentType, response)

    def update_experiment(self, experiment_url: str, experiment: ExperimentType) -> ExperimentType:
        _, experiment_id = QneClient.parse_url(experiment_url)
        params = self._cast_parameter_type(experiment)
        response = self._action('updateExperiment', id=experiment_id, experiment=params)
        return cast(ExperimentType, response)

    def partial_update_experiment(self, experiment_url: str, experiment: ExperimentType) -> ExperimentType:
        _, experiment_id = QneClient.parse_url(experiment_url)
        params = self._cast_parameter_type({
            'personal_note': experiment['personal_note'],
            'is_marked': experiment['is_marked']
        })
        response = self._action('partialUpdateExperiment', id=experiment_id, experiment=params)
        return cast(ExperimentType, response)

    def destroy_experiment(self, experiment_url: str) -> None:
        _, experiment_id = QneClient.parse_url(experiment_url)
        self._action('destroyExperiment', id=experiment_id)

    def assets_latest_experiment(self, experiment_url: str) -> AssetType:
        _, experiment_id = QneClient.parse_url(experiment_url)
        response = self._action('assetsLatestExperiment', id=experiment_id)
        return cast(AssetType, response)

    def final_results_latest_experiment(self, experiment_url: str) -> FinalResultType:
        _, experiment_id = QneClient.parse_url(experiment_url)
        response = self._action('finalResultsLatestExperiment', id=experiment_id)
        return cast(FinalResultType, response)

    def results_experiments(self, experiment_url: str) -> List[ResultType]:
        _, experiment_id = QneClient.parse_url(experiment_url)
        response = self._action('resultsExperiment', id=experiment_id)
        return cast(List[ResultType], response)

    def round_sets_experiment(self, experiment_url: str) -> List[RoundSetType]:
        _, experiment_id = QneClient.parse_url(experiment_url)
        response = self._action('roundSetsExperiment', id=experiment_id)
        return cast(List[RoundSetType], response)

    def round_sets_latest_experiment(self, experiment_url: str) -> RoundSetType:
        _, experiment_id = QneClient.parse_url(experiment_url)
        response = self._action('roundSetsLatestExperiment', id=experiment_id)
        return cast(RoundSetType, response)

    def list_roundsets(self) -> List[RoundSetType]:
        response = self._action('listRoundSets')
        return cast(List[RoundSetType], response)

    def create_roundset(self, roundset: RoundSetType) -> RoundSetType:
        params = self._cast_parameter_type(roundset)
        response = self._action('createRoundSet', roundset=params)
        return cast(RoundSetType, response)

    def retrieve_roundset(self, roundset_url: str) -> RoundSetType:
        _, roundset_id = QneClient.parse_url(roundset_url)
        response = self._action('retrieveRoundSet', id=roundset_id)
        return cast(RoundSetType, response)

    def final_results_roundset(self, roundset_url: str) -> FinalResultType:
        _, roundset_id = QneClient.parse_url(roundset_url)
        response = self._action('finalResultsRoundSet', id=roundset_id)
        return cast(FinalResultType, response)

    def results_roundset(self, roundset_url: str) -> List[ResultType]:
        _, roundset_id = QneClient.parse_url(roundset_url)
        response = self._action('resultsRoundSet', id=roundset_id)
        return cast(List[ResultType], response)

    def retrieve_result(self, result_url: str) -> ResultType:
        _, result_id = QneClient.parse_url(result_url)
        response = self._action('retrieveResult', id=result_id)
        return cast(ResultType, response)

    def retrieve_finalresult(self, finalresult_url: str) -> FinalResultType:
        _, finalresult_id = QneClient.parse_url(finalresult_url)
        response = self._action('retrieveFinalResult', id=finalresult_id)
        return cast(FinalResultType, response)

    def list_templates(self) -> List[TemplateType]:
        response = self._action('listTemplates')
        return cast(List[TemplateType], response)

    def retrieve_template(self, template_url: str) -> TemplateType:
        _, template_id = QneClient.parse_url(template_url)
        response = self._action('retrieveTemplate', id=template_id)
        return cast(TemplateType, response)

    def list_networks(self) -> List[NetworkListType]:
        response = self._action('listNetworks')
        return cast(List[NetworkListType], response)

    def retrieve_network(self, network_url: str) -> NetworkType:
        _, network_id = QneClient.parse_url(network_url)
        response = self._action('retrieveNetwork', id=network_id)
        return cast(NetworkType, response)

    def list_channels(self) -> List[ChannelType]:
        response = self._action('listChannels')
        return cast(List[ChannelType], response)

    def retrieve_channel(self, channel_url: str) -> ChannelType:
        _, channel_id = QneClient.parse_url(channel_url)
        response = self._action('retrieveChannel', id=channel_id)
        return cast(ChannelType, response)

    def list_nodes(self) -> List[NodeType]:
        response = self._action('listNodes')
        return cast(List[NodeType], response)

    def retrieve_node(self, node_url: str) -> NodeType:
        _, node_id = QneClient.parse_url(node_url)
        response = self._action('retrieveNode', id=node_id)
        return cast(NodeType, response)
