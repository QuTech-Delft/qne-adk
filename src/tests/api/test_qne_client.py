import unittest
from unittest.mock import call, patch

from adk.api.qne_client import QneFrontendClient


class TestQneFrontendClient(unittest.TestCase):
    def setUp(self):
        self.applications = {'next': None,
                             'previous': None,
                             'total_applications': 5,
                             'applications': [
                                 {
                                     'id': 90, 'url': 'http://127.0.0.1:8000/applications/90/',
                                     'name': 'killer_app', 'slug': 'killer_app', 'date': '2022-03-07',
                                     'description': 'add description', 'author': 'add your name',
                                     'email': 'add@your.email', 'is_draft': False, 'is_public': True,
                                     'is_disabled': False,
                                     'owner': {
                                         'id': 2, 'bio': '', 'avatar': None, 'slack_handle': '', 'nickname': 'user_2'
                                     },
                                     'number_of_successful_runs': 2
                                 },
                                 {
                                     'id': 6, 'url': 'http://127.0.0.1:8000/applications/6/',
                                     'name': 'QKD', 'slug': 'qkd', 'date': '2021-09-20',
                                     'description': 'QKD is a quantum key distribution scheme developed by '
                                                    'Charles Bennett and Gilles Brassard in 1984.',
                                     'author': 'Axel Dahlberg', 'email': 'a.dahlberg@tudelft.nl',
                                     'is_draft': False, 'is_public': True, 'is_disabled': False,
                                     'owner': None, 'number_of_successful_runs': 1
                                 },
                                 {
                                     'id': 78, 'url': 'http://127.0.0.1:8000/applications/78/',
                                     'name': 'Blind computation', 'slug': 'blind-computation', 'date': '2022-01-13',
                                     'description': 'This example demonstrates the quantum blind '
                                                    'computation application.',
                                     'author': 'Bart van der Vecht', 'email': 'B.vanderVecht@tudelft.nl',
                                     'is_draft': False, 'is_public': True, 'is_disabled': False, 'owner': None,
                                     'number_of_successful_runs': 1
                                 },
                                 {
                                     'id': 4, 'url': 'http://127.0.0.1:8000/applications/4/',
                                     'name': 'Distributed CNOT',
                                     'slug': 'distributed-cnot', 'date': '2021-09-20',
                                     'description': 'Performs a CNOT operation distributed over two nodes: Controller '
                                                    'and Target. Controller owns the control qubit and Target the '
                                                    'target qubit.', 'author': 'Axel Dahlberg',
                                     'email': 'a.dahlberg@tudelft.nl', 'is_draft': False, 'is_public': True,
                                     'is_disabled': False,
                                     'owner': {
                                         'id': 1, 'bio': 'This is my bio', 'avatar': None,
                                         'slack_handle': 'This is my slack_handle', 'nickname': 'user_1'
                                     },
                                     'number_of_successful_runs': 0
                                 },
                                 {
                                     'id': 92, 'url': 'http://127.0.0.1:8000/applications/92/', 'name': 'local_app',
                                     'slug': 'local_app', 'date': '2022-07-18', 'description': 'add description',
                                     'author': 'add your name', 'email': 'add@your.email', 'is_draft': False,
                                     'is_public': True, 'is_disabled': False,
                                     'owner': {
                                         'id': 2, 'bio': '', 'avatar': None, 'slack_handle': '', 'nickname': 'user_2'
                                     },
                                     'number_of_successful_runs': 0
                                 }
                             ]
                             }
        self.applications_limit_is_1 = [
            {
                'next': 'http://127.0.0.1:8000/applications/90/?limit=1&offset=1',
                'previous': None,
                'total_applications': 5,
                'applications': [self.applications['applications'][0]]
            },
            {
                'next': 'http://127.0.0.1:8000/applications/?limit=1&offset=2',
                'previous': 'http://127.0.0.1:8000/applications/?limit=1',
                'total_applications': 5,
                'applications': [self.applications['applications'][1]]
            },
            {
                'next': 'http://127.0.0.1:8000/applications/?limit=1&offset=3',
                'previous': 'http://127.0.0.1:8000/applications/?limit=1&offset=1',
                'total_applications': 5,
                'applications': [self.applications['applications'][2]]
            },
            {
                'next': 'http://127.0.0.1:8000/applications/?limit=1&offset=4',
                'previous': 'http://127.0.0.1:8000/applications/?limit=1&offset=2',
                'total_applications': 5,
                'applications': [self.applications['applications'][3]]
            },
            {
                'next': None,
                'previous': 'http://127.0.0.1:8000/applications/?limit=1&offset=3',
                'total_applications': 5,
                'applications': [self.applications['applications'][4]]
            }
        ]
        self.applications_unpaged = [
        {
            "id": 1,
            "url": "https://api.quantum-network.com/applications/1/",
            "name": "State Teleportation",
            "slug": "state-teleportation",
            "date": "2021-11-17",
            "description": "Quantum teleportation is a process in which quantum information (e.g. the exact state of an atom or photon) can be transmitted (exactly, in principle) from one location to another, with the help of classical communication and previously shared quantum entanglement between the sending and receiving location.",
            "author": "Axel Dahlberg",
            "email": "a.dahlberg@tudelft.nl",
            "is_draft": False,
            "is_public": True,
            "is_disabled": False
        },
        {
            "id": 7,
            "url": "https://api.quantum-network.com/applications/7/",
            "name": "Distributed CNOT",
            "slug": "distributed-cnot",
            "date": "2021-11-17",
            "description": "Performs a CNOT operation distributed over two nodes: Controller and Target. Controller owns the control qubit and Target the target qubit.",
            "author": "Axel Dahlberg",
            "email": "a.dahlberg@tudelft.nl",
            "is_draft": False,
            "is_public": True,
            "is_disabled": False
        },
        {
            "id": 5,
            "url": "https://api.quantum-network.com/applications/5/",
            "name": "QKD",
            "slug": "qkd",
            "date": "2021-11-17",
            "description": "QKD is a quantum key distribution scheme developed by Charles Bennett and Gilles Brassard in 1984.",
            "author": "Axel Dahlberg",
            "email": "a.dahlberg@tudelft.nl",
            "is_draft": False,
            "is_public": True,
            "is_disabled": False
        }
        ]

        with patch('adk.api.remote_api.AuthManager') as auth_manager, \
             patch('adk.api.qne_client.QneFrontendClient'):

            self.qne_frontend_client = QneFrontendClient(auth_manager)


class TestApplications(TestQneFrontendClient):
    def test_application_unpaged_list(self):
        # test the backwards compatibility with the previous version of the applications endpoint
        with patch.object(QneFrontendClient, "_action") as action_mock:

            action_mock.return_value = self.applications_unpaged
            application_list = self.qne_frontend_client.list_applications()
            self.assertEqual(action_mock.call_count, 1)
            self.assertListEqual(application_list, self.applications_unpaged)

    def test_application_paged_list_at_once(self):
        with patch.object(QneFrontendClient, "_action") as action_mock:

            action_mock.return_value = self.applications
            application_list = self.qne_frontend_client.list_applications()
            self.assertEqual(action_mock.call_count, 1)
            self.assertListEqual(application_list, self.applications["applications"])

    def test_application_paged_list_limited(self):
        with patch.object(QneFrontendClient, "_action") as action_mock:

            action_mock.side_effect = self.applications_limit_is_1
            application_list = self.qne_frontend_client.list_applications()
            self.assertEqual(action_mock.call_count, 5)

            action_calls = [call('listApplications'),
                            call('listApplications', limit='1', offset='1'),
                            call('listApplications', limit='1', offset='2'),
                            call('listApplications', limit='1', offset='3'),
                            call('listApplications', limit='1', offset='4')]

            action_mock.assert_has_calls(action_calls)
            self.assertListEqual(application_list, self.applications["applications"])
