from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """ Table for users """

    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def get_id(self):
        return (self.user_id)


class Admin(UserMixin, db.Model):
    """ Table for users """

    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def get_id(self):
        return (self.user_id)


class QuizJson(db.Model):
    """save requested json file for each quiz"""

    __tablename__ = "quizJson"
    json_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String())
    quiz_json = db.Column(db.String())

    def get_id(self):
        return (self.json_id)


class Scores(db.Model):
    """save user answers and scores"""

    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String())
    user_selections = db.Column(db.String())
    quiz_id = db.Column(db.String())
    submit_date = db.Column(db.String())
    score = db.Column(db.String())


class Material(db.Model):
    """save user answers and scores"""

    __tablename__ = "material"
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String())
    content = db.Column(db.String())


class Announcements(db.Model):
    """save user answers and scores"""

    __tablename__ = "announcements"
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String())
    content = db.Column(db.String())
    date = db.Column(db.String())


class CustomQuestions(db.Model):
    """save user answers and scores"""

    __tablename__ = "custom_questions"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.String())
    topic = db.Column(db.String())
    question = db.Column(db.String())
    op1 = db.Column(db.String())
    op2 = db.Column(db.String())
    op3 = db.Column(db.String())
    op4 = db.Column(db.String())
    correctAnswer = db.Column(db.String())


class Messages(db.Model):
    """save user answers and scores"""

    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String())
    msg = db.Column(db.String())
    date = db.Column(db.String())
    sender = db.Column(db.String())
