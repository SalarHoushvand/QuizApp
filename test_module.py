from app import app
import unittest
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq


class FlaskTestCase(unittest.TestCase):

    # Ensure that flask was setup correctly
    def test_index(self):
        """
        This test makes sure that our main path has a content and loads properly.
        """
        tester = app.test_client(self)
        response = tester.get('/', content_type='text/html; charset=utf-8')
        self.assertEqual(response.status_code, 200)

    # Ensure that the register page loads correctly
    def test_register_page_loads(self):
        """
        This test makes sure that the main path is registration page, has a content of HTML .
        """
        tester = app.test_client(self)
        response = tester.get('/', content_type='text/html; charset=utf-8')
        self.assertTrue(b'register' in response.data)

    # Ensure that the login works properly with correct data
    def test_user_login_correct_data(self):
        """
        This test makes sure that we can login with correct credentials and redirect to the dashboard.
        """

        my_url = "http://127.0.0.1:5000/login"
        uClient = uReq(my_url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")

        token = page_soup.find('input', {'name': 'csrf_token'})['value']

        tester = app.test_client(self)
        response = tester.post('/login',
                               data=dict(email='test@test.com', password='11111111'),
                               follow_redirects=True)
        # searching for welcome in the response which appears in dashboard
        self.assertIn(b'quiz', response.data)

    # Ensure that the login works properly with correct data
    def test_user_login_wrong_credentials(self):
        """
        This test makes sure that we can't login with wrong credentials.
        """
        tester = app.test_client(self)

        # with email field left empty
        response = tester.post('/login',
                               data=dict(email='something', password='1234567'),
                               follow_redirects=True)
        # searching for 'fill' in the page wich is part of please fill out the forms
        self.assertIn(b'incorrect', response.data)

    # Ensure that the login works properly with correct data
    def test_user_login_empty_field(self):
        """
        This test makes sure that we can't login with empty field in email and password. and program asks to
         fill out the forms.
        """
        tester = app.test_client(self)

        # with email field left empty
        response = tester.post('/login',
                               data=dict(email='', password='1234567'),
                               follow_redirects=True)
        # searching for 'fill' in the page wich is part of please fill out the forms
        self.assertIn(b'fill', response.data)

        # with password field left empty
        response = tester.post('/login',
                               data=dict(email='test@gmail.com', password=''))
        # searching for 'fill' in the page wich is part of please fill out the forms
        self.assertIn(b'fill', response.data)

    # Ensure that the user can register with proper inputs
    def test_user_registration_correct(self):
        """
        This test tests the registration of new user.
        This is for testing correct inputs
        Email should be in proper email format and between 6 to 50 characters (defined in wtforms_fields.py)
        Password should be at least 6 characters (defined in wtforms_fields.py)
        """
        my_url = "http://127.0.0.1:5000/login"
        uClient = uReq(my_url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")

        token = page_soup.find('input', {'name': 'csrf_token'})['value']

        tester = app.test_client(self)
        response = tester.post('/',
                               data=dict(email='testuse9rssasdqwe9@email.com', password='11111111',
                                         confirm_pswd='11111111', csrf_token=token),
                               follow_redirects=True)
        # searching for welcome in the response which appears in dashboard
        self.assertIn(b'login', response.data)

    # Ensure that the user can register with proper inputs
    def test_user_registration_wrong(self):
        """
        This test tests the registration of new user.
        This is for testing incorrect inputs
        Email should be in proper email format and between 6 to 50 characters (defined in wtforms_fields.py)
        Password should be at least 6 characters (defined in wtforms_fields.py)
        """
        tester = app.test_client(self)
        response = tester.post('/',
                               data=dict(email='testuser99@email.com', password='11111111',
                                         confirm_pswd='111111'),
                               follow_redirects=True)
        # searching for welcome in the response which appears in dashboard
        self.assertIn(b'match', response.data)

    # Ensure that we can generate a quiz from dashboard
    def test_api_fetch(self):
        """
        This test makes sure that system fetches different topics from api.
        This test should return the non-empty list or true for the fethced topic lists
        """

        tester = app.test_client(self)
        response = tester.get('http://127.0.0.1:5000/pre_quiz')
        print(response.data)
        self.assertTrue(b'set-union' in response.data)

    # # Ensure that we can generate a quiz from dashboard
    # def test_quiz_generator(self):
    #     """
    #     This test makes sure that we can login with correct credentials and redirect to the dashboard.
    #
    #     """
    #     tester = app.test_client(self)
    #     response = tester.post('/pre_quiz',
    #                            data=dict(topic='set-union', questionNumber='2'),
    #                            follow_redirects=True)
    #     # searching for welcome in the response which appears in dashboard
    #     self.assertIn(b'next', response.data)
    #
    # # Ensure that the logout function works
    # def test_logout(self):
    #     """
    #     This test makes sure that logout function works properly.
    #     """
    #     tester = app.test_client(self)
    #     response = tester.get('/logout', content_type='text/html; charset=utf-8', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'login', response.data)


if __name__ == '__main__':
    app.secret_key = 'SECRET'
    unittest.main()

# import requests
#
#
# def test_main_page():
#     """
#     Unit test for the main page, we test the followings:
#     request returns 200 (OK) code.
#     It has content
#     Content type is html
#     :return:
#     """
#
#     # variables for storing number of test cases
#     test_cases_for_status_code = 0
#     test_cases_for_content = 0
#
#     print('starting test for main page (path "/") ...')
#     for i in range(100):
#         # making a call to the path
#         res = requests.get('http://127.0.0.1:5000/')
#         # checking the status code
#         if res.status_code is not 200:
#             print('Status code not 200')
#         else:
#             test_cases_for_status_code = test_cases_for_content + 1
#         # checking the content and content type
#         if str(res.headers.get('Content-Type')) != 'text/html; charset=utf-8':
#             print('Error in content')
#             print(str(res.headers.get('Content-Type')))
#         else:
#             test_cases_for_content = test_cases_for_content + 1
#
#     # printing results
#     print(f'{test_cases_for_status_code} requests returned code 200 .')
#     print(f'{test_cases_for_content} responses had a content type of html.')
#     print('test completed for main page\n')
#
#
# def test_login_page():
#     """
#     Unit test for the login page, we test the followings:
#     request returns 200 (OK) code.
#     It has content
#     Content type is html
#     :return:
#     """
#
#     # variables for storing number of test cases
#     test_cases_for_status_code = 0
#     test_cases_for_content = 0
#
#     print('starting test for login page (path "/login") ...')
#     for i in range(100):
#         # making a call to the path
#         res = requests.get('http://127.0.0.1:5000/login')
#         # checking the status code
#         if res.status_code is not 200:
#             print('Status code not 200')
#         else:
#             test_cases_for_status_code = test_cases_for_content + 1
#         # checking the content and content type
#         if str(res.headers.get('Content-Type')) != 'text/html; charset=utf-8':
#             print('Error in content')
#             print(str(res.headers.get('Content-Type')))
#         else:
#             test_cases_for_content = test_cases_for_content + 1
#
#     # printing results
#     print(f'{test_cases_for_status_code} requests returned code 200 .')
#     print(f'{test_cases_for_content} responses had a content type of html.')
#     print('test completed for main page\n')
#
# def test_pre_quiz_page():
#     """
#     Unit test for the pre quiz page, we test the followings:
#     request returns 200 (OK) code.
#     It has content
#     Content type is html
#     :return:
#     """
#
#     # variables for storing number of test cases
#     test_cases_for_status_code = 0
#     test_cases_for_content = 0
#
#     print('starting test for pre quiz page (path "/pre-quiz") ...')
#     for i in range(100):
#         # making a call to the path
#         res = requests.get('http://127.0.0.1:5000/pre_quiz')
#         # checking the status code
#         if res.status_code is not 200:
#             print('Status code not 200')
#         else:
#             test_cases_for_status_code = test_cases_for_content + 1
#         # checking the content and content type
#         if str(res.headers.get('Content-Type')) != 'text/html; charset=utf-8':
#             print('Error in content')
#             print(str(res.headers.get('Content-Type')))
#         else:
#             test_cases_for_content = test_cases_for_content + 1
#
#     # printing results
#     print(f'{test_cases_for_status_code} requests returned code 200 .')
#     print(f'{test_cases_for_content} responses had a content type of html.')
#     print('test completed for pre quiz\n')
#
#
# test_main_page()
# test_login_page()
# test_pre_quiz_page()
