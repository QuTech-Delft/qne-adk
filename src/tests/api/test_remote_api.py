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

        self.experiment_meta_remote = {
            "backend": {
                "location": "remote",
                "type": "netsquid",
             },
            "number_of_rounds": 1,
            "description": ""
        }

        self.experiment_data_remote = {'meta': self.experiment_meta_remote, 'asset': {}}

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

    def test_list_application(self):
        with patch.object(AuthManager, "load_token") as load_token_mock, \
            patch.object(RemoteApi, "_action") as action_mock:
            load_token_mock.return_value = 'token'
            self.remote_api.list_applications()

            load_token_mock.assert_called_once()
            action_mock.assert_called_once_with('listApplications', {'token': 'token'})

    def test_create_experiment(self):
        with patch("cli.api.remote_api.write_json_file") as write_mock:
            self.remote_api.create_experiment('test', {'foo': 'bar'}, Path('dummy'))

            self.experiment_data_remote['meta']['description'] = 'test: experiment description'
            self.experiment_data_remote['asset'] = {'foo': 'bar'}

            write_mock.assert_called_once_with(Path('dummy') / 'experiment.json', self.experiment_data_remote)

    def test_get_application_config(self):
        with patch.object(ConfigManager, "remote_application_exists") as remote_application_mock:
            remote_application_mock.return_value = (True, 1)
            self.remote_api.get_application_config('test')
