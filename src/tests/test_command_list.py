import unittest
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

from adk.exceptions import ApplicationNotFound, ExperimentDirectoryNotValid
from adk.command_list import app, applications_app, experiments_app, retrieve_application_name_and_path, \
                             retrieve_experiment_name_and_path
from adk.command_processor import CommandProcessor
from adk.managers.config_manager import ConfigManager


class TestCommandList(unittest.TestCase):
    def setUp(self):
        self.application = 'test_application'
        self.experiment_name = 'test_experiment'
        self.roles = ["role1, role2"]
        self.path = Path("dummy")
        self.runner = CliRunner()
        self.app_dict_1 = {'remote': [], 'local': []}
        self.app_dict_2 = {'remote': [{'name': 'foo'}, {'name': 'bar'}], 'local': []}
        self.app_dict_3 = {'remote': [], 'local': [{'name': 'foo'}]}
        self.app_dict_4 = {'remote': [{'name': 'bar'}], 'local': [{'name': 'foo'}]}
        self.app_dict_5 = {'local': []}
        self.app_dict_6 = {'local': [{'name': 'foo'}, {'name': 'bar'}]}
        self.app_dict_7 = {'remote': []}
        self.app_dict_8 = {'remote': [{'name': 'foo'}, {'name': 'bar'}]}

    def test_login(self):
        with patch.object(CommandProcessor, "login") as login_mock:
            login_output = self.runner.invoke(app, ['login', 'test_host'], input="test_username\ntest_password")
            self.assertIn('Command is not yet implemented', login_output.stdout)
            login_mock.reset_mock()
            login_output = self.runner.invoke(app, ['login'], input="test_username\ntest_password")
            self.assertIn('Command is not yet implemented', login_output.stdout)
            login_mock.reset_mock()
            login_output = self.runner.invoke(app, ['login'], input=" \n ")
            self.assertIn('Command is not yet implemented', login_output.stdout)

    def test_logout(self):
        with patch.object(CommandProcessor, "logout") as logout_mock:
            logout_output = self.runner.invoke(app, ['logout'])
            self.assertIn('Command is not yet implemented', logout_output.stdout)

            logout_mock.reset_mock()
            logout_output = self.runner.invoke(app, ['logout', 'qutech.com'])
            self.assertIn('Command is not yet implemented', logout_output.stdout)

    def test_applications_create_succes(self):
        with patch("adk.command_list.Path.cwd", return_value=self.path) as mock_cwd, \
             patch("adk.command_list.validate_path_name") as mock_validate_path_name, \
             patch.object(CommandProcessor, 'applications_create') as application_create_mock:

            application_create_output = self.runner.invoke(applications_app,
                                                           ['create', 'test_application', 'role1', 'role2'])
            mock_cwd.assert_called_once()
            self.assertEqual(mock_validate_path_name.call_count, 3)
            application_create_mock.assert_called_once_with(application_name=self.application, roles=('role1', 'role2'),
                                                            application_path=self.path / self.application)
            self.assertEqual(application_create_output.exit_code, 0)
            self.assertIn(f"Application 'test_application' created successfully in directory '{self.path}'",
                          application_create_output.stdout)

    def test_applications_create_exceptions(self):
        with patch("adk.command_list.Path.cwd", return_value='test') as mock_cwd:

            # Raise NotEnoughRoles when only one or less roles are given
            application_create_output = self.runner.invoke(applications_app, ['create', 'test_application', 'role1'])
            self.assertIn('The number of roles must be higher than one', application_create_output.stdout)

            # Raise RolesNotUnique when roles are duplicated
            application_create_output = self.runner.invoke(applications_app, ['create', 'test_application', 'role1',
                                                                              'role2', 'role3', 'role2'])
            self.assertIn('The role names must be unique', application_create_output.stdout)

            # Raise InvalidApplicationName when the application name is invalid contains ['/', '\\', '*', ':', '?',
            # '"', '<', '>', '|']
            application_create_output = self.runner.invoke(applications_app, ['create', 'test_application/2',
                                                                              'role1', 'role2'])
            self.assertIn('Error: Application name can\'t contain any of the following characters: [\'/\', \'\\\', '
                          '\'*\', \':\', \'?\', \'"\', \'<\', \'>\', \'|\']', application_create_output.stdout)

            application_create_output = self.runner.invoke(applications_app, ['create', 'test*application',
                                                                              'role1', 'role2'])
            self.assertIn('Error: Application name can\'t contain any of the following characters: [\'/\', \'\\\', '
                          '\'*\', \':\', \'?\', \'"\', \'<\', \'>\', \'|\']', application_create_output.stdout)

            application_create_output = self.runner.invoke(applications_app, ['create', 'test\\application',
                                                                              'role1', 'role2'])
            self.assertIn('Error: Application name can\'t contain any of the following characters: [\'/\', \'\\\', '
                          '\'*\', \':\', \'?\', \'"\', \'<\', \'>\', \'|\']', application_create_output.stdout)

            # Raise InvalidRoleName when one of the roles contains ['/', '\\', '*', ':', '?', '"', '<', '>', '|']
            application_create_output = self.runner.invoke(applications_app, ['create', 'test_application',
                                                                              'role/1', 'role2'])
            self.assertIn('Error: Role name can\'t contain any of the following characters: [\'/\', \'\\\', '
                          '\'*\', \':\', \'?\', \'"\', \'<\', \'>\', \'|\']', application_create_output.stdout)

            application_create_output = self.runner.invoke(applications_app, ['create', 'test_application',
                                                                              'role1', 'role/2'])
            self.assertIn('Error: Role name can\'t contain any of the following characters: [\'/\', \'\\\', '
                          '\'*\', \':\', \'?\', \'"\', \'<\', \'>\', \'|\']', application_create_output.stdout)

            application_create_output = self.runner.invoke(applications_app, ['create', 'test_application',
                                                                              'rol/e1', 'role2'])
            self.assertIn('Error: Role name can\'t contain any of the following characters: [\'/\', \'\\\', '
                          '\'*\', \':\', \'?\', \'"\', \'<\', \'>\', \'|\']', application_create_output.stdout)

            # Raise Other Exception
            mock_cwd.side_effect = Exception("Test")
            application_create_output = self.runner.invoke(applications_app,
                                                           ['create', 'test_application', 'role1', 'role2'])
            self.assertIn("Unhandled exception: Exception('Test')", application_create_output.stdout)

    def test_application_delete_no_experiment_dir(self):
        with patch.object(CommandProcessor, 'applications_delete', return_value=True) as applications_delete_mock, \
             patch("adk.command_list.retrieve_application_name_and_path") as retrieve_appname_and_path_mock:

            retrieve_appname_and_path_mock.return_value = self.path, self.application
            application_delete_output = self.runner.invoke(applications_app, ['delete'])
            self.assertEqual(application_delete_output.exit_code, 0)
            retrieve_appname_and_path_mock.assert_called_once()
            self.assertIn("Application deleted successfully",
                          application_delete_output.stdout)

            retrieve_appname_and_path_mock.reset_mock()
            applications_delete_mock.return_value = False
            application_delete_output = self.runner.invoke(applications_app, ['delete'])
            self.assertEqual(application_delete_output.exit_code, 0)
            retrieve_appname_and_path_mock.assert_called_once()
            self.assertIn("Application files deleted",
                          application_delete_output.stdout)

    def test_application_delete_with_application_dir(self):
        with patch.object(CommandProcessor, 'applications_delete', return_value=False) as applications_delete_mock, \
             patch("adk.command_list.retrieve_application_name_and_path") as retrieve_appname_and_path_mock:

            retrieve_appname_and_path_mock.return_value = self.path, self.application
            application_delete_output = self.runner.invoke(applications_app, ['delete', 'app_dir'])
            applications_delete_mock.assert_called_once()
            self.assertEqual(application_delete_output.exit_code, 0)
            retrieve_appname_and_path_mock.assert_called_once()
            self.assertIn("Application files deleted, directory not empty",
                          application_delete_output.stdout)

    def test_experiment_delete_no_experiment_dir(self):
        with patch.object(CommandProcessor, 'experiments_delete', return_value=True) as experiments_delete_mock, \
             patch("adk.command_list.retrieve_experiment_name_and_path") as retrieve_expname_and_path_mock:

            retrieve_expname_and_path_mock.return_value = self.path, self.experiment_name
            experiment_delete_output = self.runner.invoke(experiments_app, ['delete'])
            self.assertEqual(experiment_delete_output.exit_code, 0)
            retrieve_expname_and_path_mock.assert_called_once()
            self.assertIn("Experiment deleted successfully",
                          experiment_delete_output.stdout)

            retrieve_expname_and_path_mock.reset_mock()
            experiments_delete_mock.return_value = False
            experiment_delete_output = self.runner.invoke(experiments_app, ['delete'])
            self.assertEqual(experiment_delete_output.exit_code, 0)
            retrieve_expname_and_path_mock.assert_called_once()
            self.assertIn("Experiment files deleted",
                          experiment_delete_output.stdout)

    def test_experiment_delete_with_experiment_dir(self):
        with patch.object(CommandProcessor, 'experiments_delete', return_value=False) as experiments_delete_mock, \
             patch("adk.command_list.retrieve_experiment_name_and_path") as retrieve_expname_and_path_mock:

            retrieve_expname_and_path_mock.return_value = self.path, self.experiment_name
            experiment_delete_output = self.runner.invoke(experiments_app, ['delete', 'exp_dir'])
            experiments_delete_mock.assert_called_once_with(experiment_name=self.experiment_name,
                                                            experiment_path=self.path)
            self.assertEqual(experiment_delete_output.exit_code, 0)
            retrieve_expname_and_path_mock.assert_called_once()
            self.assertIn("Experiment files deleted, directory not empty",
                          experiment_delete_output.stdout)


    def test_retrieve_application_name_and_path(self):
        with patch("adk.command_list.validate_path_name") as validate_path_name_mock, \
             patch("adk.command_list.Path.cwd") as cwd_mock, \
             patch.object(ConfigManager, "get_application_path") as get_application_path_mock, \
             patch.object(ConfigManager, "get_application_from_path") as get_application_from_path_mock, \
             patch("adk.command_list.Path.is_dir") as is_dir_mock:

            get_application_path_mock.return_value = self.path
            # application name not None
            retrieve_application_name_and_path(application_name=self.application)
            is_dir_mock.assert_called_once()
            validate_path_name_mock.assert_called_once_with("Application", self.application)
            get_application_path_mock.assert_called_once_with(self.application)

            # application name is None
            is_dir_mock.reset_mock()
            cwd_mock.return_value = self.path
            get_application_from_path_mock.return_value = self.application, None
            retrieve_application_name_and_path(application_name=None)
            is_dir_mock.assert_called_once()
            cwd_mock.assert_called_once()
            get_application_from_path_mock.assert_called_once_with(self.path)

            # Raise ApplicationNotFound when application_path is None
            validate_path_name_mock.reset_mock()
            get_application_path_mock.reset_mock()
            get_application_path_mock.return_value = None
            self.assertRaises(ApplicationNotFound, retrieve_application_name_and_path, self.application)
            validate_path_name_mock.assert_called_once_with("Application", self.application)
            get_application_path_mock.assert_called_once_with(self.application)

            # Raise Raise ApplicationNotFound when application directory does not exist
            validate_path_name_mock.reset_mock()
            get_application_path_mock.reset_mock()
            is_dir_mock.reset_mock()
            is_dir_mock.return_value = False
            get_application_path_mock.return_value = self.path
            self.assertRaises(ApplicationNotFound, retrieve_application_name_and_path, self.application)
            is_dir_mock.assert_called_once()
            validate_path_name_mock.assert_called_once_with("Application", self.application)
            get_application_path_mock.assert_called_once_with(self.application)

    def test_applications_validate_all_ok(self):
        with patch.object(CommandProcessor, 'applications_validate') as applications_validate_mock, \
             patch("adk.command_list.retrieve_application_name_and_path") as retrieve_appname_and_path_mock:

            retrieve_appname_and_path_mock.return_value = self.path, self.application

            # When application is valid (no items in error, warning and info)
            applications_validate_mock.return_value = {"error": {}, "warning": {}, "info": {}}

            application_validate_output = self.runner.invoke(applications_app, ['validate'])
            retrieve_appname_and_path_mock.assert_called_once()
            applications_validate_mock.assert_called_once_with(application_name=self.application,
                                                               application_path=self.path)
            self.assertIn(f"Application '{self.application}' is valid", application_validate_output.stdout)

            # When application is valid with item in in 'info'
            retrieve_appname_and_path_mock.reset_mock()
            applications_validate_mock.reset_mock()
            applications_validate_mock.return_value = {"error": {}, "warning": {}, "info": {"info"}}

            application_validate_output = self.runner.invoke(applications_app, ['validate'])
            applications_validate_mock.assert_called_once_with(application_name=self.application,
                                                               application_path=self.path)
            retrieve_appname_and_path_mock.assert_called_once()
            self.assertIn(f"Application '{self.application}' is valid", application_validate_output.stdout)

            # When application name is given as input
            retrieve_appname_and_path_mock.reset_mock()
            applications_validate_mock.reset_mock()

            application_validate_output = self.runner.invoke(applications_app, ['validate', self.application])
            applications_validate_mock.assert_called_once_with(application_name=self.application,
                                                               application_path=self.path)
            retrieve_appname_and_path_mock.assert_called_once()
            self.assertIn(f"Application '{self.application}' is valid", application_validate_output.stdout)

    def test_applications_validate_invalid(self):
        with patch.object(CommandProcessor, 'applications_validate') as applications_validate_mock, \
             patch("adk.command_list.retrieve_application_name_and_path") as retrieve_appname_and_path_mock:

            retrieve_appname_and_path_mock.return_value = self.path, self.application
            applications_validate_mock.return_value = {"error": {"error"}, "warning": {"warning"}, "info": {"info"}}

            application_validate_output = self.runner.invoke(applications_app, ['validate'])
            applications_validate_mock.assert_called_once_with(application_name=self.application,
                                                               application_path=self.path)
            retrieve_appname_and_path_mock.assert_called_once()
            self.assertIn(f"Application '{self.application}' is invalid", application_validate_output.stdout)

            # When only 'error' has items
            retrieve_appname_and_path_mock.reset_mock()
            applications_validate_mock.reset_mock()
            applications_validate_mock.return_value = {"error": {"error"}, "warning": {}, "info": {}}

            application_validate_output = self.runner.invoke(applications_app, ['validate'])
            applications_validate_mock.assert_called_once_with(application_name=self.application,
                                                               application_path=self.path)
            retrieve_appname_and_path_mock.assert_called_once()
            self.assertIn(f"Application '{self.application}' is invalid", application_validate_output.stdout)

    def test_experiment_create(self):
        with patch("adk.command_list.Path.cwd") as mock_cwd, \
             patch.object(CommandProcessor, 'experiments_create') as experiment_create_mock, \
             patch.object(CommandProcessor, 'applications_validate') as app_validate_mock, \
             patch("adk.command_list.validate_path_name") as mock_validate_path, \
             patch("adk.command_list.retrieve_application_name_and_path") as retrieve_application_name_and_path_mock:

            retrieve_application_name_and_path_mock.return_value = self.path, "app_name"
            mock_cwd.return_value = 'test'
            app_validate_mock.return_value = {"error": [], "warning": [], "info": []}
            experiment_create_mock.return_value = True, ''

            experiment_create_output = self.runner.invoke(experiments_app, ['create', 'test_exp', 'app_name',
                                                                            'network_1'])
            mock_validate_path.assert_called_once_with('Experiment', 'test_exp')
            retrieve_application_name_and_path_mock.assert_called_once_with(application_name="app_name")
            self.assertEqual(experiment_create_output.exit_code, 0)
            self.assertIn("Experiment 'test_exp' created successfully in directory 'test'",
                          experiment_create_output.stdout)
            experiment_create_mock.assert_called_once_with(experiment_name='test_exp', application_name='app_name',
                                                           network_name='network_1', local=True, path='test')

    def test_retrieve_experiment_name_and_path(self):
        with patch("adk.command_list.Path.cwd") as cwd_mock, \
             patch("adk.command_list.validate_path_name") as validate_path_name_mock, \
             patch("adk.command_list.Path.is_dir") as is_dir_mock:

            # if experiment name is not None
            cwd_mock.return_value = self.path
            retrieve_experiment_name_and_path(self.experiment_name)
            validate_path_name_mock.assert_called_once_with("Experiment", self.experiment_name)
            is_dir_mock.assert_called_once()

            # if experiment name is None
            is_dir_mock.reset_mock()
            retrieve_experiment_name_and_path(None)
            is_dir_mock.assert_called_once()

            # raise ExperimentDirectoryNotValid
            is_dir_mock.reset_mock()
            validate_path_name_mock.reset_mock()
            is_dir_mock.return_value = False
            self.assertRaises(ExperimentDirectoryNotValid, retrieve_experiment_name_and_path, self.experiment_name)
            validate_path_name_mock.assert_called_once_with("Experiment", self.experiment_name)
            is_dir_mock.assert_called_once()


    def test_experiment_validate(self):
        with patch("adk.command_list.Path.cwd") as mock_cwd, \
             patch.object(CommandProcessor, 'experiments_validate') as experiments_validate_mock, \
             patch("adk.command_list.show_validation_messages") as show_validation_messages_mock:

            mock_cwd.return_value = self.path
            experiments_validate_mock.return_value = {"error": {"error"}, "warning": {"warning"}, "info": {"info"}}

            experiment_validate_output = self.runner.invoke(experiments_app, ['validate'])
            mock_cwd.assert_called_once()
            experiments_validate_mock.assert_called_once_with(path=self.path)
            show_validation_messages_mock.assert_called_once()
            self.assertIn("Experiment is invalid", experiment_validate_output.stdout)

            # When only 'error' has items
            experiments_validate_mock.reset_mock()
            mock_cwd.reset_mock()
            show_validation_messages_mock.reset_mock()
            mock_cwd.return_value = self.path
            experiments_validate_mock.return_value = {"error": {"error"}, "warning": {}, "info": {}}

            experiment_validate_output = self.runner.invoke(experiments_app, ['validate'])
            mock_cwd.assert_called_once()
            experiments_validate_mock.assert_called_once_with(path=self.path)
            show_validation_messages_mock.assert_called_once()
            self.assertIn("Experiment is invalid", experiment_validate_output.stdout)

            # When application is valid (no items in error, warning and info)
            experiments_validate_mock.reset_mock()
            mock_cwd.reset_mock()
            show_validation_messages_mock.reset_mock()
            mock_cwd.return_value = self.path
            experiments_validate_mock.return_value = {"error": {}, "warning": {}, "info": {}}

            experiment_validate_output = self.runner.invoke(experiments_app, ['validate'])
            mock_cwd.assert_called_once()
            experiments_validate_mock.assert_called_once_with(path=self.path)
            show_validation_messages_mock.assert_called_once()
            self.assertIn("Experiment is valid", experiment_validate_output.stdout)

            # When application is valid with item in in 'info'
            experiments_validate_mock.reset_mock()
            mock_cwd.reset_mock()
            show_validation_messages_mock.reset_mock()
            mock_cwd.return_value = self.path
            experiments_validate_mock.return_value = {"error": {}, "warning": {}, "info": {"info"}}

            experiment_validate_output = self.runner.invoke(experiments_app, ['validate'])
            mock_cwd.assert_called_once()
            experiments_validate_mock.assert_called_once_with(path=self.path)
            show_validation_messages_mock.assert_called_once()
            self.assertIn("Experiment is valid", experiment_validate_output.stdout)

    def test_experiment_run(self):
        with patch.object(CommandProcessor, 'experiments_validate') as exp_validate_mock, \
             patch.object(CommandProcessor, 'experiments_run') as exp_run_mock, \
             patch("adk.command_list.retrieve_experiment_name_and_path") as retrieve_expname_and_path_mock:

            retrieve_expname_and_path_mock.return_value = self.path, None
            exp_validate_mock.return_value = {"error": [], "warning": [], "info": []}
            exp_run_output = self.runner.invoke(experiments_app, ['run'])
            exp_validate_mock.assert_called_once_with(experiment_path=self.path)
            retrieve_expname_and_path_mock.assert_called_once()
            exp_run_mock.assert_called_once_with(experiment_path=self.path, block=False)
            self.assertEqual(exp_run_output.exit_code, 0)

            retrieve_expname_and_path_mock.reset_mock()
            exp_run_mock.reset_mock()
            exp_run_output = self.runner.invoke(experiments_app, ['run', '--block'])
            exp_run_mock.assert_called_once_with(experiment_path=self.path, block=True)
            retrieve_expname_and_path_mock.assert_called_once()
            self.assertEqual(exp_run_output.exit_code, 0)

    def test_experiment_results(self):
        with patch.object(CommandProcessor, 'experiments_results') as exp_results_mock, \
             patch("adk.command_list.retrieve_experiment_name_and_path") as retrieve_expname_and_path_mock:

            retrieve_expname_and_path_mock.return_value = self.path, None
            exp_results_output = self.runner.invoke(experiments_app, ['results'])

            exp_results_mock.assert_called_once_with(all_results=False, experiment_path=self.path)
            self.assertEqual(exp_results_output.exit_code, 0)
            retrieve_expname_and_path_mock.assert_called_once()

            retrieve_expname_and_path_mock.reset_mock()
            exp_results_mock.reset_mock()
            exp_results_mock.return_value = ['r1', 'r2']
            exp_results_output = self.runner.invoke(experiments_app, ['results', '--all', '--show'])
            exp_results_mock.assert_called_once_with(all_results=True, experiment_path=self.path)
            retrieve_expname_and_path_mock.assert_called_once()
            self.assertEqual(exp_results_output.exit_code, 0)
            self.assertIn("['r1', 'r2']", exp_results_output.stdout)

            retrieve_expname_and_path_mock.reset_mock()
            exp_results_mock.reset_mock()
            exp_results_output = self.runner.invoke(experiments_app, ['results', '--all'])
            exp_results_mock.assert_called_once_with(all_results=True, experiment_path=self.path)
            retrieve_expname_and_path_mock.assert_called_once()
            self.assertEqual(exp_results_output.exit_code, 0)
            self.assertIn("Results are stored at location 'dummy/results/processed.json'", exp_results_output.stdout)

    def test_applications_list(self):
        with patch.object(CommandProcessor, "applications_list") as list_applications_mock:
            list_applications_mock.side_effect = [self.app_dict_1, self.app_dict_2,
                                                  self.app_dict_3, self.app_dict_4]

            result_both = self.runner.invoke(applications_app, ['list'])
            self.assertEqual(result_both.exit_code, 0)
            self.assertIn('There are no local applications available', result_both.stdout)
            self.assertNotIn('There are no remote applications available', result_both.stdout)

            result_both = self.runner.invoke(applications_app, ['list'])
            self.assertEqual(result_both.exit_code, 0)
            self.assertIn('There are no local applications available', result_both.stdout)
            self.assertNotIn('2 remote application(s)', result_both.stdout)
            self.assertNotIn('foo', result_both.stdout)
            self.assertNotIn('bar', result_both.stdout)

            result_both = self.runner.invoke(applications_app, ['list'])
            self.assertEqual(result_both.exit_code, 0)
            self.assertIn('1 local application(s)', result_both.stdout)
            self.assertIn('foo', result_both.stdout)
            self.assertNotIn('There are no remote applications available', result_both.stdout)

            result_both = self.runner.invoke(applications_app, ['list'])
            self.assertEqual(result_both.exit_code, 0)
            self.assertIn('1 local application(s)', result_both.stdout)
            self.assertNotIn('1 remote application(s)', result_both.stdout)
            self.assertIn('foo', result_both.stdout)
            self.assertNotIn('bar', result_both.stdout)

    def test_applications_list_local(self):
        with patch.object(CommandProcessor, "applications_list") as list_applications_mock:
            list_applications_mock.side_effect = [self.app_dict_5, self.app_dict_6]

            result_local = self.runner.invoke(applications_app, ['list', '--local'])
            self.assertEqual(result_local.exit_code, 0)
            self.assertIn('There are no local applications available', result_local.stdout)
            self.assertNotIn('remote', result_local.stdout)

            result_local = self.runner.invoke(applications_app, ['list', '--local'])
            self.assertEqual(result_local.exit_code, 0)
            self.assertIn('2 local application(s)', result_local.stdout)
            self.assertIn('foo', result_local.stdout)
            self.assertIn('bar', result_local.stdout)
            self.assertNotIn('remote', result_local.stdout)

    def test_applications_list_remote(self):
        with patch.object(CommandProcessor, "applications_list") as list_applications_mock:
            list_applications_mock.side_effect = [self.app_dict_7, self.app_dict_8]

            result_remote = self.runner.invoke(applications_app, ['list', '--remote'])
            self.assertEqual(result_remote.exit_code, 2)
            self.assertNotIn('There are no remote applications available', result_remote.stdout)
            self.assertNotIn('local', result_remote.stdout)

            result_remote = self.runner.invoke(applications_app, ['list', '--remote'])
            self.assertEqual(result_remote.exit_code, 2)
            self.assertNotIn('2 remote application(s)', result_remote.stdout)
            self.assertNotIn('foo', result_remote.stdout)
            self.assertNotIn('bar', result_remote.stdout)
            self.assertNotIn('local', result_remote.stdout)
