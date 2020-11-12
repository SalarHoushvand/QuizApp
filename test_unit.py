# This file contains all unittests


import os
import unittest
from app import app, db, login
import string
import random
import models as mds

from flask import request

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

    def random_string(self, length):
        """
        random string generator to test inputs
        :param length: length of the string
        :return: string
        """
        return ''.join(random.choices(string.ascii_uppercase +
                                      string.digits, k=length))

    # Tests

    # Registration

    def test_registration_page(self):
        """
        test TC001
        """
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_valid_email_registration(self):
        """
        test TC002
        :return:
        """
        response = self.register('patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)

    def test_invalid_email_registration(self):
        """
        test TC003
        """
        response = self.register('mail', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter a valid mail', response.data)

    def test_not_matching_password_registration(self):
        """
        test TC004
        """
        response = self.register('mail@test.com', '11111111', '22222222')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'password must match', response.data)

    def test_short_password_registration(self):
        """
        test TC005
        """

        response = self.register('mail@test.com', '12345', '12345')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password must be between 6 and 50 characters', response.data)

    def test_existing_email_registration(self):
        """
        test TC006
        """
        response = self.register('test@test.com', '11111111', '11111111')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email already exists', response.data)

    def test_password_boundaries(self):
        """
        test TC007
        testing boundary range for password
        min 6
        max 50
        """
        short_password_list = ['1', '12', '123', '1234', '12345']
        minimum_password = '123456'
        min_plus_one_password = '123456'

        # generating string with length of 50
        max_password = self.random_string(50)
        max_plus_one_password = self.random_string(51)
        max_minus_one_password = self.random_string(49)

        # testing short passwords
        for password in short_password_list:
            response_short_pass = self.register('passwordtest@gmail.com', password, password)
            self.assertIn(b'Password must be between 6 and 50 characters', response_short_pass.data)

        # testing minimum password
        response_min_pass = self.register('passwordtest@gmail.com', minimum_password, minimum_password)
        self.assertIn(b'login', response_min_pass.data)

        # testing minimum+1 password
        response_min_plus_one_pass = self.register('passwordtest@gmail.com', min_plus_one_password,
                                                   min_plus_one_password)
        self.assertIn(b'login', response_min_plus_one_pass.data)

        # testing max-1 password
        response_max_minus_one_password = self.register('passwordtest@gmail.com', max_minus_one_password,
                                                        max_minus_one_password)
        self.assertIn(b'login', response_max_minus_one_password.data)

        # testing max password
        response_max_password = self.register('passwordtest@gmail.com', max_password,
                                              max_password)
        self.assertIn(b'login', response_max_password.data)

        # testing max+1 password
        response_max_plus_one_password = self.register('passwordtest@gmail.com', max_plus_one_password,
                                                       max_plus_one_password)
        self.assertIn(b'Password must be between 6 and 50 characters', response_max_plus_one_password.data)

    def test_email_boundaries(self):
        """
        test TC008
        testing boundary range for email
        min 6
        max 50
        """
        short_mail_list = [
            's@e.c',
            'te@.d',
            'e@e.com'
        ]
        min_mail = 's@gm.com'
        min_plus_one_mail = 'ss@gm.com'
        max_minus_one_mail = self.random_string(39) + '@email.com'
        max_mail = self.random_string(40) + '@email.com'
        max_plus_one_mail = self.random_string(41) + '@email.com'

        # testing short emails
        for mail in short_mail_list:
            response_short_pass = self.register(mail, '1234567', '1234567')
            self.assertIn(b'Please enter a valid mail', response_short_pass.data)

        # testing minimum email length
        response_min_mail = self.register(min_mail, '1234567', '1234567')
        self.assertIn(b'login', response_min_mail.data)

        # testing minimum + 1 email length
        response_min_plus_one_mail = self.register(min_plus_one_mail, '1234567', '1234567')
        self.assertIn(b'login', response_min_plus_one_mail.data)

        # testing max-1 email length
        response_max_minus_one_mail = self.register(max_minus_one_mail, '1234567', '1234567')
        self.assertIn(b'login', response_max_minus_one_mail.data)

        # testing max+1 mail email length
        response_max_mail = self.register(max_mail, '1234567', '1234567')
        self.assertIn(b'login', response_max_mail.data)

        # testing max_mail email length
        response_max_plus_one_mail = self.register(max_plus_one_mail, '1234567', '1234567')
        self.assertIn(b'Please enter a valid mail', response_max_plus_one_mail.data)

    # Login
    def test_login_valid(self):
        """
        test TC009
        testing login function with valid credentials
        """

        response = self.login('test@test.com', '11111111')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'welcome', response.data)

    def test_login_invalid(self):
        """
        test TC010
        testing login function with invalid credentials
        """

        response = self.login('invalid@test.com', '11111111')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email or password incorrect', response.data)

    def test_login_empty_field(self):
        """
        test TC011
        testing login function with invalid credentials
        """

        response = self.login('', '')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'fill', response.data)

    def test_login_user_session(self):
        """
        test TC012
        testing to make sure that the username used in login in the same as the current session
        """

        response = self.login('test@test.com', '11111111')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test', response.data)

    # User dashboard

    def test_pre_quiz(self):
        """
        test TC013
        this test makes sure that user dashboard loads
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/pre_quiz')
        self.assertEqual(response.status_code, 200)

    def test_api_fetch(self):
        """
        test TC014
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
        test TC015
        testing to make sure user has access to the posted content
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/pre_quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'this is a test content', response.data)

    def test_posted_announcements(self):
        """
        test TC016
        testing to make sure user can see the posted questions
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/pre_quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test-announcement', response.data)

    def test_posted_question(self):
        """
        test TC017
        testing to make sure user has access to the posted content
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/pre_quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test-question-topic', response.data)

    # progress

    def test_progress_page(self):
        """
        test TC018
        testing to see the progress page keeps record of users scores.
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/progress')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'50.0', response.data)

    # Inbox
    def test_user_inbox(self):
        """
        test TC019
        this test makes sure user gets the messages
        """
        self.login('test@test.com', '11111111')
        response = self.app.get('/inbox')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'admin', response.data)
        self.assertIn(b'test msg', response.data)

    # questions
    def test_question_number_generated(self):
        """
            test TC020
            this test makes sure that number of requested question are same as generated questions
            """
        self.login('test@test.com', '11111111')
        response = self.app.post(
            '/pre_quiz',
            data=dict(topic='set-union', questionNumber='2', btn='quiz'),
            follow_redirects=True)
        self.assertIn(b'2 / 2', response.data)
        self.assertIn(b'1 / 2', response.data)

        response_2 = self.app.post(
            '/pre_quiz',
            data=dict(topic='floor-function', questionNumber='10', btn='quiz'),
            follow_redirects=True)
        self.assertIn(b'2 / 10', response_2.data)
        self.assertIn(b'1 / 10', response_2.data)
        self.assertIn(b'10 / 10', response_2.data)

    def test_question_topic(self):
        """
        test TC021
        this test makes sure that topics requested are the topics generated
        """
        topic_list = ['ceiling-function', 'set-union', 'function-target', 'set-partition']
        key_list = ['⌉', 'union', 'target', 'partition']
        self.login('test@test.com', '11111111')
        for i in topic_list:
            response = self.app.post(
                '/pre_quiz',
                data=dict(topic=i, questionNumber='1', btn='quiz'),
                follow_redirects=True)
            self.assertIn(bytes(key_list[topic_list.index(i)], 'utf-8'), response.data)

    # user logout
    def test_user_logout(self):
        """
        test TC022
        this test makes sure user log out function works properly
        """
        self.login('test@test.com', '11111111')
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)

    # admin login

    def test_login_admin(self):
        """
        test TC023
        testing login function for admin
        """

        response = self.login('admin@admin.com', '11111111')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Portal', response.data)

    # admin student progress
    def test_admin_student_progress(self):
        """
        test TC024
        testing admin access to students record
        """
        self.login('admin@admin.com', '11111111')
        response = self.app.get('/student_progress')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'50.0', response.data)

    def test_admin_add_announcement(self):
        """
        test TC025
        testing add announcement function for admin
        """
        self.login('admin@admin.com', '11111111')
        response = self.app.post(
            '/add_announcements',
            data=dict(topic='test_ann', content='test only content'),
            follow_redirects=True)
        quesries = mds.Announcements.query.all()
        print(quesries[0].content)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Announcement posted!', response.data)

    def test_admin_announcement_boundaries(self):
        """
        test TC026
        testing boundaries for announcement topic and body
        topic: min 1, max 80
        body: min 1, max 200
        """
        # topic
        topic_min_minus_one = ''
        topic_min = 'a'
        topic_min_plus_one = 'aa'

        topic_max_minus_one = self.random_string(79)
        topic_max = self.random_string(80)
        topic_max_plus_one = self.random_string(81)

        # body
        body_min_minus_one = ''
        body_min = 'a'
        body_min_plus_one = 'aa'

        body_max_minus_one = self.random_string(199)
        body_max = self.random_string(200)
        body_max_plus_one = self.random_string(201)

        list_allowed_topic = [topic_min, topic_min_plus_one,
                              topic_max_minus_one, topic_max]

        list_allowed_body = [body_min, body_min_plus_one,
                             body_max, body_max_minus_one]

        self.login('admin@admin.com', '11111111')

        for topic in list_allowed_topic:
            response = self.app.post(
                '/add_announcements',
                data=dict(topic=topic, content='test only content'),
                follow_redirects=True)
            self.assertIn(b'Announcement posted!', response.data)
            # query = mds.Announcements.query.filter_by(topic=topic)
            # db.session.delete(query)

        for body in list_allowed_body:
            response = self.app.post(
                '/add_announcements',
                data=dict(topic='topic', content=body),
                follow_redirects=True)
            self.assertIn(b'Announcement posted!', response.data)

        response_topic_min_minus_one = self.app.post(
            '/add_announcements',
            data=dict(topic=topic_min_minus_one, content='test only content'),
            follow_redirects=True)
        self.assertIn(b'Announcement should has a topic and text', response_topic_min_minus_one.data)

        response_topic_max_plus_one = self.app.post(
            '/add_announcements',
            data=dict(topic=topic_max_plus_one, content='test only content'),
            follow_redirects=True)
        self.assertIn(b'maximum allowed is 80', response_topic_max_plus_one.data)

        response_body_min_minus_one = self.app.post(
            '/add_announcements',
            data=dict(topic='topic', content=body_min_minus_one),
            follow_redirects=True)
        self.assertIn(b'Announcement should has a topic and text', response_body_min_minus_one.data)

        response_body_max_plus_one = self.app.post(
            '/add_announcements',
            data=dict(topic='topic', content=body_max_plus_one),
            follow_redirects=True)
        self.assertIn(b'maximum allowed is 200', response_body_max_plus_one.data)

    def test_add_content_boundaries(self):
        """
        test TC027
        testing boundaries for content topic and body
        topic: min 1, max 80
        body: min 1, max 1000
        """
        # topic
        topic_min_minus_one = ''
        topic_min = 'a'
        topic_min_plus_one = 'aa'

        topic_max_minus_one = self.random_string(79)
        topic_max = self.random_string(80)
        topic_max_plus_one = self.random_string(81)

        # body
        body_min = 'a'
        body_min_plus_one = 'aa'

        body_max_minus_one = self.random_string(999)
        body_max = self.random_string(1000)
        body_max_plus_one = self.random_string(1001)

        list_allowed_topic = [topic_min, topic_min_plus_one,
                              topic_max_minus_one, topic_max]

        list_allowed_body = [body_min, body_min_plus_one,
                             body_max, body_max_minus_one]

        self.login('admin@admin.com', '11111111')

        for topic in list_allowed_topic:
            response = self.app.post(
                '/add_material',
                data=dict(topic=topic, content='test only content'),
                follow_redirects=True)
            self.assertIn(b'Submitted', response.data)
            # query = mds.Announcements.query.filter_by(topic=topic)
            # db.session.delete(query)

        for body in list_allowed_body:
            response = self.app.post(
                '/add_material',
                data=dict(topic='topic', content=body),
                follow_redirects=True)
            self.assertIn(b'Submitted', response.data)

        response_topic_min_minus_one = self.app.post(
            '/add_material',
            data=dict(topic=topic_min_minus_one, content='test only content'),
            follow_redirects=True)
        self.assertIn(b'Topic can not be empty', response_topic_min_minus_one.data)

        response_topic_max_plus_one = self.app.post(
            '/add_material',
            data=dict(topic=topic_max_plus_one, content='test only content'),
            follow_redirects=True)
        self.assertIn(b'maximum allowed is 80', response_topic_max_plus_one.data)

        response_body_max_plus_one = self.app.post(
            '/add_material',
            data=dict(topic='topic', content=body_max_plus_one),
            follow_redirects=True)
        self.assertIn(b'maximum allowed is 1000', response_body_max_plus_one.data)

    def test_add_question(self):
        """
        test TC028
        test question maker function for admin
        """
        self.login('admin@admin.com', '11111111')
        response = self.app.post(
            '/question_generation',
            data=dict(topic='test_topic', question='test only question',
                      op1='t-op1', op2='t-op2', op3='t-op3', op4='t-op4', correctAnswer='1'),
            follow_redirects=True)
        self.assertIn(b'Question Successfully Added', response.data)

    def test_messenger(self):
        """
        test TC029
        test messenger functionality for admin
        should not be empty
        """
        self.login('admin@admin.com', '11111111')
        response = self.app.post(
            '/messenger',
            data=dict(user='test@test.com', msg='hi it is a test msg'),
            follow_redirects=True)
        self.assertIn(b'message sent', response.data)

        response_empty_field = self.app.post(
            '/messenger',
            data=dict(user='test@test.com', msg=''),
            follow_redirects=True)
        self.assertIn(b'can not be empty', response_empty_field.data)

    def test_admin_logout(self):
        """
        tes TC030
        test admin logout
        """
        self.login('admin@admin.com', '11111111')
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)

    # database
    def test_db_users(self):
        """
        tes TC031
        test users table in database
        """
        self.login('admin@admin.com', '11111111')
        user_object = mds.User.query.all()
        emails = []
        for user in user_object:
            emails.append(user.email)
        self.assertTrue(len(emails) > 0)


if __name__ == "__main__":
    unittest.main()
