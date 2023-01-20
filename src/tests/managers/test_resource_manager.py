from pathlib import Path
from unittest.mock import call, patch, MagicMock
import unittest

from adk.exceptions import InvalidPath
from adk.managers.resource_manager import ResourceManager


class TestResourceManager(unittest.TestCase):
    def setUp(self) -> None:
        self.app_source = {
            'id': 126,
            'url': 'http://localhost/app-sources/126/',
            'app_version': 'http://localhost/app-versions/134/',
            'source_files': 'http://localhost/media/app-source/remote_app.tar.gz',
            'output_parser': '{}',
            'all_results_needed': False
        }

        self.application_data = {
            "application": {
                "name": "test_app",
                "description": "test_app description",
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

    def test_generate_resources_success(self):
        tar = MagicMock()
        qne_client = MagicMock()
        with patch("adk.managers.resource_manager.Path.exists") as mock_path_exists, \
             patch("adk.managers.resource_manager.Path.is_file") as mock_tarfile_is_file, \
             patch("adk.managers.resource_manager.tarfile.open", tar) as mock_tarfile_open:

            tarfile = tar().__enter__()
            alice = MagicMock()
            alice.name = 'alice.py'
            bob = MagicMock()
            bob.name = 'bob.py'
            tarfile.getmembers.return_value = [alice, bob]

            mock_path_exists.side_effect = [True, True]
            mock_tarfile_is_file.return_value = False
            resource_manager = ResourceManager()
            app_source = self.app_source

            resource_manager.generate_resources(qne_client=qne_client,
                                                app_source=app_source,
                                                application_path=self.path)

            mock_tarfile_open.assert_called_with(self.path / "src" / "remote_app.tar.gz", "r:gz")

            tarfile.extractall.assert_called_with(str(self.path / "src"))
            self.assertEqual(tarfile.extractall.call_count, 1)

    def test_generate_resources_path_created(self):
        tar = MagicMock()
        qne_client = MagicMock()
        with patch("adk.managers.resource_manager.Path.exists") as mock_path_exists, \
             patch("adk.managers.resource_manager.Path.is_file") as mock_tarfile_is_file, \
             patch("adk.managers.resource_manager.Path.unlink") as mock_path_unlink, \
             patch("adk.managers.resource_manager.Path.mkdir") as mock_path_mkdir, \
             patch("adk.managers.resource_manager.tarfile.open", tar) as mock_tarfile_open:

            tarfile = tar().__enter__()
            alice = MagicMock()
            alice.name = 'alice.py'
            bob = MagicMock()
            bob.name = 'bob.py'
            tarfile.getmembers.return_value = [alice, bob]

            mock_path_exists.side_effect = [False, False]
            mock_tarfile_is_file.return_value = True
            resource_manager = ResourceManager()
            app_source = self.app_source

            resource_manager.generate_resources(qne_client=qne_client,
                                                app_source=app_source,
                                                application_path=self.path)

            mock_tarfile_open.assert_called_with(self.path / "src" / "remote_app.tar.gz", "r:gz")
            mock_path_mkdir.assert_called_with(parents=True, exist_ok=True)
            mock_path_unlink.assert_called_once()
            qne_client.download_source_files.assert_called_once_with(
                'http://localhost/media/app-source/remote_app.tar.gz', self.path / "src", "remote_app.tar.gz")
            tarfile.extractall.assert_called_with(str(self.path / "src"))
            self.assertEqual(tarfile.extractall.call_count, 1)

    def test_generate_resources_fails(self):
        tar = MagicMock()
        qne_client = MagicMock()
        with patch("adk.managers.resource_manager.Path.exists") as mock_path_exists, \
             patch("adk.managers.resource_manager.Path.is_file") as mock_path_is_file, \
             patch("adk.managers.resource_manager.tarfile.open", tar) as mock_tarfile_open:

            tarfile = tar().__enter__()
            alice = MagicMock()
            alice.name = 'alice.py'
            bob = MagicMock()
            bob.name = '../bob.py'
            tarfile.getmembers.return_value = [alice, bob]

            mock_path_exists.side_effect = [True, True]
            mock_path_is_file.return_value = False
            resource_manager = ResourceManager()
            app_source = {'id': 126,
                          'url': 'http://localhost/app-sources/126/',
                          'app_version': 'http://localhost/app-versions/134/',
                          'source_files': 'http://localhost/media/app-source/remote_app.tar.gz',
                          'output_parser': '{}',
                          'all_results_needed': False
                          }

            self.assertRaises(InvalidPath, resource_manager.generate_resources,
                              qne_client=qne_client,
                              app_source=app_source,
                              application_path=self.path)

            mock_tarfile_open.assert_called_with(self.path / "src" / "remote_app.tar.gz", "r:gz")
            self.assertEqual(tarfile.extractall.call_count, 0)

    def test_delete_resources(self):
        with patch("adk.managers.resource_manager.Path.is_file") as mock_path_is_file, \
             patch("adk.managers.resource_manager.Path.unlink") as mock_path_unlink:

            mock_path_is_file.return_value = True
            resource_manager = ResourceManager()

            resource_manager.delete_resources(application_data=self.application_data,
                                              application_path=self.path)

            mock_path_is_file.assert_called_once()
            mock_path_unlink.assert_called_once()
