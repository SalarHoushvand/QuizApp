import os

from flask import Flask, render_template, redirect, url_for, flash, request
from wtform_fields import *
import models as mds
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, login_user, current_user, logout_user
import requests
from clarifai.errors import ApiError
import uuid
from datetime import date

# APP
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET')

# database configs
app.config[
    'SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = mds.SQLAlchemy(app)

# app configs
login = LoginManager()
login.init_app(app)


# load the current user
@login.user_loader
def load_user(user_id):
    return mds.User.query.get(int(user_id))


# main page
@app.route("/", methods=['GET', 'POST'])
def index():
    """Registration : Get User Info and add to database"""

    # Define form from wtform-fields
    reg_form = RegistrationForm()

    # Validating the inputs
    if reg_form.validate_on_submit():
        email = reg_form.email.data
        password = reg_form.password.data

        # hash password before adding to database
        hashed_paswd = pbkdf2_sha256.hash(password)

        # define user in order to add to db
        user = mds.User(email=email, password=hashed_paswd)
        db.session.add(user)
        db.session.commit()
        db.session.close()
        # redirect to login page after register
        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login Page"""
    # Define Login form
    login_form = LoginForm()

    # Validating login form
    if login_form.validate_on_submit():
        user_object = mds.User.query.filter_by(email=login_form.email.data).first()
        login_user(user_object)

        # redirect to pre_quiz(dashboard) page after login
        return redirect(url_for('pre_quiz'))

    # render login.html on GET request
    return render_template("login.html", form=login_form)


@app.route("/logout", methods=['GET'])
def logout():
    """
    logout function
    """
    logout_user()

    # redirect to login page after logout
    return redirect(url_for('login'))


@app.route("/pre_quiz", methods=['GET', 'POST'])
def pre_quiz():
    """ Pre-quiz( dashboard ) page"""

    # get current users email
    user_email = current_user.email

    # get the text before @ to show user id after welcome text
    user_id_arr = user_email.split("@")
    user_id = user_id_arr[0]

    # get available topics from API
    topics = requests.get('https://mathgen-api.herokuapp.com/topics')

    # save topics in a var
    topic_json = topics.json()

    if request.method == 'POST':

        # get number of requested questions from form
        question_num = request.form.get('questionNumber')
        selected_topic = request.form.get('topic')
        print(selected_topic)
        # make an API call based on users choices
        if selected_topic == 'union of sets' or selected_topic == 'symmetric difference' or selected_topic == 'partition' or selected_topic == 'difference of sets' or selected_topic == 'complement' or selected_topic == 'cartesian product':
            resp = requests.get(
                'https://mathgen-api.herokuapp.com' + topic_json['topics'][selected_topic] + question_num + '/11')
        else:
            resp = requests.get(
                'https://mathgen-api.herokuapp.com' + topic_json['topics'][selected_topic] + question_num)

        # check if the API call was successful
        if resp.status_code != 200:
            # This means something went wrong.
            raise ApiError('GET /tasks/ {}'.format(resp.status_code))

        # save response from API
        response = resp.json()

        # change quiz from json to string
        quiz_json = str(response)

        # generates a unique id for quiz
        quiz_id = uuid.uuid1().hex

        # add quiz_id and quiz_json to database
        quiz_query = mds.QuizJson(quiz_id=quiz_id, quiz_json=quiz_json)
        db.session.add(quiz_query)
        db.session.commit()
        db.session.close()

        # redirect to quiz page
        return redirect(url_for("quiz", quiz_id=quiz_id))

    else:

        # get the keys from each topic to show in select menu
        topics_list = list(topic_json['topics'].keys())

        # render pre-quiz.html
        return render_template("pre_quiz.html", topics=topics_list, user_id=user_id)


@app.route("/quiz", methods=['GET', 'POST'])
def quiz():
    """quiz page"""

    # get quiz_id sent from pre-quiz
    quiz_id = request.args.get("quiz_id")

    # get the row with requested quiz_id
    user_object = mds.QuizJson.query.filter_by(quiz_id=quiz_id).first()

    # get the quiz in json
    quizJson = user_object.quiz_json

    # change quiz to dict and get the questions array
    questions = eval(quizJson)['questions']

    # get current users emaik
    user_email = current_user.email

    # get the date for today
    submit_date = str(date.today())

    # to calculate score
    question_num = len(questions)
    point = 100 / question_num
    score_int = 0

    if request.method == 'POST':

        # save users selections in an array
        user_selections = []

        for i in questions:
            questionId = i['questionID']
            selected = int(request.form.get(questionId))
            user_selections.append(selected)
            if selected == i['correctAnswer']:
                score_int = score_int + point

        # save calculated score in a var
        score = str(score_int)

        # add the quiz with users answers to database
        quiz_query = mds.Scores(quiz_id=quiz_id, user_email=user_email, user_selections=user_selections,
                                submit_date=submit_date, score=score)
        db.session.add(quiz_query)
        db.session.commit()
        db.session.close()

        # render post quiz
        return render_template("post_quiz.html", quiz_id=quiz_id, questions=questions, user_selections=user_selections,
                               submit_date=submit_date, user_email=user_email, score=score)
    else:
        # render quiz.html on GET request
        return render_template("quiz.html", quiz_id=quiz_id, questions=questions)


@app.route('/progress', methods=['GET'])
def progress():
    """get user progress and show it in a chart"""

    # get current user info
    user_email = current_user.email
    quesries = mds.Scores.query.filter_by(user_email=user_email).all()
    scores = []
    dates = []
    for i in quesries:

        scores.append(i.score)
        dates.append(i.submit_date)
    score_str = (str(scores).replace("[", '').replace(']', '').replace("'",""))
    date_str = (str(dates).replace("]", '').replace('[', '').replace("'",""))

    table_data = []
    for i in range(len(scores)):
        arr = []
        arr.append(scores[i])
        arr.append(dates[i])
        table_data.append(arr)
    table_data.reverse()

    return render_template("progress.html", score_str=score_str, date_str=date_str, table_data=table_data)


@app.route('/about', methods=['GET'])
def about():
    """about the project and credits"""

    return render_template("about.html")


# error handlings

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_logged_in(e):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500


# app run
if __name__ == "__main__":
    app.run(debug=False)
