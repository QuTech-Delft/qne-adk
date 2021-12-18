from unittest.mock import Mock, patch
import unittest

from adk.managers.auth_manager import AuthManager


class TestAuthManager(unittest.TestCase):

    def setUp(self):
        self.login_function = Mock()
        self.fallback_function = Mock()
        self.auth_manager = AuthManager(config_dir='test_config_dir', login_function=self.login_function,
                                        fallback_function=self.fallback_function)
        self.host = 'test'
        self.username = 'test_username'
        self.password = 'test_password'

    def test_login(self):
        with patch.object(AuthManager, "_AuthManager__fetch_token") as fetch_token_mock, \
         patch.object(AuthManager, "_AuthManager__store_token") as store_token_mock, \
         patch.object(AuthManager, "set_active_host") as set_active_host_mock:
            fetch_token_mock.return_value = 'token'
            self.auth_manager.login(username=self.username, password=self.password, host=self.host)
            fetch_token_mock.assert_called_once_with(self.login_function,
                                       {'username': self.username, 'password': self.password, 'host': self.host})
            store_token_mock.assert_called_once_with('token')
            set_active_host_mock.assert_called_once_with(self.host)

    def test_login_without_credentials(self):
        with patch.object(AuthManager, "_AuthManager__fetch_token") as fetch_token_mock, \
         patch.object(AuthManager, "_AuthManager__store_token") as store_token_mock, \
         patch.object(AuthManager, "_AuthManager__get_host_from_token") as host_token_mock, \
         patch.object(AuthManager, "set_active_host") as set_active_host_mock:
            fetch_token_mock.return_value = 'token'
            host_token_mock.return_value = 'host_from_token'
            self.auth_manager.login(username=None, password=None, host=None)
            fetch_token_mock.assert_called_once_with(self.fallback_function, {})
            store_token_mock.assert_called_once_with('token')
            host_token_mock.assert_called_once_with('token')
            set_active_host_mock.assert_called_once_with('host_from_token')

    def test_get_active_host(self):
        host = self.auth_manager.get_active_host()
        self.assertEqual(host, 'HOST')

    def test_load_token(self):
        with patch.object(AuthManager, "_AuthManager__fetch_token") as fetch_token_mock, \
             patch.object(AuthManager, "_AuthManager__has_token") as has_token_mock, \
             patch.object(AuthManager, "_AuthManager__get_token") as get_token_mock:

            has_token_mock.return_value = True
            self.auth_manager.load_token()
            get_token_mock.assert_called_once()
            fetch_token_mock.assert_not_called()

            has_token_mock.reset_mock()
            fetch_token_mock.reset_mock()
            get_token_mock.reset_mock()
            has_token_mock.return_value = False
            self.auth_manager.load_token()
            fetch_token_mock.assert_called_once()
            get_token_mock.assert_not_called()
