import os
import random

from flask import Flask, render_template, redirect, url_for, flash, request
from wtform_fields import *
import models as mds
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, login_user, current_user, logout_user
import requests
from clarifai.errors import ApiError
import uuid
from datetime import date, datetime
from flask_cors import CORS, cross_origin
import smtplib
import string
from flask_sqlalchemy import SQLAlchemy

# APP
# from QuizApp.QuizApp.wtform_fields import AdminLogin

app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'SECRET'

# database configs
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgres://jhivjrfwkjzlff:9c37a83349353453a04fb5ae5102d86d9b84ae8fea94b46c24e01c3d4a4a0da2@ec2-54-81-37-115.compute-1.amazonaws.com:5432/d3lm6g7l0bs75i'

# 'postgres://jhivjrfwkjzlff:9c37a83349353453a04fb5ae5102d86d9b84ae8fea94b46c24e01c3d4a4a0da2@ec2-54-81-37-115.compute-1.amazonaws.com:5432/d3lm6g7l0bs75i'
# os.environ.get('DATABASE_URL')
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

        user_email = current_user.email
        if user_email == 'admin@admin.com':
            return redirect(url_for('admin_dashboard'))

        # redirect to pre_quiz(dashboard) page after login
        else:
            return redirect(url_for('pre_quiz'))

    # render login.html on GET request
    return render_template("login.html", form=login_form)


@app.route("/admin_dashboard", methods=['GET', 'POST'])
def admin_dashboard():
    """Login Page"""
    return render_template("admin_dashboard.html")


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

        if request.method == 'POST':
            if request.form['btn'] == 'quiz':

                # get number of requested questions from form
                question_num = request.form.get('questionNumber')
                selected_topic = request.form.get('topic')
                print(question_num)
                print(selected_topic)
                # make an API call based on users choices
                if selected_topic == 'union of sets' or selected_topic == 'symmetric difference' or selected_topic == 'partition' or selected_topic == 'difference of sets' or selected_topic == 'complement' or selected_topic == 'cartesian product':
                    resp = requests.get(
                        'https://mathgen-api.herokuapp.com' + topic_json['topics'][
                            selected_topic] + question_num + '/11')
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

            # if user asks learning content
            elif request.form['btn'] == 'content':

                # get topic from select form
                selected_topic = request.form.get('contentTopic')

                # get the selected topic from db
                content_queries = mds.Material.query.filter_by(topic=selected_topic).first()
                c_topic = content_queries.topic
                c_body = content_queries.content

                return render_template("content.html", c_topic=c_topic, c_body=c_body)

            # get topic for custom question
            elif request.form['btn'] == 'customTopic':

                # get the topic and questions from db
                selected_topic = request.form.get('customTopic')
                content_queries = mds.CustomQuestions.query.filter_by(topic=selected_topic).first()
                question_id = content_queries.question_id

                return redirect(url_for("custom_quiz_page", question_id=question_id))

    else:

        # get all the announcements from db
        quesries = mds.Announcements.query.all()
        topics = []
        dates = []
        contents = []

        # split the query into lists
        for i in quesries:
            contents.append(i.content)
            topics.append(i.topic)
            dates.append(i.date)

        table_data = []
        for i in range(len(topics)):
            arr = []
            arr.append(contents[i])
            arr.append(topics[i])
            arr.append(dates[i])
            table_data.append(arr)
        table_data.reverse()

        # get topics for questions from API
        topics_list = list(topic_json['topics'].keys())

        # get all available learning content data from db
        content_quesries = mds.Material.query.all()

        # get content topics
        content_topics = []
        for i in content_quesries:
            content_topics.append(i.topic)

        # get custom question data from db
        customQuestionQueries = mds.CustomQuestions.query.all()
        custom_question_topics = []
        for i in customQuestionQueries:
            custom_question_topics.append(i.topic)

        # render pre-quiz.html
        return render_template("pre_quiz.html", topics=topics_list, user_id=user_id, table_data=table_data,
                               content_topics=content_topics, custom_topics=custom_question_topics)


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

    # number of questions
    question_num = len(questions)

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
        return render_template("quiz.html", quiz_id=quiz_id, questions=questions, question_num=question_num)


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
    score_str = (str(scores).replace("[", '').replace(']', '').replace("'", ""))
    date_str = (str(dates).replace("]", '').replace('[', '').replace("'", ""))

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


@app.route('/add_material', methods=['GET', 'POST'])
def add_material():
    """
    A function for admin to add learning content
    """

    # POST request
    if request.method == 'POST':
        # get topic and content
        topic = request.form.get('topic')
        content = request.form.get('content')
        # validate entries
        if topic == '':
            err_msg = 'Topic can not be empty'
            return render_template("add_material.html", err_msg=err_msg)
        elif len(topic) > 80:
            err_msg = 'topic length is ' + str(len(topic)) + 'maximum allowed is 80'
            return render_template("add_material.html", err_msg=err_msg)
        elif len(content) > 1000:
            err_msg = 'content length is ' + str(len(content)) + 'maximum allowed is 1000'
            return render_template("add_material.html", err_msg=err_msg)
        # add entries into db
        else:
            material_query = mds.Material(topic=topic, content=content)
            db.session.add(material_query)
            db.session.commit()
            db.session.close()

            return render_template("add_material.html", submit_msg='Submitted!')

    else:
        return render_template("add_material.html", submit_msg='')


@app.route('/add_announcements', methods=['GET', 'POST'])
def add_announcement():
    """
    A function for admin to add announcements for users
    """
    # POST request
    if request.method == 'POST':
        # gets entries from form
        topic = request.form.get('topic')
        content = request.form.get('content')
        post_date = str(date.today())

        # validate entries
        if topic == '' or content == '':
            return render_template("add_announcements.html", err_msg='Announcement should has a topic and text')
        elif len(topic) > 80:
            err_msg = 'topic length is ' + str(len(topic)) + ' maximum allowed is 80'
            return render_template("add_announcements.html", err_msg=err_msg)
        elif len(content) > 200:
            err_msg = 'announcement length is ' + str(len(content)) + ' maximum allowed is 200'
            return render_template("add_announcements.html", err_msg=err_msg)

        # add entries to db
        else:
            material_query = mds.Announcements(topic=topic, content=content, date=post_date)
            db.session.add(material_query)
            db.session.commit()
            db.session.close()
            return render_template("add_announcements.html", submit_msg='Announcement posted!')

    return render_template("add_announcements.html")


@app.route('/student_progress', methods=['GET'])
def student_progress():
    """
    show all studet scores to admin
    """
    # get current user info
    quesries = mds.Scores.query.all()
    scores = []
    dates = []
    id = []
    for i in quesries:
        id.append(i.user_email)
        scores.append(i.score)
        dates.append(i.submit_date)
    user_str = (str(id).replace("[", '').replace(']', '').replace("'", ""))
    score_str = (str(scores).replace("[", '').replace(']', '').replace("'", ""))
    date_str = (str(dates).replace("]", '').replace('[', '').replace("'", ""))

    table_data = []
    for i in range(len(scores)):
        arr = []
        arr.append(id[i])
        arr.append(scores[i])
        arr.append(dates[i])
        table_data.append(arr)
    table_data.reverse()
    return render_template("student_progress.html", score_str=score_str, date_str=date_str, user_str=user_str,
                           table_data=table_data)


@app.route('/pre_quiz_generator', methods=['GET'])
def pre_quiz_generator():
    """
    pre quiz maker page for admin

    """
    return render_template("pre_quiz_generator.html")


@app.route('/question_generation', methods=['GET', 'POST'])
def question_generation():
    """
    add custom questions function for admin

    """
    # POST request
    if request.method == 'POST':
        # get entries
        topic = request.form.get('topic')
        question = request.form.get('question')
        op1 = request.form.get('op1')
        op2 = request.form.get('op2')
        op3 = request.form.get('op3')
        op4 = request.form.get('op4')
        correctAnswer = request.form.get('correctAnswer')
        # assigns a unique ID
        question_id = uuid.uuid1().hex
        question_query = mds.CustomQuestions(topic=topic, question_id=question_id, question=question, op1=op1, op2=op2,
                                             op3=op3, op4=op4, correctAnswer=correctAnswer)
        # add entries to db
        db.session.add(question_query)
        db.session.commit()
        db.session.close()

        return render_template("question_generator.html", submit_msg='Question Successfully Added!')

    return render_template("question_generator.html")


@app.route('/custom_quiz_page', methods=['GET', 'POST'])
def custom_quiz_page():
    """
    quiz page for users that renders questions added by admin
    """
    # gets question ID
    question_id = request.args.get("question_id")
    # gets question data from db
    user_object = mds.CustomQuestions.query.filter_by(question_id=question_id).all()
    questions = []

    # add question to JSON
    for i in user_object:
        questions.append(
            {'question': i.question,
             'questionID': i.question_id,
             'answers': [i.op1, i.op2, i.op3, i.op4],
             'correctAnswer': i.correctAnswer,
             'topic': i.topic
             }
        )

    # gets current user and date
    user_email = current_user.email
    submit_date = str(date.today())
    question_num = len(questions)
    point = 100 / 1
    score_int = 0
    quiz_id = uuid.uuid1().hex
    # POST request
    if request.method == 'POST':
        user_selections = []
        for i in questions:
            questionId = i['questionID']
            selected = int(request.form.get(questionId))
            user_selections.append(selected)
            if selected == int(i['correctAnswer']):
                score_int = score_int + point
        score = str(score_int)

        # add submition data to db
        quiz_query = mds.Scores(quiz_id=quiz_id, user_email=user_email, user_selections=user_selections,
                                submit_date=submit_date, score=score)
        db.session.add(quiz_query)
        db.session.commit()
        db.session.close()
        return render_template("post_quiz.html", quiz_id=quiz_id, questions=questions, user_selections=user_selections,
                               submit_date=submit_date, user_email=user_email, score=score)

    return render_template("custom_quiz_page.html", quiz_id=quiz_id, questions=questions)


@app.route('/messenger', methods=['GET', 'POST'])
def messenger():
    """
    messenger function for admin
    """
    # POST request
    if request.method == 'POST':
        # get inquire info
        now = datetime.now()
        date = now.strftime("%d/%m/%Y %H:%M:%S")
        sender = 'admin'
        user = request.form.get('user')
        msg = request.form.get('msg')
        # validate msg
        if msg == '':
            return render_template("messenger.html", err_msg='Message can not be empty')
        # add msg to db
        else:
            msg_query = mds.Messages(user=user, msg=msg, date=date, sender=sender)
            db.session.add(msg_query)
            db.session.commit()
            db.session.close()
            return render_template("messenger.html", submit_msg='message sent')

    # gets all available users
    user_quesries = mds.User.query.all()
    users = []
    for i in user_quesries:
        users.append(i.email)
    return render_template("messenger.html", users=users)


@app.route('/inbox', methods=['GET', 'POST'])
def inbox():
    """
    Inbox for users to get msg from admin
    :return:
    """
    # get current users email
    user_email = current_user.email
    # check all messages in db for current user
    msg_quesries = mds.Messages.query.filter_by(user=user_email).all()
    msgs = []
    senders = []
    dates = []
    for i in msg_quesries:
        msgs.append(i.msg)
        senders.append(i.sender)
        dates.append(i.date)

    table_data = []
    for i in range(len(msgs)):
        arr = []
        arr.append(msgs[i])
        arr.append(senders[i])
        arr.append(dates[i])
        table_data.append(arr)
    table_data.reverse()
    return render_template("inbox.html", data=table_data)


def random_string(length):
    """
    random string generator to generating new password
    :param length: length of the string
    :return: string
    """
    return ''.join(random.choices(string.ascii_uppercase +
                                  string.digits, k=length))


@app.route('/forget_pass', methods=['GET', 'POST'])
def forget_pass():
    """
    function to generate and send new password with email
    """
    # POST request
    if request.method == 'POST':
        # senders information
        sender_email = "questionsystem2020@gmail.com"
        # using env variable to not disclose email pass
        mail_pass = os.environ.get('EMAILPASSWORD')

        # get the receivers email from form
        reciever_email = request.form.get('email')
        # generate a new password with length of 10
        new_pass = random_string(10)
        message = f'Your new password is {new_pass}'
        msg = f'An email containing your new password has sent to {reciever_email}'
        # connect to gmail with TLS
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # login to gmail
        server.login("questionsystem2020@gmail.com", mail_pass)
        # hash generated password
        hashed_paswd = pbkdf2_sha256.hash(new_pass)
        # execute a quesry to replace old pass with new one
        r = db.engine.execute(f"UPDATE users SET password = '{hashed_paswd}' WHERE email = '{reciever_email}';")
        db.session.commit()
        # send new pass to user
        server.sendmail(sender_email, reciever_email, message)

        return render_template("forget_pass.html", msg=msg)

    return render_template("forget_pass.html")


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
    app.run(debug=True)
