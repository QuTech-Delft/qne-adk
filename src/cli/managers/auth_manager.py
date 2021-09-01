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
        if username is not None and password is not None and host is not None:
            token = self.__fetch_token(self.__login_function,
                                       {'username': username, 'password': password, 'host': host})
        else:
            token = self.__fetch_token(self.__fallback_function, {})

        self.__store_token(token)

        if host is not None:
            self.set_active_host(host)
        else:
            self.set_active_host(host='?')

    def load_token(self) -> str:
        if self.__has_token():
            token = self.__get_token()
        else:
            token = self.__fetch_token(self.__fallback_function, {})

        return token

    def __has_token(self) -> bool:
        pass

    def __get_token(self) -> str:
        return '****'

    def __store_token(self, token: str) -> None:
        pass

    def __fetch_token(
        self, function: TokenFetchFunctionType, payload: Dict[str, Any]
    ) -> str:
        return function(**payload)   # type: ignore[call-arg]

    def delete_token(self, host: str) -> None:
        pass

    def set_active_host(self, host: str) -> None:
        pass

    def get_active_host(self) -> str:
        return 'HOST'
