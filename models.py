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




class Question(db.Model):
    """ Table for users """

    __tablename__ = "questions"
    question_id = db.Column(db.Integer, primary_key=True)
    question_topic = db.Column(db.String(), nullable=False)
    question = db.Column(db.String(), nullable=False)
    option1 = db.Column(db.String(), nullable=False)
    option2 = db.Column(db.String(), nullable=False)
    option3 = db.Column(db.String(), nullable=False)
    option4 = db.Column(db.String(), nullable=False)
    answer = db.Column(db.Integer(), nullable=False)
    point = db.Column(db.String(), nullable=True)
    quiz_id = db.Column(db.String(), nullable=True)
    selected_answer = db.Column(db.String(), nullable=True)


    def get_id(self):
        return (self.question_id)

class QuizJson(db.Model):
    """save requested json file for each quiz"""

    __tablename__ = "quizJson"
    json_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String())
    quiz_json = db.Column(db.String())
    user_email = db.Column(db.String())

    def get_id(self):
        return (self.json_id)

class Scores(db.Model):
    """save user answers and scores"""

    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String())
    user_selections = db.Column(db.String())
    quiz_id=db.Column(db.String())
    submit_date=db.Column(db.String())
    score=db.Column(db.String())
