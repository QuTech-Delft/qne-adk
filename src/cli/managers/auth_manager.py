from typing import Any, Dict

from cli.types import (FallbackFunctionType, LoginFunctionType,
                       TokenFetchFunctionType)


class AuthManager:
    def __init__(
        self,
        config_dir: str,
        login_function: LoginFunctionType,
        fallback_function: FallbackFunctionType,
    ):
        self.__config_dir = config_dir
        self.__login_function = login_function
        self.__fallback_function = fallback_function

    def login(self, username: str, password: str, host: str) -> None:
        pass

    def load_token(self) -> str:
        pass

    def __store_token(self, token: str) -> None:
        pass

    def __fetch_token(
        self, function: TokenFetchFunctionType, payload: Dict[str, Any]
    ) -> str:
        pass

    def delete_token(self, host: str) -> None:
        pass

    def set_active_host(self, host: str) -> None:
        pass
