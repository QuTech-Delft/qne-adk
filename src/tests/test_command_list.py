import unittest

from unittest.mock import patch
from typer.testing import CliRunner

from cli.command_list import app, applications_app, experiments_app
from cli.command_processor import CommandProcessor
from cli.managers.config_manager import ConfigManager

class TestCommandList(unittest.TestCase):

    def setUp(self):
        self.application = 'test_application'
        self.roles = ["role1, role2"]
        self.runner = CliRunner()

    def test_login(self):
        with patch.object(CommandProcessor, "login") as login_mock:
            login_output = self.runner.invoke(app, ['login', 'test_host'], input="test_username\ntest_password")
            login_mock.assert_called_once_with(host='test_host', username='test_username', password='test_password')
            self.assertEqual(login_output.exit_code, 0)
            self.assertIn('Log in succeeded.', login_output.stdout)

    def test_logout(self):
        with patch.object(CommandProcessor, "logout") as logout_mock:
            logout_output = self.runner.invoke(app, ['logout'])
            logout_mock.assert_called_once_with(host=None)
            self.assertEqual(logout_output.exit_code, 0)
            self.assertIn('Log out succeeded.', logout_output.stdout)

            logout_mock.reset_mock()
            logout_output = self.runner.invoke(app, ['logout', 'qutech.com'])
            logout_mock.assert_called_once_with(host='qutech.com')
            self.assertEqual(logout_output.exit_code, 0)
            self.assertIn('Log out succeeded.', logout_output.stdout)

    def test_applications_create(self):
        with patch("cli.command_list.Path.cwd") as mock_cwd,\
             patch.object(CommandProcessor, 'applications_create') as application_create_mock:

            mock_cwd.return_value = 'test'

            application_create_output = self.runner.invoke(applications_app,
                                                           ['create', 'test_application', 'role1', 'role2'])
            mock_cwd.assert_called_once()
            application_create_mock.assert_called_once()
            self.assertEqual(application_create_output.exit_code, 0)
            self.assertIn('Application successfully created.', application_create_output.stdout)

    def test_applications_validate(self):
        with patch("cli.command_list.Path.cwd") as mock_cwd, \
             patch.object(ConfigManager, 'get_application_from_path') as get_application_from_path_mock, \
             patch.object(CommandProcessor, 'applications_validate') as applications_validate_mock:

            mock_cwd.return_value = 'test'
            get_application_from_path_mock.return_value = (self.application, None)

            application_validate_output = self.runner.invoke(applications_app, ['validate'])
            mock_cwd.assert_called_once()
            get_application_from_path_mock.assert_called_once_with('test')
            applications_validate_mock.assert_called_once_with(application=self.application)
            self.assertEqual(application_validate_output.exit_code, 0)
            self.assertIn('Application is valid.', application_validate_output.stdout)

    def test_application_list(self):
        with patch.object(CommandProcessor, "applications_list") as list_mock:
            list_mock.return_value = ['app1', 'app2']

            list_output = self.runner.invoke(applications_app, ['list'])
            self.assertEqual(list_output.exit_code, 0)
            list_mock.assert_called_once_with(remote=True, local=True)
            self.assertIn('app1', list_output.stdout)
            self.assertIn('app2', list_output.stdout)

            list_mock.reset_mock()
            list_output = self.runner.invoke(applications_app, ['list', '--remote'])
            self.assertEqual(list_output.exit_code, 0)
            list_mock.assert_called_once_with(remote=True, local=False)

            list_mock.reset_mock()
            list_output = self.runner.invoke(applications_app, ['list', '--local'])
            self.assertEqual(list_output.exit_code, 0)
            list_mock.assert_called_once_with(remote=False, local=True)

            list_mock.reset_mock()
            list_output = self.runner.invoke(applications_app, ['list', '--local', '--remote'])
            self.assertEqual(list_output.exit_code, 0)
            list_mock.assert_called_once_with(remote=True, local=True)

    def test_experiment_create(self):
        with patch("cli.command_list.Path.cwd") as mock_cwd, \
            patch.object(CommandProcessor, 'experiments_create') as experiment_create_mock, \
            patch.object(CommandProcessor, 'applications_validate') as app_validate_mock:
            mock_cwd.return_value = 'test'
            app_validate_mock.return_value = True, ''
            experiment_create_mock.return_value = True, ''

            experiment_create_output = self.runner.invoke(experiments_app, ['create', 'test_exp', 'app_name',
                                                                            'network_1'])
            self.assertEqual(experiment_create_output.exit_code, 0)
            self.assertIn('Experiment created successfully.', experiment_create_output.stdout)
            experiment_create_mock.assert_called_once_with(name='test_exp', application='app_name', network='network_1',
                                                           local=True, path='test')

            app_validate_mock.return_value = False, 'network.json is not a valid json.'
            experiment_create_mock.reset_mock()
            experiment_create_output = self.runner.invoke(experiments_app, ['create', 'test_exp', 'app_name',
                                                                            'network_1'])
            self.assertEqual(experiment_create_output.exit_code, 0)
            self.assertIn('The application app_name is not valid.', experiment_create_output.stdout)
            self.assertIn('network.json is not a valid json.', experiment_create_output.stdout)
            self.assertIn('You can use the application validate command to check the application.',
                          experiment_create_output.stdout)

            app_validate_mock.return_value = True, ''
            experiment_create_mock.return_value = False, 'lorem ipsum issue'
            experiment_create_mock.reset_mock()
            experiment_create_output = self.runner.invoke(experiments_app, ['create', 'test_exp', 'app_name',
                                                                            'network_1'])
            self.assertEqual(experiment_create_output.exit_code, 0)
            experiment_create_mock.assert_called_once_with(name='test_exp', application='app_name', network='network_1',
                                                           local=True, path='test')
            self.assertIn("Experiment could not be created. lorem ipsum issue", experiment_create_output.stdout)

    def test_experiment_validate(self):
        with patch("cli.command_list.Path.cwd") as mock_cwd,\
             patch.object(CommandProcessor, 'experiments_validate') as exp_validate_mock:

            mock_cwd.return_value = 'test'
            exp_validate_mock.return_value = True, 'ok'

            validate_output = self.runner.invoke(experiments_app, ['validate'])
            self.assertEqual(validate_output.exit_code, 0)
            exp_validate_mock.assert_called_once_with(path='test')
            self.assertIn("Experiment is valid.", validate_output.stdout)

            exp_validate_mock.reset_mock()
            exp_validate_mock.return_value = False, 'lorem ipsum error'
            validate_output = self.runner.invoke(experiments_app, ['validate'])
            self.assertEqual(validate_output.exit_code, 0)
            exp_validate_mock.assert_called_once_with(path='test')
            self.assertIn("Experiment is not valid. lorem ipsum error", validate_output.stdout)

    def test_experiment_run(self):
        with patch("cli.command_list.Path.cwd") as mock_cwd,\
             patch.object(CommandProcessor, 'experiments_run') as exp_run_mock:

            mock_cwd.return_value = 'test'
            exp_run_output = self.runner.invoke(experiments_app, ['run'])
            exp_run_mock.assert_called_once_with(path='test', block=False)
            self.assertEqual(exp_run_output.exit_code, 0)
            self.assertIn("Experiment has been created successfully.", exp_run_output.stdout)

            exp_run_mock.reset_mock()
            exp_run_output = self.runner.invoke(experiments_app, ['run', '--block'])
            exp_run_mock.assert_called_once_with(path='test', block=True)
            self.assertEqual(exp_run_output.exit_code, 0)
            self.assertIn("Experiment has run successfully.", exp_run_output.stdout)
