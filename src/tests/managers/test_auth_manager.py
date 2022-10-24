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
        self.email = 'test@email.com'
        self.password = 'test_password'
        self.use_username = False

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
            auth_manager.login(email=self.email, password=self.password, host=self.host, use_username=self.use_username)
            fetch_token_mock.assert_called_once_with(self.login_function,
                                       {'email': self.email, 'password': self.password,
                                        'host': self.host, 'use_username': self.use_username})
            expected = {f"{self.host}": {"token": 'token', "email": self.email,
                                         "password": self.password, 'use_username': '1' if self.use_username else '0'}}
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
            auth_manager.login(email=None, password=None, host=None, use_username=None)
            fetch_token_mock.assert_called_once_with(self.fallback_function, {'host': QNE_URL})
            expected = {f"{QNE_URL}": {"token": 'token', "email": None, "password": None, "use_username": None}}
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
            auth_config = {f"{self.host}": {"token": 'token', "email": self.email, "password": self.password}}
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
            auth_config = {f"{self.host}": {"token": token_to_load, "email": self.email,
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
            auth_config = {f"{self.host}": {"token": 'token', "email": self.email, "password": self.password}}
            read_json_mock.return_value = auth_config

            auth_manager.set_token(self.host, token_to_set)

            expected_auth_config = {f"{self.host}": {"token": token_to_set, "email": self.email,
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
            auth_config = {f"{self.host}": {"token": token, "email": self.email, "password": self.password}}
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
            auth_manager.login(email=self.email, password=self.password,
                               host=new_active_host, use_username=self.use_username)
            active_host = auth_manager.get_active_host()
            self.assertEqual(active_host, new_active_host)
            expected_auth_config = {f"{active_host}": {"token": 'token',
                                                       "email": self.email,
                                                       "password": self.password,
                                                       'use_username': '1' if self.use_username else '0'}}
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
            auth_config = {f"{self.host}": {"token": 'token', "email": self.email,
                                            "password": password_to_get, "use_username": self.use_username}}
            read_json_mock.return_value = auth_config

            password = auth_manager.get_password(self.host)
            self.assertEqual(password, password_to_get)

            read_json_mock.return_value = {}

            password = auth_manager.get_password(self.host)
            self.assertIsNone(password)

    def test_get_email(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch("adk.managers.auth_manager.read_json_file") as read_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)
            email_to_get = 'get@email.com'
            auth_config = {f"{self.host}": {"token": 'token', "email": email_to_get,
                                            "password": self.password, "use_username": self.use_username}}
            read_json_mock.return_value = auth_config

            email = auth_manager.get_email(self.host)
            self.assertEqual(email, email_to_get)

            read_json_mock.return_value = {}

            email = auth_manager.get_email(self.host)
            self.assertIsNone(email)

    def test_get_use_username(self):
        with patch("adk.managers.auth_manager.Path.is_file", return_value=True), \
             patch("adk.managers.auth_manager.os.path.isdir", return_value=True), \
             patch("adk.managers.auth_manager.Path.mkdir"), \
             patch.object(AuthManager, "_AuthManager__read_active_host", return_value='host'), \
             patch("adk.managers.auth_manager.read_json_file") as read_json_mock:

            auth_manager = AuthManager(config_dir=self.path, login_function=self.login_function,
                                       fallback_function=self.fallback_function, logout_function=self.logout_function)
            use_username_to_get = '1'
            auth_config = {f"{self.host}": {"token": 'token', "email": self.email, "password": self.password,
                                            "use_username": use_username_to_get}}
            read_json_mock.return_value = auth_config

            use_username = auth_manager.get_use_username(self.host)
            self.assertEqual(use_username, True)

            use_username_to_get = '0'
            auth_config = {f"{self.host}": {"token": 'token', "email": self.email, "password": self.password,
                                            "use_username": use_username_to_get}}
            read_json_mock.return_value = auth_config

            use_username = auth_manager.get_use_username(self.host)
            self.assertEqual(use_username, False)

            read_json_mock.return_value = {}

            use_username = auth_manager.get_use_username(self.host)
            self.assertIsNone(use_username)
