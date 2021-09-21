import unittest

from pathlib import Path
from cli.managers.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.path = Path('dummy')
        self.config_manager = ConfigManager(config_dir=self.path)
        self.application = 'test_application'

    def test_add_application(self):
        self.config_manager.add_application(application=self.application, path=self.path)

    def test_application_exists(self):
        self.assertTrue(self.config_manager.application_exists(application=self.application))

    def test_get_application_from_path(self):
        self.config_manager.get_application_from_path(self.path)
