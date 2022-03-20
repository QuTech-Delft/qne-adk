from pathlib import Path
from unittest.mock import call, patch, MagicMock
import unittest

from adk.managers.resource_manager import ResourceManager


class TestResourceManager(unittest.TestCase):
    def setUp(self) -> None:
        self.application_data = {
            "application": {
                "name": "test_app",
                "description": "test_app description",
                "author": "my name",
                "email": "me@my.email",
                "multi_round": False
            },
            "remote": {
                "slug": "remote_app"
            }
        }
        self.path = Path('dummy')

    def test_prepare_resources(self):
        tar = MagicMock()
        with patch("adk.managers.resource_manager.tarfile.open", tar) as mock_tarfile_open:
            resource_manager = ResourceManager()

            files_list = ["app_role1.py", "app_role2.py", "lib.py"]
            file_path, file_name = resource_manager.prepare_resources(application_data=self.application_data,
                                                                      application_path=self.path,
                                                                      files_list=files_list)

            mock_tarfile_open.assert_called_once_with(self.path / "src" / "remote_app.tar.gz", "w:gz")
            tarfile = tar().__enter__()
            tar_files_calls = [call(name=self.path / "src" / "app_role1.py", arcname="app_role1.py", recursive=False),
                               call(name=self.path / "src" / "app_role2.py", arcname="app_role2.py", recursive=False),
                               call(name=self.path / "src" / "lib.py", arcname="lib.py", recursive=False)]

            tarfile.add.assert_has_calls(tar_files_calls, any_order=True)
            self.assertEqual(tarfile.add.call_count, 3)
            self.assertEqual(file_path, str(self.path / "src" / "remote_app.tar.gz"))
            self.assertEqual(file_name, "remote_app.tar.gz")
