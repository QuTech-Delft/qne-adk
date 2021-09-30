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
        self.application = 'test_application'
        self.roles = ['role1', 'role2']
        self.path = Path('path/to/application')
        self.remote_List = ['r1', 'r2']
        self.local_list = ['l1', 'l2', 'l3']

    def test_login(self):
        with patch.object(RemoteApi, "login") as remote_login_mock:
            self.processor.login(host=self.host, username=self.username, password=self.password)
            remote_login_mock.assert_called_once_with(username=self.username, password=self.password, host=self.host)

    def test_logout(self):
        with patch.object(RemoteApi, "logout") as remote_logout_mock:
            self.processor.logout(host=self.host)
            remote_logout_mock.assert_called_once_with(host=self.host)

    def test_applications_create(self):
        with patch.object(LocalApi, "create_application") as create_application_mock:
            self.processor.applications_create(application=self.application, roles=self.roles, path=self.path)
            create_application_mock.assert_called_once_with(self.application, self.roles, self.path)

    def test_applications_validate(self):
        with patch.object(LocalApi, "is_application_valid") as is_application_valid_mock:
            self.processor.applications_validate(self.application)
            is_application_valid_mock.assert_called_once_with(self.application)


    def test_experiments_create_local(self):
        with patch.object(LocalApi, "experiments_create") as create_exp_mock, \
             patch.object(LocalApi, "get_application_config") as get_config_mock, \
             patch.object(LocalApi, "is_network_available") as check_network_mock:
            get_config_mock.return_value = {'foo': 'bar'}
            check_network_mock.return_value = True
            self.processor.experiments_create(name='test_exp', application='app_name', network_name='network_1',
                                              local=True, path='test')
            get_config_mock.assert_called_once_with('app_name')
            check_network_mock.assert_called_once_with('network_1', {'foo': 'bar'})
            create_exp_mock.assert_called_once_with(name='test_exp', app_config={'foo': 'bar'},
                                                    network_name='network_1', path='test', application='app_name')

    def test_experiments_create_remote(self):
        success, message = self.processor.experiments_create(name='test_exp', application='app_name',
                                                             network_name='network_1', local=False, path='test')

        self.assertEqual(success, False)
        self.assertEqual(message, 'Remote experiment creation is not yet enabled.')

    def test_experiments_validate(self):
        with patch.object(LocalApi, "validate_experiment") as validate_exp_mock:
            validate_exp_mock.return_value = True, 'ok'
            success, message = self.processor.experiments_validate(path=Path('dummy'))
            validate_exp_mock.assert_called_once_with(Path('dummy'))
            self.assertEqual(success, True)
            self.assertEqual(message, 'ok')

            validate_exp_mock.reset_mock()
            validate_exp_mock.return_value = False, 'experiment.json does not contain valid json'
            success, message = self.processor.experiments_validate(path=Path('dummy'))
            validate_exp_mock.assert_called_once_with(Path('dummy'))
            self.assertEqual(success, False)
            self.assertEqual(message, 'experiment.json does not contain valid json')

    def test_experiments_run(self):
        with patch.object(LocalApi, "is_experiment_local") as is_exp_local_mock, \
             patch.object(LocalApi, "run_experiment") as run_exp_mock, \
             patch.object(CommandProcessor, '_CommandProcessor__store_results') as store_result_mock:

            is_exp_local_mock.return_value = True
            run_exp_mock.return_value = ['foo']
            self.processor.experiments_run(Path('dummy'), True)

            is_exp_local_mock.assert_called_once_with(Path('dummy'))
            run_exp_mock.assert_called_once_with(Path('dummy'))
            store_result_mock.assert_called_once_with(['foo'])

            is_exp_local_mock.reset_mock()
            run_exp_mock.reset_mock()
            store_result_mock.reset_mock()
            run_exp_mock.return_value = None
            self.processor.experiments_run(Path('dummy'), True)
            is_exp_local_mock.assert_called_once_with(Path('dummy'))
            run_exp_mock.assert_called_once_with(Path('dummy'))
            store_result_mock.assert_not_called()

    def test_experiments_result(self):
        with patch.object(LocalApi, "is_experiment_local") as is_exp_local_mock, \
             patch.object(LocalApi, "get_results") as results_mock, \
             patch.object(CommandProcessor, '_CommandProcessor__store_results') as store_result_mock:

            is_exp_local_mock.return_value = True
            results_mock.return_value = ['foo']
            self.processor.experiments_results(True, False, Path('dummy'))
            is_exp_local_mock.assert_called_once_with(Path('dummy'))
            results_mock.assert_called_once_with(Path('dummy'), True)
            store_result_mock.assert_called_once_with(['foo'])

            is_exp_local_mock.reset_mock()
            results_mock.reset_mock()
            store_result_mock.reset_mock()
            self.processor.experiments_results(True, True, Path('dummy'))
            is_exp_local_mock.assert_called_once_with(Path('dummy'))
            results_mock.assert_called_once_with(Path('dummy'), True)
            store_result_mock.assert_not_called()

    def test_applications_list(self):
        with patch.object(LocalApi, "list_applications") as local_list_applications_mock, \
            patch.object(RemoteApi, "list_applications") as remote_list_applications_mock:

            remote_list_applications_mock.return_value = self.remote_List
            local_list_applications_mock.return_value = self.local_list
            applications = self.processor.applications_list(remote=True, local=True)

            local_list_applications_mock.assert_called_once()
            remote_list_applications_mock.assert_called_once()

            self.assertIn('local', applications)
            self.assertIn('remote', applications)
            self.assertEqual(len(applications), 2)
            self.assertEqual(len(applications['local']), 3)
            self.assertEqual(len(applications['remote']), 2)

    def test_applications_list_local(self):
        with patch.object(LocalApi, "list_applications") as local_list_applications_mock, \
            patch.object(RemoteApi, "list_applications") as remote_list_applications_mock:

            local_list_applications_mock.return_value = self.local_list
            applications = self.processor.applications_list(remote=False, local=True)

            local_list_applications_mock.assert_called_once()
            remote_list_applications_mock.assert_not_called()

            self.assertIn('local', applications)
            self.assertNotIn('remote', applications)
            self.assertEqual(len(applications), 1)
            self.assertEqual(len(applications['local']), 3)

    def test_applications_list_remote(self):
        with patch.object(LocalApi, "list_applications") as local_list_applications_mock, \
            patch.object(RemoteApi, "list_applications") as remote_list_applications_mock:

            remote_list_applications_mock.return_value = self.remote_List
            applications = self.processor.applications_list(remote=True, local=False)

            remote_list_applications_mock.assert_called_once()
            local_list_applications_mock.assert_not_called()

            self.assertIn('remote', applications)
            self.assertNotIn('local', applications)
            self.assertEqual(len(applications), 1)
            self.assertEqual(len(applications['remote']), 2)
