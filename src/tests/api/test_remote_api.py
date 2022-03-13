import unittest

from pathlib import Path
from unittest.mock import call, patch, MagicMock, mock_open

from adk.api.remote_api import RemoteApi
from adk.exceptions import ApiClientError, ApplicationNotFound


class TestRemoteApi(unittest.TestCase):
    def setUp(self):
        self.app_path = Path("path/to/application")
        self.base_uri = 'base_uri.com'
        self.host = 'http://unittest_server/'
        self.username = 'username'
        self.password = 'password'
        self.token = 'token'
        self.application_data = {
            "application": {
                "name": "test_app",
                "description": "test_app description",
                "author": "my name",
                "email": "me@my.email",
                "multi_round": False
            },
            "remote": {}
        }
        self.network_config = {
            "networks": [
                "randstad",
                "europe",
                "the-netherlands"
            ],
            "roles": [
                "sender",
                "receiver"
            ]
        }
        self.application_config = [
            {
                "title": "Qubit state of Sender",
                "slug": "qubit_state_sender",
                "description": "...",
                "values": [
                    {
                        "name": "phi",
                        "default_value": 0.0,
                        "minimum_value": -1.0,
                        "maximum_value": 1.0,
                        "unit": "radials",
                        "scale_value": 1
                    },
                    {
                        "name": "theta",
                        "default_value": 0.0,
                        "minimum_value": 0.0,
                        "maximum_value": 1.0,
                        "unit": "radials",
                        "scale_value": 1
                    }
                ],
                "input_type": "qubit",
                "roles": [
                    "sender"
                ]
            }
        ]
        self.result = {
            "round_result_view": [],
            "cumulative_result_view": [],
            "final_result_view": []
        }
        self.application_data_uploaded = {
            'application': {'name': 'test_app',
                            'description': 'test_app description',
                            'author': 'my name',
                            'email': 'me@my.email',
                            'multi_round': False
                            },
            'remote': {'application': f'{self.host}application/42',
                       'application_id': 42,
                       'slug': 'application_slug',
                       'app_version': {
                           'enabled': False,
                           'version': 1,
                           'app_version': 'http://unittest_server/app_version/42',
                           'app_config': 'http://unittest_server/app_config/42',
                           'app_result': 'http://unittest_server/app_result/42',
                           'app_source': 'http://unittest_server/app_source/42'
                       }
                       }
        }
        self.mock_tarball = 'fake_file'
        self.application = {
            "id": 42,
            "url": f"{self.host}application/42",
            "slug": "application_slug",
            "name": self.application_data["application"]["name"],
            "description": self.application_data["application"]["description"],
            "author": self.application_data["application"]["author"],
            "email": self.application_data["application"]["email"]
        }

        self.app_version = {
            "id": 42,
            "url": f"{self.host}app_version/42",
            "application": self.application["url"],
            "version": 1,
            "is_disabled": True
        }
        self.app_config = {
            "id": 42,
            "url": f"{self.host}app_config/42",
            "app_version": self.app_version["url"],
            "network": self.network_config,
            "application": self.application_config,
            "multi_round": self.application_data["application"]["multi_round"]
        }
        self.app_result = {
            "id": 42,
            "url": f"{self.host}app_result/42",
            "app_version": self.app_version["url"],
            "round_result_view": self.result["round_result_view"],
            "cumulative_result_view": self.result["cumulative_result_view"],
            "final_result_view": self.result["final_result_view"]
        }
        self.app_source_files = {
            "id": 42,
            "url": f"{self.host}app_source/42",
            "source_files": ('tarball', self.mock_tarball),
            "app_version": (None, self.app_version['url']),
            "output_parser": (None, '{}')
        }
        with patch('adk.api.remote_api.AuthManager'), \
             patch('adk.api.remote_api.QneFrontendClient'), \
             patch('adk.api.remote_api.ResourceManager'):

            self.config_manager = MagicMock(config_dir=Path("path/to/application"))
            self.remote_api = RemoteApi(config_manager=self.config_manager)


class TestRemoteApiAuthentication(TestRemoteApi):
    def test_login(self):
        self.remote_api.login(self.username, self.password, self.host)
        self.remote_api.auth_manager.login.assert_called_once_with(self.username, self.password, self.host)

    def test_logout(self):
        self.remote_api._RemoteApi__qne_client.is_logged_in.return_value = False
        ret_val = self.remote_api.logout(self.host)
        self.assertFalse(ret_val)
        self.remote_api._RemoteApi__qne_client.is_logged_in.return_value = True
        ret_val = self.remote_api.logout(self.host)
        self.remote_api.auth_manager.logout.assert_called_once_with(self.host)
        self.assertTrue(ret_val)

    def test_logout_with_host(self):
        pass


class TestRemoteApiApplication(TestRemoteApi):
    def test_list_application(self):
        pass

    def test_get_application_config(self):
        pass

    def test_clone_application_successful(self):
        with patch('adk.api.remote_api.Path.mkdir') as mock_mkdir, \
             patch("adk.api.remote_api.utils.write_json_file") as write_json_file_mock, \
             patch.object(RemoteApi, "_RemoteApi__get_application_by_slug") as get_application_by_slug_mock:

            self.remote_api._RemoteApi__qne_client.app_config_application.return_value = {"network" : "the_net",
                                                                                          "application": "the_app"}
            self.remote_api._RemoteApi__qne_client.app_result_application.return_value = self.result
            self.remote_api._RemoteApi__qne_client.app_source_application.return_value = "app_source"
            get_application_by_slug_mock.return_value = self.application
            self.remote_api.clone_application("Old_App", "New_App", self.app_path)

            self.assertEqual(mock_mkdir.call_count, 2)
            get_application_by_slug_mock.assert_called_once_with("Old_App")
            self.remote_api._RemoteApi__qne_client.app_config_application.assert_called_once_with(
                self.application["url"])
            self.remote_api._RemoteApi__qne_client.app_result_application.assert_called_once_with(
                self.application["url"])
            self.remote_api._RemoteApi__qne_client.app_source_application.assert_called_once_with(
                self.application["url"])

            self.remote_api._RemoteApi__resource_manager.generate_resources.assert_called_once_with(
                self.remote_api._RemoteApi__qne_client, "app_source", self.app_path)

            expected_manifest = {
                "application": {
                    "name": "new_app",
                    "description": "add description",
                    "author": "add your name",
                    "email": "add@your.email",
                    "multi_round": False
                },
                "remote": {}
            }
            write_json_files_calls = [call(self.app_path / 'config' / 'network.json', "the_net"),
                                      call(self.app_path / 'config' / 'application.json', "the_app"),
                                      call(self.app_path / 'config' / 'result.json', self.result),
                                      call(self.app_path / 'manifest.json', expected_manifest)]

            write_json_file_mock.assert_has_calls(write_json_files_calls)
            self.remote_api._RemoteApi__config_manager.add_application.assert_called_once_with(
                application_name="new_app", application_path=self.app_path)

    def test_clone_application_fails(self):
        with patch('adk.api.remote_api.Path.mkdir') as mock_mkdir, \
             patch("adk.api.remote_api.utils.write_json_file") as write_json_file_mock, \
             patch.object(RemoteApi, "_RemoteApi__get_application_by_slug") as get_application_by_slug_mock:

            get_application_by_slug_mock.return_value = None

            self.assertRaises(ApplicationNotFound, self.remote_api.clone_application,
                              "Old_App", "New_App", self.app_path)

    def test_upload_application_new_app_successful(self):
        application_data = self.application_data
        application_config = {"application": self.application_config, "network": self.network_config}

        self.remote_api._RemoteApi__resource_manager.prepare_resources.return_value = self.app_path, 'tarball'
        self.remote_api._RemoteApi__resource_manager.delete_resources.return_value = None
        self.remote_api._RemoteApi__qne_client.partial_update_application.return_value = None
        self.remote_api._RemoteApi__qne_client.create_application.return_value = self.application
        self.remote_api._RemoteApi__qne_client.create_app_version.return_value = self.app_version
        self.remote_api._RemoteApi__qne_client.create_app_config.return_value = self.app_config
        self.remote_api._RemoteApi__qne_client.create_app_result.return_value = self.app_result
        self.remote_api._RemoteApi__qne_client.create_app_source.return_value = self.app_source_files
        with patch('adk.api.remote_api.open', mock_open(read_data=self.mock_tarball)):
            app_data_actual = self.remote_api.upload_application(self.app_path,
                                                                 application_data,
                                                                 application_config,
                                                                 self.result)

        self.assertDictEqual(app_data_actual, self.application_data_uploaded)

    def test_upload_application_new_app_creation_fails(self):
        application_data = self.application_data
        application_config = {"application": self.application_config, "network": self.network_config}
        application_result = self.result

        self.remote_api._RemoteApi__qne_client.create_application.side_effect = ApiClientError("Error: creating app")
        self.assertRaises(ApiClientError, self.remote_api.upload_application, self.app_path,
                          application_data,
                          application_config,
                          application_result)

    def test_upload_application_new_appversion_creation_fails(self):
        application_data = self.application_data
        application_config = {"application": self.application_config, "network": self.network_config}
        application_result = self.result
        application = {
            "id": 42,
            "url": f"{self.host}application/42",
            "slug": "application_slug",
            "name": application_data["application"]["name"],
            "description": application_data["application"]["description"],
            "author": application_data["application"]["author"],
            "email": application_data["application"]["email"]
        }

        self.remote_api._RemoteApi__qne_client.create_application.return_value = application
        self.remote_api._RemoteApi__qne_client.create_app_version.side_effect =\
            ApiClientError("Error: creating appversion")
        self.assertRaises(ApiClientError, self.remote_api.upload_application, self.app_path,
                          application_data,
                          application_config,
                          application_result)

    def test_upload_application_appversion_exists_but_not_complete_succeeds(self):
        application_data = self.application_data_uploaded
        # appversion exists, but not yet completed
        application_data["remote"]["app_version"]["app_config"] = ''
        application_data["remote"]["app_version"]["app_result"] = ''
        application_data["remote"]["app_version"]["app_source"] = ''

        application_config = {"application": self.application_config, "network": self.network_config}
        application_result = self.result

        self.remote_api._RemoteApi__resource_manager.prepare_resources.return_value = self.app_path, 'tarball'
        self.remote_api._RemoteApi__resource_manager.delete_resources.return_value = None
        self.remote_api._RemoteApi__qne_client.partial_update_application.return_value = None
        self.remote_api._RemoteApi__qne_client.list_applications.return_value = [self.application]
        self.remote_api._RemoteApi__qne_client.create_app_version.side_effect = \
            ApiClientError("Error: You already have one incomplete/draft AppVersion for this Application. "
                           "Please complete it before adding a new AppVersion")
        self.remote_api._RemoteApi__qne_client.create_app_config.return_value = self.app_config
        self.remote_api._RemoteApi__qne_client.create_app_result.return_value = self.app_result
        self.remote_api._RemoteApi__qne_client.create_app_source.return_value = self.app_source_files
        with patch('adk.api.remote_api.open', mock_open(read_data=self.mock_tarball)):
            app_data_actual = self.remote_api.upload_application(self.app_path,
                                                                 application_data,
                                                                 application_config,
                                                                 application_result)

        self.assertDictEqual(app_data_actual, self.application_data_uploaded)

    def test_upload_application_appversion_exists_but_not_complete_succeeds_after_failure(self):
        application_data = self.application_data_uploaded
        # appversion exists, delete some references to make it not complete
        application_data["remote"]["app_version"]["app_config"] = ''
        application_data["remote"]["app_version"]["app_result"] = ''
        application_data["remote"]["app_version"]["app_source"] = ''

        application_config = {"application": self.application_config, "network": self.network_config}
        application_result = self.result

        self.remote_api._RemoteApi__resource_manager.prepare_resources.return_value = self.app_path, 'tarball'
        self.remote_api._RemoteApi__resource_manager.delete_resources.return_value = None
        self.remote_api._RemoteApi__qne_client.partial_update_application.return_value = None
        self.remote_api._RemoteApi__qne_client.list_applications.return_value = [self.application]
        self.remote_api._RemoteApi__qne_client.create_app_version.side_effect = \
            ApiClientError("Error: You already have one incomplete/draft AppVersion for this Application. "
                           "Please complete it before adding a new AppVersion")
        self.remote_api._RemoteApi__qne_client.create_app_config.return_value = self.app_config
        self.remote_api._RemoteApi__qne_client.create_app_result.side_effect = \
            ApiClientError("Error: appresult creation failed")

        self.assertRaises(ApiClientError, self.remote_api.upload_application, self.app_path,
                          application_data,
                          application_config,
                          application_result)

        self.remote_api._RemoteApi__qne_client.create_app_result.side_effect = None
        self.remote_api._RemoteApi__qne_client.create_app_result.return_value = self.app_result
        self.remote_api._RemoteApi__qne_client.create_app_source.return_value = self.app_source_files
        with patch('adk.api.remote_api.open', mock_open(read_data=self.mock_tarball)):
            app_data_actual = self.remote_api.upload_application(self.app_path,
                                                                 application_data,
                                                                 application_config,
                                                                 application_result)

        self.assertDictEqual(app_data_actual, self.application_data_uploaded)

    def test_upload_existing_application_appversion_new_version(self):
        application_data = self.application_data_uploaded
        application_config = {"application": self.application_config, "network": self.network_config}
        self.next_app_version = {
            "id": 43,
            "url": f"{self.host}app_version/43",
            "application": self.application["url"],
            "version": 2,
            "is_disabled": True
        }
        self.next_app_config = {
            "id": 43,
            "url": f"{self.host}app_config/43",
            "app_version": self.app_version["url"],
            "network": self.network_config,
            "application": self.application_config,
            "multi_round": self.application_data["application"]["multi_round"]
        }
        self.next_app_result = {
            "id": 43,
            "url": f"{self.host}app_result/43",
            "app_version": self.app_version["url"],
            "round_result_view": self.result["round_result_view"],
            "cumulative_result_view": self.result["cumulative_result_view"],
            "final_result_view": self.result["final_result_view"]
        }
        self.next_app_source_files = {
            "id": 43,
            "url": f"{self.host}app_source/43",
            "source_files": ('tarball', self.mock_tarball),
            "app_version": (None, self.app_version['url']),
            "output_parser": (None, '{}')
        }

        self.remote_api._RemoteApi__resource_manager.prepare_resources.return_value = self.app_path, 'tarball'
        self.remote_api._RemoteApi__resource_manager.delete_resources.return_value = None
        self.remote_api._RemoteApi__qne_client.partial_update_application.return_value = None
        self.remote_api._RemoteApi__qne_client.list_applications.return_value = [self.application]
        self.remote_api._RemoteApi__qne_client.create_app_version.return_value = self.next_app_version
        self.remote_api._RemoteApi__qne_client.create_app_config.return_value = self.next_app_config
        self.remote_api._RemoteApi__qne_client.create_app_result.return_value = self.next_app_result
        self.remote_api._RemoteApi__qne_client.create_app_source.return_value = self.next_app_source_files
        with patch('adk.api.remote_api.open', mock_open(read_data=self.mock_tarball)):
            app_data_actual = self.remote_api.upload_application(self.app_path,
                                                                 application_data,
                                                                 application_config,
                                                                 self.result)

        self.assertEqual(app_data_actual["remote"]["application"], f'{self.host}application/42')
        self.assertEqual(app_data_actual["remote"]["application_id"], 42)
        self.assertEqual(app_data_actual["remote"]["app_version"]["version"], 2)
        self.assertEqual(app_data_actual["remote"]["app_version"]["enabled"], False)
        self.assertEqual(app_data_actual["remote"]["app_version"]["app_version"], f'{self.host}app_version/43')
        self.assertEqual(app_data_actual["remote"]["app_version"]["app_config"], f'{self.host}app_config/43')
        self.assertEqual(app_data_actual["remote"]["app_version"]["app_result"], f'{self.host}app_result/43')
        self.assertEqual(app_data_actual["remote"]["app_version"]["app_source"], f'{self.host}app_source/43')

    def test_publish_application_successful(self):
        application_data = self.application_data_uploaded
        application_data_published = application_data
        application_data_published["remote"]["app_version"]["enabled"] = True
        application = {
            "id": application_data["remote"]["application_id"],
            "url": application_data["remote"]["application"],
            "slug": application_data["remote"]["slug"],
            "name": application_data["application"]["name"],
            "description": application_data["application"]["description"],
            "author": application_data["application"]["author"],
            "email": application_data["application"]["email"]
        }
        app_version = {
            "id": 42,
            "url": f"{self.host}app_version/42",
            "application": application["url"],
            'app_config': f"{self.host}app_config/42",
            'app_result': f"{self.host}app_result/42",
            'app_source': f"{self.host}app_source/42",
            "version": 1,
            "is_disabled": False
        }

        self.remote_api._RemoteApi__qne_client.list_applications.return_value = [application]
        self.remote_api._RemoteApi__qne_client.partial_update_app_version.return_value = app_version

        application_published = self.remote_api.publish_application(application_data)
        self.assertTrue(application_published)
        self.assertDictEqual(application_data, application_data_published)

    def test_publish_not_uploaded_application_fails(self):
        application_data = self.application_data
        application_published = self.remote_api.publish_application(application_data)
        self.assertFalse(application_published)

    def test_publish_not_existing_application_fails(self):
        application_data = self.application_data_uploaded
        self.remote_api._RemoteApi__qne_client.list_applications.return_value = []
        application_published = self.remote_api.publish_application(application_data)
        self.assertFalse(application_published)


class TestRemoteApiExperiment(TestRemoteApi):
    def test_create_experiment(self):
        pass
