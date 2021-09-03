from pathlib import Path
from unittest.mock import patch
import unittest

from cli.api.local_api import LocalApi
from cli.api.remote_api import RemoteApi
from cli.command_processor import CommandProcessor
from cli.managers.config_manager import ConfigManager

class TestCommandProcessor(unittest.TestCase):

    def setUp(self):
        self.config_manager = ConfigManager(config_dir=Path('dummy'))
        self.local_api = LocalApi(config_manager=self.config_manager)
        self.remote_api = RemoteApi(config_manager=self.config_manager)
        self.processor = CommandProcessor(local_api=self.local_api, remote_api=self.remote_api)
        self.host = 'qutech.com'
        self.username = 'test_username'
        self.password = 'test_password'

    def test_login(self):
        with patch.object(RemoteApi, "login") as remote_login_mock:
            self.processor.login(host=self.host, username=self.username, password=self.password)
            remote_login_mock.assert_called_once_with(username=self.username, password=self.password, host=self.host)

    def test_logout(self):
        with patch.object(RemoteApi, "logout") as remote_logout_mock:
            self.processor.logout(host=self.host)
            remote_logout_mock.assert_called_once_with(host=self.host)
