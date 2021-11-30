import json
import os.path
from pathlib import Path
from typing import Any, Dict, Optional

from adk.exceptions import DirectoryIsFile
from adk.type_aliases import (FallbackFunctionType, LoginFunctionType, LogoutFunctionType,
                              TokenFetchFunctionType)
from adk.utils import read_json_file, write_json_file

# username = os.environ.get('QNE_EMAIL', None)
# password = os.environ.get('QNE_PASSWORD', None)
QNE_URL = os.environ.get('QNE_URL', 'https://api.quantum-network.com')


class AuthManager:
    def __init__(self, config_dir: Path, login_function: LoginFunctionType, fallback_function: FallbackFunctionType,
                 logout_function: LogoutFunctionType):
        self.__config_dir = config_dir
        if os.path.isfile(str(self.__config_dir)):
            raise DirectoryIsFile(str(self.__config_dir))
        if not os.path.isdir(str(self.__config_dir)):
            self.__config_dir.mkdir(parents=True)
        self.auth_config = self.__config_dir / 'qnerc'

        if not self.auth_config.is_file():
            self.__create_config()

        self.__login_function = login_function
        self.__fallback_function = fallback_function
        self.__logout_function = logout_function
        self.__active_host = self.__read_active_host()

    def login(self, username: Optional[str], password: Optional[str], host: Optional[str]) -> None:
        """
        When a token is not found it tries to login
        with basic authentication read from the environment variables QNE_EMAIL and QNE_PASSWORD. When the environment
        variables are not both set, email and password are read from standard input.

        :param username: username (e-mail)
        :param password: password
        :param host: the Quantum Network host for which we try to log in

        """
        if host is None:
            host = QNE_URL
        if username is not None and password is not None and host is not None:
            token = self.__fetch_token(self.__login_function,
                                       {'username': username, 'password': password, 'host': host})
        else:
            token = self.__fetch_token(self.__fallback_function, {'host': host})

        self.__store_token(host, token, username, password)
        self.__set_active_host(host)

    def logout(self, host: Optional[str]) -> None:
        if host is None:
            host = self.get_active_host()
        self.__logout_function(host)
        self.__delete_token(host)
        # fall back to default host
        self.__set_active_host(QNE_URL)

    def load_token(self, host: str) -> str:
        """ Try to load an earlier stored Quantum Network token from file.

        :param host: the Quantum Network host.
        :return:
            The Quantum Network token or None when no token is found.
        """
        token = self.__read_token(host)
        # if token is None:
        #     token = self.__fetch_token(self.__fallback_function, {'host': host})
        return token

    def __create_config(self) -> None:
        """ Creates the authorization config file in the .qne/ root directory"""
        write_json_file(self.auth_config, {})

    def __read_token(self, host: str) -> Optional[str]:
        """ Try to read an earlier stored Quantum Network token from file for a certain host.

        :param host: the Quantum Network host.
        :return:
            The Quantum Network token for this host or None when no token is found or token is empty.
        """
        return self.__get_item_from_host(host, "token")

    def __store_token(self, host: str, token: str, username: str, password: str) -> None:
        """Save the token for a host to a file. Currently allowing one login at a time.

        :param host: the Quantum Network host for which the token is saved.
        :param token: the Quantum Network token to save.
        """
        accounts = dict()
        accounts[host] = {"token": token, "username": username, "password": password}
        write_json_file(self.auth_config, accounts)

    def set_token(self, host: str, token: str) -> None:
        accounts = read_json_file(self.auth_config)

        if host in accounts:
            accounts[host]["token"] = token
            write_json_file(self.auth_config, accounts)

    def get_host_from_token(self, token: str) -> Optional[str]:
        """Get the host for a certain token.

        :param host: the Quantum Network host for which the token is deleted.
        """
        accounts = read_json_file(self.auth_config)
        for uri in accounts:
            if accounts[uri]["token"] == token:
                return uri
        return None

    def __fetch_token(
        self, function: TokenFetchFunctionType, payload: Dict[str, Any]
    ) -> str:
        return function(**payload)   # type: ignore[call-arg]

    def __delete_token(self, host: str) -> None:
        """Delete the entry for a host.

        :param host: the Quantum Network host for which the token is deleted.
        """
        accounts = read_json_file(self.auth_config)
        for uri in accounts:
            if uri.lower() == host.lower():
                del accounts[uri]
                write_json_file(self.auth_config, accounts)
                break

    def __read_active_host(self) -> Optional[str]:
        """Read the host from the auth configs (first entry)"""
        accounts = read_json_file(self.auth_config)
        account_list = list(accounts)
        return account_list[0] if len(account_list) > 0 else QNE_URL

    def __set_active_host(self, host: str) -> None:
        """Set the active host"""
        self.__active_host = host

    def get_active_host(self) -> str:
        """Get the active host"""
        return self.__active_host

    def __get_item_from_host(self, host: str, item: str) -> Optional[str]:
        accounts = read_json_file(self.auth_config)

        if host in accounts:
            return accounts[host][item]
        return None

    def get_password(self, host: str) -> Optional[str]:
        return self.__get_item_from_host(host, "password")

    def get_username(self, host: str) -> Optional[str]:
        return self.__get_item_from_host(host, "username")
