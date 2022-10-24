import os.path
from pathlib import Path
from typing import Any, Dict, Optional

from adk.exceptions import DirectoryIsFile
from adk.type_aliases import (AuthType, FallbackFunctionType, LoginFunctionType, LogoutFunctionType,
                              TokenFetchFunctionType)
from adk.utils import read_json_file, write_json_file

QNE_URL = os.environ.get('QNE_URL', 'https://api.quantum-network.com')


class AuthManager:
    def __init__(self, config_dir: Path, login_function: LoginFunctionType, fallback_function: FallbackFunctionType,
                 logout_function: LogoutFunctionType):
        if os.path.isfile(str(config_dir)):
            raise DirectoryIsFile(str(config_dir))
        if not os.path.isdir(str(config_dir)):
            config_dir.mkdir(parents=True)
        self.auth_config = config_dir / 'qnerc'

        if not self.auth_config.is_file():
            self.__create_config()

        self.__login_function = login_function
        self.__fallback_function = fallback_function
        self.__logout_function = logout_function
        self.__active_host = self.__read_active_host()

    def login(self, email: Optional[str], password: Optional[str], host: Optional[str],
              use_username: Optional[bool]) -> None:
        """
        When a token is not found it tries to log in
        with basic authentication read from the environment variables QNE_EMAIL and QNE_PASSWORD. When the environment
        variables are not both set, email and password are read from standard input.

        :param email: e-mail
        :param password: password
        :param host: the Quantum Network host for which we try to log in
        :param use_username: use the username field to log in instead of email

        """
        if host is None:
            host = QNE_URL
        if email is not None and password is not None and host is not None:
            token = self.__fetch_token(self.__login_function,
                                       {'email': email, 'password': password,
                                        'host': host, 'use_username': use_username})
        else:
            token = self.__fetch_token(self.__fallback_function, {'host': host})

        self.__store_token(host, token, email, password, use_username)
        self.__set_active_host(host)

    def logout(self, host: Optional[str]) -> None:
        if host is None:
            host = self.get_active_host()
        self.__logout_function(host)
        self.__delete_token(host)
        # fall back to default host
        self.__set_active_host(QNE_URL)

    def load_token(self, host: str) -> Optional[str]:
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

    def __store_token(self, host: str, token: str, email: Optional[str], password: Optional[str],
                      use_username: Optional[bool]) -> None:
        """Save the token for a host to a file. Currently, allowing one login at a time.

        :param host: the Quantum Network host for which the token is saved.
        :param token: the Quantum Network token to save.
        :param email: the email to save.
        :param password: the password to save.
        :param use_username: the flag to use email or username to save.
        """
        accounts = {}
        accounts[host] = {"token": token, "email": email, "password": password,
                          "use_username": None if use_username is None else '1' if use_username else '0'}
        write_json_file(self.auth_config, accounts)

    def set_token(self, host: str, token: str) -> None:
        accounts: AuthType = read_json_file(self.auth_config)

        if host in accounts:
            accounts[host]["token"] = token
            write_json_file(self.auth_config, accounts)

    def get_host_from_token(self, token: str) -> Optional[str]:
        """Get the host for a certain token.

        :param token: the token for which the Quantum Network host is searched for.
        """
        accounts: AuthType = read_json_file(self.auth_config)
        for uri in accounts:
            if accounts[uri]["token"] == token:
                return uri
        return None

    def __fetch_token(self, function: TokenFetchFunctionType, payload: Dict[str, Any]) -> str:
        return function(**payload)   # type: ignore[call-arg]

    def __delete_token(self, host: str) -> None:
        """Delete the entry for a host.

        :param host: the Quantum Network host for which the token is deleted.
        """
        accounts: AuthType = read_json_file(self.auth_config)
        for uri in accounts:
            if uri.lower() == host.lower():
                del accounts[uri]
                write_json_file(self.auth_config, accounts)
                break

    def __read_active_host(self) -> str:
        """Read the host from the auth configs (first entry)"""
        accounts: AuthType = read_json_file(self.auth_config)
        account_list = list(accounts)
        return account_list[0] if len(account_list) > 0 else QNE_URL

    def __set_active_host(self, host: str) -> None:
        """Set the active host"""
        self.__active_host = host

    def get_active_host(self) -> str:
        """Get the active host"""
        return self.__active_host

    def __get_item_from_host(self, host: str, item: str) -> Optional[str]:
        accounts: AuthType = read_json_file(self.auth_config)

        if host in accounts:
            return accounts[host].get(item)
        return None

    def get_password(self, host: str) -> Optional[str]:
        return self.__get_item_from_host(host, "password")

    def get_email(self, host: str) -> Optional[str]:
        return self.__get_item_from_host(host, "email")

    def get_use_username(self, host: str) -> Optional[bool]:
        use_username = self.__get_item_from_host(host, "use_username")
        return None if use_username is None else True if use_username == '1' else False
