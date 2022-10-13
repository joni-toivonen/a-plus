from typing import Set
from django.test import TestCase
from rest_framework.test import APIClient

class UserProfileAPITest(TestCase):
    # use same setUp as for normal tests
    from ..tests import UserProfileTest # pylint: disable=import-outside-toplevel
    setUp = UserProfileTest.setUp

    def test_get_userlist(self):
        """
        Test if list of users are given correctly via REST.
        This does not need any authentication.
        """
        client = APIClient()
        client.force_authenticate(user=self.superuser)
        response = client.get('/api/v2/users/')

        model = {
            'count': 4,
            'next': None,
            'previous': None,
        }

        for key in model: # pylint: disable=consider-using-dict-items
            with self.subTest(key=key):
                self.assertIn(key, response.data)
                self.assertEqual(response.data[key], model[key])

        results = [
            {'id': 1,
             'url': 'http://testserver/api/v2/users/1/',
             'username': 'testUser',
             'student_id': '12345X',
             'email': 'test@aplus.com',
             'full_name': 'Superb Student',
             'is_external': False},
            {'id': 2,
             'url': 'http://testserver/api/v2/users/2/',
             'username': 'grader',
             'student_id': '67890Y',
             'email': 'grader@aplus.com',
             'full_name': 'Grumpy Grader',
             'is_external': False},
            {'id': 3,
             'url': 'http://testserver/api/v2/users/3/',
             'username': 'teacher',
             'student_id': None,
             'email': 'teacher@aplus.com',
             'full_name': 'Tedious Teacher',
             'is_external': True},
            {'id': 4,
             'url': 'http://testserver/api/v2/users/4/',
             'username': 'superuser',
             'student_id': None,
             'email': 'superuser@aplus.com',
             'full_name': 'Super User',
             'is_external': True},
        ]

        self.assertIn('results', response.data)
        r = response.data['results']
        self.assertEqual(len(r), len(results), "Wrong number of results")
        for user in results:
            with self.subTest(id=user['id'], user=user):
                u = next((u for u in r if u.get('id') == user['id']), None)
                self.assertNotEqual(u, None, "User with id %s not found from the result list" % (user['id'],))
                u = dict(u) # convert OrderedDict to dict for more clear error messages
                self.assertDictEqual(u, user)

        # check that there is no extra fields
        model['results'] = results
        self.assertCountEqual(response.data, model)

    def test_get_userdetail(self):
        client = APIClient()
        client.force_authenticate(user=self.superuser)
        response = client.get('/api/v2/users/1/')
        self.assertEqual(response.data, {
            'id': 1,
            'url': 'http://testserver/api/v2/users/1/',
            'username':'testUser',
            'student_id':'12345X',
            'is_external': False,
            'enrolled_courses': [],
            'full_name':'Superb Student',
            'first_name':'Superb',
            'last_name':'Student',
            'email':'test@aplus.com'})

    def test_field_values_filter(self):
        client = APIClient()
        client.force_authenticate(user=self.superuser)

        # Helper function that checks that the response contains the expected user ids (and no others)
        def check_response(url: str, expected_ids: Set[int]) -> None:
            response = client.get(url)
            ids = {u['id'] for u in response.data['results']}
            self.assertSetEqual(ids, expected_ids)

        # Check that all individual field filters work (id, student_id, email)
        check_response('/api/v2/users/?field=id&values=1,2,3,4', {1, 2, 3, 4})
        check_response('/api/v2/users/?field=student_id&values=12345X,67890Y', {1, 2})
        check_response('/api/v2/users/?field=email&values=teacher@aplus.com,superuser@aplus.com', {3, 4})

        # Check that partial matches are not returned
        check_response('/api/v2/users/?field=student_id&values=123,67890Y', {2})

        # Check that unmatched values don't cause errors
        check_response('/api/v2/users/?field=id&values=1,999', {1})

        # Check that an empty or missing values list returns an empty result
        check_response('/api/v2/users/?field=email', set())
