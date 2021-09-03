from pathlib import Path
from unittest.mock import patch
import unittest

from cli.api.remote_api import RemoteApi
from cli.managers.config_manager import ConfigManager
from cli.managers.auth_manager import AuthManager

class TestRemoteApi(unittest.TestCase):

    def setUp(self):
        config_manager = ConfigManager(config_dir=Path('dummy'))
        self.remote_api = RemoteApi(config_manager=config_manager)
        self.host = 'test'
        self.username = 'test_username'
        self.password = 'test_password'

    def test_login(self):
        with patch.object(AuthManager, "login") as login_mock:
            self.remote_api.login(username=self.username, password=self.password, host=self.host)
            login_mock.assert_called_once_with(username=self.username, password=self.password, host=self.host)

    def test_logout(self):
        with patch.object(AuthManager, "get_active_host") as get_active_host_mock, \
            patch.object(AuthManager, "delete_token") as delete_token_mock:
            self.remote_api.logout(host=None)
            get_active_host_mock.assert_called_once()
            delete_token_mock.assert_called_once()

    def test_logout_with_host(self):
        with patch.object(AuthManager, "get_active_host") as get_active_host_mock, \
            patch.object(AuthManager, "delete_token") as delete_token_mock:
            self.remote_api.logout(host=self.host)
            get_active_host_mock.assert_not_called()
            delete_token_mock.assert_called_once_with(self.host)
