from pathlib import Path
from unittest.mock import Mock, patch
import unittest

from adk.managers.auth_manager import AuthManager, QNE_URL


class TestAuthManager(unittest.TestCase):

    def setUp(self):
        self.login_function = Mock()
        self.logout_function = Mock()
        self.fallback_function = Mock()
        self.path = Path('path/to/application')
        self.host = 'http://unittest_server/'
        self.username = 'test_username'
        self.password = 'test_password'

    def test_login(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch.object(AuthManager, "_AuthManager__fetch_token") as fetch_token_mock, \
             patch.object(AuthManager, "_AuthManager__set_active_host") as set_active_host_mock, \
             patch("adk.managers.auth_manager.write_json_file") as write_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)

            fetch_token_mock.return_value = 'token'
            auth_manager.login(username=self.username, password=self.password, host=self.host)
            fetch_token_mock.assert_called_once_with(self.login_function,
                                       {'username': self.username, 'password': self.password, 'host': self.host})
            expected = {f"{self.host}": {"token": 'token', "username": self.username, "password": self.password}}
            write_json_mock.assert_called_once_with(self.path / 'qnerc', expected)
            set_active_host_mock.assert_called_once_with(self.host)

    def test_login_without_credentials(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch.object(AuthManager, "_AuthManager__fetch_token") as fetch_token_mock, \
             patch.object(AuthManager, "_AuthManager__set_active_host") as set_active_host_mock, \
             patch("adk.managers.auth_manager.write_json_file") as write_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)

            fetch_token_mock.return_value = 'token'
            auth_manager.login(username=None, password=None, host=None)
            fetch_token_mock.assert_called_once_with(self.fallback_function, {'host': QNE_URL})
            expected = {f"{QNE_URL}": {"token": 'token', "username": None, "password": None}}
            write_json_mock.assert_called_once_with(self.path / 'qnerc', expected)
            set_active_host_mock.assert_called_once_with(QNE_URL)

    def test_logout(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch.object(AuthManager, "get_active_host") as get_active_host_mock, \
             patch.object(AuthManager, "_AuthManager__set_active_host") as set_active_host_mock, \
             patch("adk.managers.auth_manager.read_json_file") as read_json_mock, \
             patch("adk.managers.auth_manager.write_json_file") as write_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)
            get_active_host_mock.return_value = self.host
            auth_config = {f"{self.host}": {"token": 'token', "username": self.username, "password": self.password}}
            read_json_mock.return_value = auth_config
            auth_manager.logout(None)
            self.logout_function.assert_called_once_with(self.host)
            write_json_mock.assert_called_once_with(self.path / 'qnerc', {})
            set_active_host_mock.assert_called_once_with(QNE_URL)

    def test_load_token(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch("adk.managers.auth_manager.read_json_file") as read_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)
            token_to_load = 'token_to_load'
            auth_config = {f"{self.host}": {"token": token_to_load, "username": self.username,
                                            "password": self.password}}
            read_json_mock.return_value = auth_config

            loaded_token = auth_manager.load_token(self.host)
            self.assertEqual(loaded_token, token_to_load)

            read_json_mock.return_value = {}

            loaded_token = auth_manager.load_token(self.host)
            self.assertIsNone(loaded_token)

    def test_set_token(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch("adk.managers.auth_manager.read_json_file") as read_json_mock, \
             patch("adk.managers.auth_manager.write_json_file") as write_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)
            token_to_set = 'token_to_set'
            auth_config = {f"{self.host}": {"token": 'token', "username": self.username, "password": self.password}}
            read_json_mock.return_value = auth_config

            auth_manager.set_token(self.host, token_to_set)

            expected_auth_config = {f"{self.host}": {"token": token_to_set, "username": self.username,
                                                     "password": self.password}}
            write_json_mock.assert_called_once_with(self.path / 'qnerc', expected_auth_config)

    def test_get_host_from_token(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch("adk.managers.auth_manager.read_json_file") as read_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)
            token = 'token'
            auth_config = {f"{self.host}": {"token": token, "username": self.username, "password": self.password}}
            read_json_mock.return_value = auth_config

            the_host = auth_manager.get_host_from_token(token)
            self.assertEqual(the_host, self.host)

            the_host = auth_manager.get_host_from_token('non_existing_token')
            self.assertIsNone(the_host)

    def test_get_active_host(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch.object(AuthManager, "_AuthManager__fetch_token") as fetch_token_mock, \
             patch("adk.managers.auth_manager.write_json_file") as write_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)
            fetch_token_mock.return_value = 'token'
            new_active_host = 'new_active_host'
            auth_manager.login(username=self.username, password=self.password, host=new_active_host)
            active_host = auth_manager.get_active_host()
            self.assertEqual(active_host, new_active_host)
            expected_auth_config = {f"{active_host}": {"token": 'token', "username": self.username,
                                                       "password": self.password}}
            write_json_mock.assert_called_once_with(self.path / 'qnerc', expected_auth_config)

    def test_get_password(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch("adk.managers.auth_manager.read_json_file") as read_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)
            password_to_get = 'password_to_get'
            auth_config = {f"{self.host}": {"token": 'token', "username": self.username, "password": password_to_get}}
            read_json_mock.return_value = auth_config

            password = auth_manager.get_password(self.host)
            self.assertEqual(password, password_to_get)

            read_json_mock.return_value = {}

            password = auth_manager.get_password(self.host)
            self.assertIsNone(password)

    def test_get_username(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch("adk.managers.auth_manager.read_json_file") as read_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)
            username_to_get = 'username_to_get'
            auth_config = {f"{self.host}": {"token": 'token', "username": username_to_get, "password": self.password}}
            read_json_mock.return_value = auth_config

            username = auth_manager.get_username(self.host)
            self.assertEqual(username, username_to_get)

            read_json_mock.return_value = {}

            username = auth_manager.get_username(self.host)
            self.assertIsNone(username)
