from unittest.mock import patch
import unittest
from typer.testing import CliRunner

from cli.command_list import app
from cli.command_processor import CommandProcessor

class TestCommandList(unittest.TestCase):

    def setUp(self):
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
