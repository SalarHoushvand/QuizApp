from flask import Flask, render_template, redirect, url_for, flash, request
from wtform_fields import *
import models as mds
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
import requests
from clarifai.errors import ApiError
import uuid
from datetime import date

# APP
app = Flask(__name__)
app.secret_key = 'replace later'

# database configs
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgres://jhivjrfwkjzlff:9c37a83349353453a04fb5ae5102d86d9b84ae8fea94b46c24e01c3d4a4a0da2@ec2-54-81-37-115.compute-1.amazonaws.com:5432/d3lm6g7l0bs75i'
db = mds.SQLAlchemy(app)

login = LoginManager()
login.init_app(app)


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

        return redirect(url_for('login'))
        # return redirect(url_for("login"))

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

        return redirect(url_for('pre_quiz'))

    return render_template("login.html", form=login_form)


@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))


# =====================================================================================================================


@app.route("/pre_quiz", methods=['GET', 'POST'])
def pre_quiz():
    user_email = current_user.email
    user_id_arr = user_email.split("@")
    user_id=user_id_arr[0]
    if request.method == 'POST':
        question_num = request.form.get('questionNumber')
        resp = requests.get('https://mathgen-api.herokuapp.com/union/' + question_num + '/11')
        if resp.status_code != 200:
            # This means something went wrong.
            raise ApiError('GET /tasks/ {}'.format(resp.status_code))
        response = resp.json()
        questions = response['questions']
        quiz_json = str(response)
        quiz_id = uuid.uuid1().hex
        quiz = mds.QuizJson(quiz_id=quiz_id, quiz_json=quiz_json)
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for("quiz", quiz_id=quiz_id))
    else:

        topics = requests.get('https://mathgen-api.herokuapp.com/topics')
        topic_json = topics.json()
        topics_list = list(topic_json['topics'].keys())
        # add_questions(questions, quiz_id)
        return render_template("pre_quiz.html", topics=topics_list, user_id=user_id)


@app.route("/quiz", methods=['GET', 'POST'])
def quiz():
    quiz_id = request.args.get("quiz_id")
    user_object = mds.QuizJson.query.filter_by(quiz_id=quiz_id).first()
    quiz = user_object.quiz_json
    questions = eval(quiz)['questions']
    user_email = current_user.email
    submit_date = str(date.today())

    # to calculate score
    question_num = len(questions)
    point = 100 / question_num
    score_int = 0

    if request.method == 'POST':
        user_selections = []
        for i in questions:
            questionId = i['questionID']
            selected = int(request.form.get(questionId))
            user_selections.append(selected)
            if selected == i['correctAnswer']:
                print('correct')
                score_int = score_int + point
            else:
                print('wrong')
        score = str(score_int)
        quiz = mds.Scores(quiz_id=quiz_id, user_email=user_email, user_selections=user_selections,
                          submit_date=submit_date, score=score)
        db.session.add(quiz)
        db.session.commit()

        return render_template("post_quiz.html", quiz_id=quiz_id, questions=questions, user_selections=user_selections,
                               submit_date=submit_date, user_email=user_email, score=score)
    else:
        return render_template("quiz.html", quiz_id=quiz_id, questions=questions)


# =====================================================================================================================
# @app.route("/quiz", methods=['GET', 'POST'])
# def quiz():
#     if request.method == 'POST':
#         return 'post'
#     else:
#         quiz_id = '37264308e1ad11ea823f8c164545a35c'
#
#         user_object = mds.Question.query.filter_by(quiz_id=quiz_id).all()
#         question = user_object[0].question
#         option1 = user_object[0].option1
#         option2 = user_object[0].option2
#         option3 = user_object[0].option3
#         option4 = user_object[0].option4
#         answer = user_object[0].answer
#         point = '10'
#         return render_template("quiz.html", question=question)
#         #add_questions(questions, quiz_id)
#
#


#
# def add_questions(questions ,quiz_id):
#     quiz_id = quiz_id
#     for i in questions:
#         print(i['questionID'])
#         questionID = i['questionID']
#         question_topic = 'title'
#         question = i['question']
#         option1 = i['answers'][0]
#         option2 = i['answers'][1]
#         option3 = i['answers'][2]
#         option4 = i['answers'][3]
#         answer = i['correctAnswer']
#         point = '10'
#         selected_answer = request.form.get(questionID)
#         question = mds.Question(question_topic=question_topic, question=question, option1=option1, option2=option2,
#                                 option3=option3, option4=option4, answer=answer,
#                                 point=point, quiz_id=quiz_id, selected_answer=selected_answer)
#         db.session.add(question)
#         db.session.commit()
#
@app.route("/post_quiz", methods=['GET'])
def post_quiz():
    quiz_id = '37264308e1ad11ea823f8c164545a35c'

    user_object = mds.Question.query.filter_by(quiz_id=quiz_id).all()
    questions = {}
    for i in user_object:
        question = i.question
        option1 = i.option1
        option2 = i.option2
        option3 = i.option3
        option4 = i.option4
        answer = i.answer

        questions.update([
            {
                "answerSelectionType": "single",
                "answers": [
                    option1,
                    option2,
                    option3,
                    option4
                ],
                "correctAnswer": answer,
                "explanation": "",
                "messageForCorrectAnswer": "Correct Answer",
                "messageForIncorrectAnswer": "Incorrect Answer",
                "point": "10",
                "question": question,
                "questionType": "text"
            }
        ])

    return render_template("quiz.html", questions=questions)


# @app.route("/dashboard", methods=['POST','GET']):
# def dashbaord():
#
#
# @app.route("/pre_quiz", methods=['GET', 'POST'])
# def pre_quiz():
#
#     if request.method == 'POST':
#         question_num = request.form.get('questionNumber')
#         resp = requests.get('https://mathgen-api.herokuapp.com/probability/multiplication/'+question_num)
#         if resp.status_code != 200:
#             # This means something went wrong.
#             raise ApiError('GET /tasks/ {}'.format(resp.status_code))
#         response = resp.json()
#         questions = response['questions']
#         quiz_id = uuid.uuid1().hex
#         for i in questions:
#             question_topic = response['quizTitle']
#             question = i['question']
#             option1 = i['answers'][0]
#             option2 = i['answers'][1]
#             option3 = i['answers'][2]
#             option4 = i['answers'][3]
#             answer = i['correctAnswer']
#             point = '10'
#
#             question_query = mds.Question(question_topic=question_topic, question=question, option1=option1, option2=option2,
#                                     option3=option3, option4=option4, answer=answer,
#                                     point=point, quiz_id=quiz_id)
#             db.session.add(question_query)
#             db.session.commit()
#         return url_for('quiz', quiz_id=quiz_id)
#     else:
#         topics = requests.get('https://mathgen-api.herokuapp.com/topics')
#         topic_json = topics.json()
#         topics_list = list(topic_json['topics'].keys())
#         # add_questions(questions, quiz_id)
#         return render_template("pre_quiz.html", topics= topics_list)


# app run
if __name__ == "__main__":
    app.run(debug=True)
