# This file includes all unittests


import os
import unittest
from app import app, db, login

TEST_DB = 'test.db'


class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'postgres://jhivjrfwkjzlff:9c37a83349353453a04fb5ae5102d86d9b84ae8fea94b46c24e01c3d4a4a0da2@ec2-54-81-37-115.compute-1.amazonaws.com:5432/d3lm6g7l0bs75i'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    # executed after each test
    def tearDown(self):
        pass

    # Helper Methods

    def register(self, email, password, confirm):
        return self.app.post(
            '/',
            data=dict(email=email, password=password, confirm_pswd=confirm),
            follow_redirects=True
        )

    def login(self, email, password):
        return self.app.post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.app.get(
            '/logout',
            follow_redirects=True
        )

    # Tests

    # Registration

    def test_registration_page(self):
        """
        test 1
        :return:
        """
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_valid_email_registration(self):
        """
        test 2
        :return:
        """
        response = self.register('patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertIn(b'login', response.data)

    def test_invalid_email_registration(self):
        """
        test 3
        """
        response = self.register('mail', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertIn(b'Please enter a valid mail', response.data)

    def test_not_matching_password_registration(self):
        """
        test 4
        :return:
        """
        response = self.register('mail@test.com', '11111111', '22222222')
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertIn(b'password must match', response.data)

    def test_short_password_registration(self):
        """
        test 5
        :return:
        """
        """
        Password must be at least 6 characters, this function test that.
        """
        response = self.register('mail@test.com', '12345', '12345')
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertIn(b'Password must be at least 6 characters', response.data)

    def test_existing_email_registration(self):
        """
        test 6
        Email should not already exist in the database, this function tests that.
        """
        response = self.register('test@test.com', '11111111', '11111111')
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertIn(b'Email already exists', response.data)

    # Login
    def test_login_valid(self):
        """
        test 7
        testing login function with valid credentials
        """

        response = self.login('test@test.com', '11111111')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'welcome', response.data)

    def test_login_invalid(self):
        """
        test 8
        testing login function with invalid credentials
        """

        response = self.login('invalid@test.com', '11111111')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email or password incorrect', response.data)

    def test_login_empty_field(self):
        """
        test 9
        testing login function with invalid credentials
        """

        response = self.login('', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'fill', response.data)

    def test_login_user_session(self):
        """
        test 10
        testing to make sure that the username used in login in the same as the current session
        """

        response = self.login('test@test.com', '11111111')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test', response.data)

    # admin login

    def test_login_admin(self):
        """
        test 11
        testing login function for admin
        """

        response = self.login('admin@admin.com', '11111111')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Portal', response.data)

    # User dashboard

    def test_pre_quiz(self):
        """
        test 12
        this test makes sure that user dashboard loads
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/pre_quiz')
        self.assertEqual(response.status_code, 200)

    def test_api_fetch(self):
        """
        test 13
        testing to make sure website could get any data from question API
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/pre_quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'set-union', response.data)
        self.assertIn(b'inverse-function', response.data)
        self.assertIn(b'reflexive-closure', response.data)

    def test_posted_material(self):
        """
        test 14
        testing to make sure user has access to the posted content
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/pre_quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'this is a test content', response.data)

    def test_posted_announcements(self):
        """
        test 15
        testing to make sure user can see the posted questions
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/pre_quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test-announcement', response.data)

    def test_posted_question(self):
        """
        test 16
        testing to make sure user has access to the posted content
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/pre_quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test-question-topic', response.data)

    # progress

    def test_progress_page(self):
        """
        test 17
        testing to see the progress page keeps record of users scores.
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/progress')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'50.0', response.data)

    # Inbox
    def test_user_inbox(self):
        """
        test 18
        this test makes sure user gets the messages
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/inbox')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'admin', response.data)
        self.assertIn(b'test msg', response.data)

    # user logout
    def test_user_logout(self):
        """
        test 19
        this test makes sure user log out function works properly
        """
        self.login('test@test.com', '11111111')
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)


if __name__ == "__main__":
    unittest.main()
