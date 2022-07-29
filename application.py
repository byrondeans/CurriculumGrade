#CurriculumGrade is an education web application with social networking features.
#It allows educators to create courses and quizes for those courses.
#Copyright (C) 2020  Ashley Byron Deans
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os, requests, json
from flask import Flask, session, render_template, request, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_socketio import SocketIO, emit
import datetime
import random
import time, sys

sys.path.append('/usr/lib/python3/dist-packages/')

app = Flask(__name__)


@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
                and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

DATABASE_URL = 'postgresql://127.0.0.1:5432/cg'

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = '2Ma3CGdW4gl2GPOvcxS'
app.permanent_session_lifetime = datetime.timedelta(days=365)

socketio = SocketIO(app, engineio_logger=True, logger=True, cors_allowed_origins=['http://curriculumgrade.com', 'https://curriculumgrade.com', 'https://www.curriculumgrade.com', 'http://127.0.0.1:5000'])

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

logged_in = 0

@app.route("/")
def index():
	logged_in = 0
	videos_to_display = 0
	videos = []
	quizzes = []
	user_id = 0
	your_videos = ""
	randomint = 0
	quizzes = []
	basic_security = 0
	investoraccess = 0
	requests = 0
	num_notifications = 0
	investorid = 0
	now = 0
	if session.get("basicsecurity") is None:
		basic_security = 0
	else:
		investorid = session.get("investorid") 
		expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investorid}).fetchone()
		firstaccess = expiration.firstaccess
		timelimit = expiration.timelimit
		now = time.time()

		if(now < (firstaccess + timelimit)):
			basic_security = 1
			investoraccess = 1
		else:
			session.pop('investorid', None)
			session.pop('basicsecurity', None)

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investorid, "ip_address": ip_address, "page": "index", "unixtime": now})
	db.commit()

	if(basic_security):
		logged_in = 0
		quizzes = 0
		user_id = 0
		randomint = 0
		if session.get("username") is None:
			session["username"] = []
			session["logged_in"] = 0
			logged_in = 0
		elif (session["logged_in"] == 1):
			logged_in = 1
			user_id = session["user_id"]
		else:
			session["logged_in"] = 0
			logged_in = 0
    
		your_videos = ""
		if(logged_in): 
			your_videos = db.execute("SELECT * FROM lecture_video WHERE user_id = %s AND completed = 1 AND deleted = FALSE ORDER BY created_on DESC" % user_id).fetchall()
			quizzes = db.execute("SELECT * FROM (lecture_video INNER JOIN quiz_grades ON lecture_video.id = quiz_grades.video_id) INNER JOIN users ON quiz_grades.user_id = users.id WHERE lecture_video.user_id = :user_id ORDER BY quiz_grades.created_on DESC LIMIT 5", {"user_id": user_id}).fetchall()

			requests = db.execute("SELECT * FROM student_request INNER JOIN users ON student_request.student_id = users.id WHERE instructor_id = %s AND permission = False ORDER BY date_requested DESC" % user_id).fetchall()
        
			videos = db.execute("SELECT * FROM lecture_video WHERE completed = 1 AND deleted = FALSE ORDER BY created_on DESC LIMIT 5")
  
			videos_to_display = 1
			randomint = random.randint(1,100)

			friend_requests = db.execute("SELECT * FROM friends WHERE friends.user_id_accepter = :user_id AND (time_accepted IS NULL AND time_denied IS NULL)", {"user_id": user_id}).fetchall()
			db.commit()
			num_notifications = len(friend_requests)

			video_requests = db.execute("SELECT * FROM student_request INNER JOIN users ON student_request.student_id = users.id WHERE instructor_id = %s AND permission = False ORDER BY date_requested DESC" % user_id).fetchall()
			db.commit()
			num_notifications = num_notifications + len(video_requests)

			new_messages = db.execute("SELECT * FROM messages WHERE user_id_receiver = %s AND time_viewed IS NULL" % user_id).fetchall()
			num_notifications = num_notifications + len(new_messages)
	return render_template("index.html", logged_in=logged_in, session=session, videos_to_display=videos_to_display, videos=videos, quizzes=quizzes, user_id=user_id, your_videos=your_videos, randomint=randomint, investoraccess=investoraccess, requests=requests, num_notifications=num_notifications)


@app.route("/basicsecurity", methods=["GET", "POST"])
def basicsecurity():
    cont = 0
    message = ""
    code = ""
    code2 = ""
    name = ""
    timelimit = 0
    displaytimelimit = 0
    if request.method == "POST":
        code = request.form.get("code")
        investorinfo = db.execute("SELECT id, name, timelimit, firstaccess FROM investorinfo WHERE accesscode = :code", {"code": code}).fetchone()
        session.permanent = True

        if(investorinfo):
            session["basicsecurity"] = "SET"
            session["name"] = investorinfo.name
            name = investorinfo.name
            investor_id = investorinfo.id
            session["investorid"] = investor_id
            
            timelimit = investorinfo.timelimit
            min, sec = divmod(timelimit, 60)
            displaytimelimit = str(min) 
            cont = 1
            now = time.time()
            if(investorinfo.firstaccess < 1): 
                timerstarted = db.execute("UPDATE investorinfo SET firstaccess = :unixtime WHERE id = :investor_id", {"unixtime": now, "investor_id": investor_id})
                db.commit()
            else:
                message = "You have already entered your investor code and if you are not able to use the site, you will need to request a new code."
                cont = 0

            ip_address = str(request.remote_addr)
            submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "basicsecurity", "unixtime": now})
            db.commit()
        else:
            message = "Wrong security code " + str(code)

    return render_template("basicsecurity.html", message=message, cont=cont, name=name, displaytimelimit=displaytimelimit)


@app.route("/video/<int:video_id>")
def video(video_id):
	if session.get("username") is None:
		session["username"] = []
		session["logged_in"] = 0
		logged_in = 0
	elif (session["logged_in"] == 1):
		logged_in = 1
		user_id = session["user_id"]
	else:
		session["logged_in"] = 0
		logged_in = 0

	preapproved = 0
	require_preapprove = 0

#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "video" + str(video_id), "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	if(investoraccess):

		num_correct = 0
		total_questions = 0
		percentage = 0
		quiz_not_taken = 1
		video = db.execute("SELECT * FROM lecture_video WHERE id='%s'" % video_id).fetchone()
		username_db = db.execute("SELECT * FROM users WHERE id='%s'" % video.user_id).fetchone()
		videos_username = username_db.username
		
		video_creator_user_id = video.user_id
		if video_creator_user_id == user_id:
			display_request_approval_link = 0
		else:
			display_request_approval_link = 1

		test = video.created_on
		investoraccess = 0
		already_requested = 0
		preapproved = 0
		require_preapprove = 0
		approval = 0

	if(logged_in): 

		select_string = "SELECT * FROM quiz_grades WHERE user_id = " + str(user_id) + " AND video_id = " + str(video_id)
		quiz_grade = db.execute(select_string).fetchone()
	if(quiz_grade):
		quiz_not_taken = 0
		num_correct = quiz_grade.num_correct
		total_questions = quiz_grade.num_total_questions
		percentage = 100 * (num_correct/total_questions)
		percentage = round(percentage, 2)
	else:
		if(video.preapprove):
			require_preapprove = 1
			select_string = "SELECT * FROM student_request WHERE student_id = " + str(user_id) + " AND video_id = " + str(video_id)
			approval = db.execute(select_string).fetchone()
		if(approval):
			if(approval.permission):
				preapproved = 1
			else:
				already_requested = 1

	video_comments = db.execute("SELECT video_comments.*, users.username FROM video_comments LEFT JOIN users ON video_comments.posting_user = users.id WHERE video_id = %s ORDER BY video_comments.created_on DESC LIMIT 50" % video_id).fetchall()
	
	comments_array = []
	for i in video_comments:
		comment_id = i.id
		result = db.execute("SELECT video_comment_replies.*, users.username FROM video_comment_replies LEFT JOIN users ON users.id = video_comment_replies.replying_user WHERE video_comment_id = %s ORDER BY video_comment_replies.created_on DESC LIMIT 25" % comment_id).fetchall()
		db.commit()
		replies_array = []
		for j in result:
			replies_array.append([j.id, j.replying_user, j.created_on, j.reply, j.username])
		
		comments_array.append([i.id, i.username, i.comment, i.created_on, replies_array])	

	video_by_user_viewing = 0
	if user_id == video_creator_user_id:
		video_by_user_viewing = 1

	result = db.execute("SELECT * FROM quiz_grades WHERE video_id = %s" % video_id).fetchall()
	num_users_have_taken_quiz = len(result)

	return render_template("video.html", test=test, video=video, video_id=video_id, num_correct=num_correct, total_questions=total_questions, percentage=percentage, quiz_not_taken=quiz_not_taken, videos_username=videos_username, require_preapprove=require_preapprove, preapproved=preapproved, already_requested=already_requested, display_request_approval_link=display_request_approval_link, video_page=1, comments_array=comments_array, user_id=user_id, video_by_user_viewing=video_by_user_viewing, num_users_have_taken_quiz=num_users_have_taken_quiz) 

@app.route("/quizzes_taken/<int:video_id>")
def quizzes_taken(video_id):
	result = db.execute("SELECT quiz_grades.*, users.username FROM quiz_grades LEFT JOIN users ON users.id = quiz_grades.user_id WHERE video_id = %s" % video_id).fetchall()
	return render_template("quizzes_taken.html", result=result, video_id=video_id)


@app.route("/request_video_approval/<int:video_id>")
def request_video_approval(video_id): 
#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        investoraccess = 1
    else:
        investoraccess = 0

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "request_video_approval" + str(video_id), "unixtime": now})
    db.commit()
#### END INVESTOR SECTION ####
    student_id = session["user_id"]
    now = time.time()

    video = db.execute("SELECT * FROM lecture_video WHERE id='%s'" % video_id).fetchone()

    instructor_id = video.user_id
    
    submitted = db.execute("INSERT INTO student_request (student_id, instructor_id, video_id, date_requested, permission) VALUES (:student_id, :instructor_id, :video_id, :unixtime, :permission)", {"student_id": student_id, "instructor_id": instructor_id, "video_id": video_id, "unixtime": now, "permission": False})
    db.commit()

    return render_template("request_video_approval.html")


@app.route("/grant_access_request/<int:video_id>")
def grant_access_request(video_id):

#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "video" + str(video_id), "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	if investoraccess:
		user_id = session["user_id"]
 
		now = time.time()
		val2 = db.execute("UPDATE student_request SET permission = True, date_granted = :unixtime WHERE video_id = :video_id AND instructor_id = :user_id", {"unixtime": now, "video_id": video_id, "user_id": user_id})
		db.commit()

		return render_template("grant_access_request.html")


@app.route("/deletevideo/<int:video_id>")
def deletevideo(video_id):
#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        investoraccess = 1
    else:
        investoraccess = 0

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "video" + str(video_id), "unixtime": now})
    db.commit()
#### END INVESTOR SECTION ####

    video = db.execute("SELECT user_id FROM lecture_video WHERE id='%s'" % video_id).fetchone() 
    user_id = session["user_id"]
    video_deleted = 0

    if(video.user_id == user_id):

        now = time.time()
        val2 = db.execute("UPDATE lecture_video SET deleted = TRUE, deleted_date = :unixtime WHERE id = :video_id", {"unixtime": now, "video_id": video_id})
        db.commit()
        video_deleted = 1

    if investoraccess:
        return render_template("deletevideo.html", video_deleted=video_deleted)


@app.route("/quiz/<int:video_id>", methods=["GET", "POST"])
def quiz(video_id):
    logged_in = 0
    user_id = 0
    if session.get("username") is None:
        session["username"] = []
        session["logged_in"] = 0
        logged_in = 0
    elif (session["logged_in"] == 1):
        logged_in = 1    
        user_id = session["user_id"]
    else:
        session["logged_in"] = 0
        logged_in = 0


    video=""
    questions=""
    test = 1
    question_array = []
    answer = ""
    supplied_answer = 0
    real_answer = 0
    quizzes = ""
    time_to_display_score = 0
    quiz_score = 0
    j = 1
    test_array = []
    test_array2 = []
    question_final = ""
    rand_num = 0
    question_array = []
    qa_arr = []
    question_array_display = []
    question_check = ""
    qcheck = 0
    final_display_arr = []
    final_question_vs_answer = []
    fstring = ""
    num_correct = 0
    question_id = 0
    display_question = ""


#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    #investorid = 1 
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()
    proceed_with_submitting = 1
    if(now < (firstaccess + timelimit)):
        logged_in = logged_in
    else:
        logged_in = 0

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "quiz" + str(video_id), "unixtime": now})
    db.commit()
#### END INVESTOR SECTION ####

#check if the user has permission for the quiz

    video = db.execute("SELECT * FROM lecture_video WHERE id='%s'" % video_id).fetchone()
    if(video.preapprove):
        select_string = "SELECT * FROM student_request WHERE student_id = " + str(user_id) + " AND video_id = " + str(video_id)
        approval = db.execute(select_string).fetchone()
        if(approval.permission):
            logged_in = logged_in
        else:
            logged_in = 0


    if(logged_in):

        if request.method == "POST": 
            
            #get the number of questions from lecture_video
            
            number_of_questions = video.number_of_questions

            while(j <= number_of_questions):
            
                query_string = "SELECT * FROM questions WHERE lecture_video_id = " + str(video_id) + " AND question_number = " + str(j)


                question = db.execute(query_string).fetchall()
                
                fstring = "answer" + str(j)
                num_provided_answer = request.form.get(fstring)
                
                
                num_q = len(question)
                if(num_q > 1):
                    query_string = "SELECT * FROM quiz_questions WHERE user_id = " + str(user_id) + " AND lecture_video_id = " + str(video_id) + " AND question_num = " + str(j)
                    quiz_question = db.execute(query_string).fetchone()
                    question_id = quiz_question.question_id
                    question2 = db.execute("SELECT * FROM questions WHERE id = '%s'" % question_id).fetchone()
                    
                    num_actual_answer = question2.answer
                    display_question = question2.question
                    choices = question2.choices
                    #actual_answer = 1
                else:
                    num_actual_answer = question[0][2]#the answer column
                    display_question = question[0][1]
                    question_id = question[0][0]#the id
                    choices = question[0][3]


                final_display_arr.append(display_question)


                choices_array = choices.split(';;;&&&')

                str_provided_answer = choices_array[int(num_provided_answer) - 1]
                str_actual_answer = choices_array[int(num_actual_answer) - 1]

                final_display_arr.append(str_provided_answer)
                final_display_arr.append(str_actual_answer)
                
                if(int(num_provided_answer) == int(num_actual_answer)):
                    final_display_arr.append(1)
                    final_display_arr.append(j)
                    final_question_vs_answer.append(final_display_arr)
                    num_correct = num_correct + 1
                else:
                    final_display_arr.append(0)
                    final_display_arr.append(j)
                    final_question_vs_answer.append(final_display_arr)

                final_display_arr = [] 

                check_already_took_quiz = db.execute("SELECT * FROM quiz_grades WHERE video_id = :lecture_video_id AND user_id = :user_id", {"user_id": user_id, "lecture_video_id": video_id}).fetchall()
                for k in check_already_took_quiz:
                    proceed_with_submitting = 0

                if proceed_with_submitting:
                    save_answer = db.execute("INSERT INTO answers (user_id, question_id, lecture_video_id, answer, created_on) VALUES (:user_id, :question_id, :lecture_video_id, :provided_answer, CURRENT_TIMESTAMP)", {"user_id": user_id, "question_id": question_id, "lecture_video_id": video_id, "provided_answer": num_provided_answer})    
                    db.commit()
                 
                j = j + 1

            if proceed_with_submitting:
                grade_insert = db.execute("INSERT INTO quiz_grades (user_id, video_id, created_on, num_correct, num_total_questions) VALUES (:user_id, :video_id, CURRENT_TIMESTAMP, :num_correct, :num_total_questions)", {"user_id": user_id, "video_id": video_id, "num_correct": num_correct, "num_total_questions": number_of_questions })
                db.commit()
            quiz_score = 100 * (int(num_correct) / int(number_of_questions))
            time_to_display_score = 1

        else:   #request method not POST
            video = db.execute("SELECT * FROM lecture_video WHERE id='%s'" % video_id).fetchone()
            #check if there is a question in quiz_questions
            question_check_string = "SELECT id from quiz_questions WHERE user_id = " + str(user_id) + " and lecture_video_id=" + str(video_id)
            question_check_string = str(question_check_string)#may be unnecessary
            question_check = db.execute(question_check_string).fetchone()

            if(question_check):
                qcheck = 1
            else:
                qcheck = 0
            
            #if qcheck is 1, load the questions from quiz_questions table
            #else, select all the questions and insert them into quiz_questions table

            questions = db.execute("SELECT * FROM questions WHERE lecture_video_id='%s'" % video_id).fetchall()
            
            number_of_questions = video.number_of_questions

            while(j <= number_of_questions):
                query_string = "SELECT * FROM questions WHERE lecture_video_id = " + str(video_id) + " AND question_number = " + str(j)

                question = db.execute(query_string).fetchall()


                num_q = len(question)
                if(num_q > 1):

                
                    if(qcheck == 0):
                        rand_num = random.randint(1,num_q)
                        random_question = question[rand_num - 1]

                        question_array.append(random_question)
                        question_id = random_question.id


                        username = db.execute("INSERT INTO quiz_questions (lecture_video_id, user_id, question_id, question_num, answer_provided) VALUES (:lecture_video_id, :uid, :question_id, :question_num, 'answer_provided')", {"lecture_video_id": video_id,  "uid": user_id, "question_id": question_id, "question_num": j})
                        db.commit()
                        test_array = [question_id] 

                    else:
                        #get the question and use it
                        query_string = "SELECT * FROM quiz_questions WHERE user_id = " + str(user_id) + " AND lecture_video_id = " + str(video_id) + " AND question_num = " + str(j)
                        stored_question = db.execute(query_string).fetchone()
                        question_id = stored_question.question_id
                        
                        test_array2.append(stored_question)
                        test_array.append(question)


                        question2 = db.execute("SELECT * FROM questions WHERE id='%s'" % question_id).fetchone()
                        test_array2.append(question2)
                        question_array.append(question2)

                

                else:

                    question_array.append(question[0])

                j = j + 1
            for i in question_array:
                question = i[1]
                answer = i[2]
                choices = i[3]

                choices_array = choices.split(';;;&&&')

                qa_arr.append(question)
                qa_arr.append(answer)
                qa_arr.append(choices_array)
                question_array_display.append(qa_arr)
                qa_arr = []
                test_array2.append(qa_arr)
                
            time_to_display_score = 0
    quiz_score = round(quiz_score, 2)
    if logged_in:
        return render_template("quiz.html", supplied_answer=supplied_answer, real_answer=real_answer, test=test, video_id=video_id, video=video, questions=questions, logged_in=logged_in, question_array=question_array, quizzes=quizzes, time_to_display_score=time_to_display_score, quiz_score=quiz_score, test_array=test_array, test_array2=test_array2, question_array_display=question_array_display, qcheck=qcheck, final_question_vs_answer=final_question_vs_answer)

@app.route("/login", methods=["GET", "POST"])
def login():

#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        investoraccess = 1
    else:
        investoraccess = 0

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "login", "unixtime": now})
    db.commit()
#### END INVESTOR SECTION ####

    message = "Test message"
    users = "Test username"
    logged_in = 0
    basicsecurity = session.get("basicsecurity")
    if session.get("username") is None:
        session["username"] = []
        session["logged_in"] = 0
        logged_in = 0
    elif (session["logged_in"] == 1):
        logged_in = 1
    else:
        session["logged_in"] = 0
        logged_in = 0

    if request.method == "POST":
        uname = request.form.get("username")
        password = request.form.get("password")
        users = db.execute("SELECT * FROM users WHERE username='%s'" % uname).fetchall()
        db.commit()
        if(users):
            message = "Username there"
            if(password == users[0][2]):
                if(basicsecurity == "SET"):
                    message = "Welcome "
                    session["username"].append(uname)
                    session["user_id"] = users[0][0] #happens to contain the id
                    session["logged_in"] = 1
                    logged_in = 1
            else:
                message = "Wrong password"
        else:
            message = "Unrecognized username"

    if investoraccess:    
        return render_template("login.html", message=message, users=users, logged_in=logged_in, session=session)

@app.route("/logout")
def logout():

#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        investoraccess = 1
    else:
        investoraccess = 0

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "logout", "unixtime": now})
    db.commit()
#### END INVESTOR SECTION ####

    if session.get("username") is None:
        session["username"] = []
        session["logged_in"] = 0
        logged_in = 0
    elif (session["logged_in"] == 1):
        session["logged_in"] = 0
        session["username"] = []
        logged_in = 0
        logged_out = 1
    else:
        session["logged_in"] = 0
        logged_in = 0

    if investoraccess: 
        return render_template("logout.html", session=session, logged_in=logged_in, logged_out=logged_out)

@app.route("/register", methods=["GET", "POST"])
def register():
    registered = ""
    message = ""
     
    basicsecurity = session.get("basicsecurity")


#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    #investorid = 1 
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        basicsecurity = session.get("basicsecurity")
    else:
        basicsecurity = "UNSET"

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "register", "unixtime": now})
    db.commit()
#### END INVESTOR SECTION ####


    if(basicsecurity == "SET"):
    
        registered = 0
        message = "Use email for username, and create account"
        if request.method == "POST":
            uname = request.form.get("username")
            password = request.form.get("password")
            users = db.execute("SELECT * FROM users WHERE username='%s'" % uname).fetchall()
            db.commit()
            if(users):
                message = "Email already in the system"
            else:
                registered = 1
                username = db.execute("INSERT INTO users (username, pwd, created_on) VALUES (:uname, :password, CURRENT_TIMESTAMP)", {"uname": uname, "password": password})
                db.commit()
                message = "Successfully registered"

    return render_template("register.html", registered=registered, message=message)


@app.route("/search", methods=['POST'])
def search():

#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    #investorid = 1 
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        basicsecurity = session.get("basicsecurity")
    else:
        basicsecurity = "UNSET"

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "search", "unixtime": now})
    db.commit()
#### INVESTOR SECTION ###

    users = ""
    videos = ""
    if request.method == "POST":
        searchstring = request.form.get("searchstring")
        select = request.form.get("srch")
        searchstring = "%" + searchstring + "%"
        if(select == "user"):
            users = db.execute("SELECT * FROM users WHERE username LIKE :id", {"id": searchstring}).fetchall()
        else:
            videos = db.execute("SELECT * FROM lecture_video WHERE video_title LIKE :id AND deleted = FALSE", {"id": searchstring}).fetchall()
        db.commit()

    if basicsecurity:
        return render_template("search.html", videos=videos, users=users, select=select, searchstring=searchstring)



@app.route("/add_video", methods=["GET", "POST"])
def add_video():
#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    #investorid = 1 
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        basicsecurity = session.get("basicsecurity")
    else:
        basicsecurity = "UNSET"

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "add_video", "unixtime": now})
    db.commit()
    require_approval = ""
#### INVESTOR SECTION ###

    inserted = 0
    proceed = 0
    message = " "
    if request.method == "POST":
        title = request.form.get("title") 
        description = request.form.get("description")
        num_q = request.form.get("num_q")
        video_address = request.form.get("video_address")
        require_approval = request.form.get("requireapproval")

        if(len(title) > 1):
            proceed = 1
        else:
            message = "Your title is too short."

        if(len(description) < 5):
            proceed = 0
            message = "Your description is too short"

        if(int(num_q) > 25):
            proceed = 0
            message = "Too many questions"

        if(int(num_q) < 0):
            proceed = 0
            message = "Something is wrong with number of questions"

        if(len(video_address) < 4):
            proceed = 0
            message = "Video address is too short"


    uname = session["username"]
    uname = uname[0]    
    user = db.execute("SELECT * FROM users WHERE username='%s'" % uname).fetchone()
    db.commit()
    user_id = user.id
   
    val = ""
    new_video_id = 0
    ro = 0

    if(proceed):
        if(require_approval == "requireapproval"):
            require_approval = True
        else:
            require_approval = False

        val = db.execute("INSERT INTO lecture_video (user_id, video_address, video_title, number_of_questions, description, created_on, preapprove) VALUES (:user_id, :video_address, :title, :number_of_questions, :description, CURRENT_TIMESTAMP, :preapprove) RETURNING id", {"user_id": user_id, "video_address": video_address, "title": title, "number_of_questions": num_q, "description": description, "preapprove": require_approval})
        
        db.commit()
        
        ro = val.fetchone()
        ro = ro.id 
        inserted = 1

    if basicsecurity:
        return render_template("add_video.html", ro=ro, val=val, message=message, inserted=inserted, proceed=proceed, require_approval=require_approval)


@app.route("/add_questions/<int:video_id>", methods=['POST', 'GET'])
def add_questions(video_id):

#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        investoraccess = 1
    else:
        investoraccess = 0

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "add_questions", "unixtime": now})
    db.commit()
#### END INVESTOR SECTION ####

    inserted = 0
    proceed = 0
    message = ""
    val2 = 0
    answer1 = ""
    answer2 = ""
    answers = ""
    val = db.execute("SELECT * FROM lecture_video WHERE id = :video_id", {"video_id": video_id}).fetchone()
    db.commit()

    num_questions = val.number_of_questions
    if request.method == "POST":
        proceed = 1
        answer = 0

        for i in range(1,num_questions+1):
            questionnum = "question" + str(i)
            question = request.form.get(questionnum)
        
            ans_string = "answers" + str(i) 
            answer = request.form.get(ans_string)


            choice1 = request.form.get("q" + str(i) + "choice1")
            choice2 = request.form.get("q" + str(i) + "choice2")
            choice3 = request.form.get("q" + str(i) + "choice3")
            choice4 = request.form.get("q" + str(i) + "choice4")
            choice5 = request.form.get("q" + str(i) + "choice5")
 
            choices = choice1 + ";;;&&&" + choice2 + ";;;&&&" + choice3 + ";;;&&&" + choice4 + ";;;&&&" + choice5
        
            val2 = db.execute("INSERT INTO questions (question, answer, choices, created_on, lecture_video_id, question_number) VALUES (:question, :answer, :choices, CURRENT_TIMESTAMP, :lecture_video_id, :question_number)", {"question": question, "answer": answer, "choices": choices, "lecture_video_id": video_id, "question_number": i})
            db.commit()
            if(val2):
                inserted = 1
            else:
                message="No insert"

        if(inserted):
            val2 = db.execute("UPDATE lecture_video SET completed = 1 WHERE id = %s" % video_id)
            db.commit()
    if investoraccess:
        return render_template("add_questions.html", val2=val2, message=message, num_questions=num_questions, inserted=inserted, video_id=video_id, proceed=proceed) 


@app.route("/batch/<int:video_id>", methods=['POST', 'GET'])
def batch(video_id):

#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        investoraccess = 1
    else:
        investoraccess = 0

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "batch" + str(video_id), "unixtime": now})
    db.commit()
#### END INVESTOR SECTION ####

    proceed = 0
    inserted = 0
    inner_array = []
    batch_array = []
    message = ""
    test_array = []
    integrity = 0
    integrity_msg = ""
    lev2_batch_array = []
    lev3_batch_array = []
    lev4_batch_array = []
    test_array2 = []
    qac_array = []
    final_array = []

    j = 1
    i = 1
    if request.method == "POST":
        proceed = 1
         
        batch = request.form.get("batch_questions")
        #integrity check
        batch_array = batch.split("1***###1")
        #integrity check
        if(batch_array[0] == ''):
            integrity = 1
        else:
            integrity_msg = "batch_array[0] doesn't contain ''"
        
        
        if(batch_array[-1] == ''):
            integrity = 1
        else:
            integrity = 0
            integrity_msg = "batch_array[-1] doesn't contain ''"

        if(integrity):
            batch_array.pop()
            del batch_array[0]
            integrity = 0
            for lev2 in batch_array:
                lev2_batch_array = lev2.split("2!!!%%%2")
              
                
                lev2_batch_array[0] = lev2_batch_array[0].strip()
                if(lev2_batch_array[0] == ''):
                    integrity = 1
                else:
                    integrity_msg = "lev2_batch_array[0] doesn't contain ''"

                lev2_batch_array[-1] = lev2_batch_array[-1].strip()
                if(lev2_batch_array[-1] == ''):
                    integrity = 1
                else:
                    integrity = 0
                    integrity_msg = "lev2_batch_array[-1] doesn't contain ''"
                
                lev2_batch_array.pop()
                del lev2_batch_array[0]
                lev3_batch_array = lev2_batch_array[0].split("3$$$@@3")
                
                integrity = 0
                if(int(lev3_batch_array[0]) == j):
                    integrity = 1
                else:
                    integrity = 0
                    integrity_msg = "When j was " + str(j) + " lev3_batch_array[0] didn't match j"
                lev3_batch_array[-1] = lev3_batch_array[-1].strip()
                
                if(integrity):
                    if(lev3_batch_array[-1] == ''):
                        integrity = 1
                    else:
                        integrity = 0
                        integrity_msg = "lev3_batch_array[-1] doesn't contain ''"

                    if(integrity):
                        lev3_batch_array.pop()
                        del lev3_batch_array[0]
                        integrity = 0
                
                        for lev4 in lev3_batch_array:
                            lev4_batch_array = lev4.split("4***$$$4")
                            integrity = 1

                            if(integrity): 
                                integrity = 0
                        
                                del lev4_batch_array[0]
                                lev4_batch_array.pop()
                                test_array2.append(lev4_batch_array)
                                
                                question = lev4_batch_array[0].strip()
                                start = question.find("=")
                                
                                question_for_db_insert = question[start+1:]
                                qac_array.append(question_for_db_insert)

                                answer = lev4_batch_array[1].strip()
                                start = answer.find("=")
                                answer_for_db_insert = answer[start+1:] 
                                qac_array.append(answer_for_db_insert)
                                
                                choices = lev4_batch_array[2].strip()
                                start = choices.find("=")
                                choices_for_db_insert = choices[start+1:]
                                qac_array.append(choices_for_db_insert)
                                qac_array.append(j)
                                final_array.append(qac_array)
                                qac_array = []


                j = j + 1



            
        comm='''
        for i in batch_array:
            inner_array = i.split("!!!%%%")
                for k in qa_pairs_array:
                    final_pairs = k.split("***$$$")
                    question_string = final_pairs[0]
                    answer_string = final_pairs[1]
                    choices_string = final_pairs[2]
                    
                    test_array[j][h] = final_pairs
            '''

        test_array = lev4_batch_array
        for i in final_array:
            question = i[0]
            answer = i[1]
            choices = i[2]
            question_number = i[3]
            result = db.execute("INSERT INTO questions (question, answer, choices, created_on, lecture_video_id, question_number) VALUES (:question, :answer, :choices,  CURRENT_TIMESTAMP, :lecture_video_id, :question_number)", {"question": question, "answer": answer, "choices": choices, "lecture_video_id": video_id, "question_number": question_number})
            db.commit()
            inserted = 1
            db.execute("UPDATE lecture_video SET completed = 1 WHERE id = %s" % video_id)
    if investoraccess:
        return render_template("batch.html", video_id=video_id, proceed=proceed, message=message, test_array=test_array, j = j, integrity_msg=integrity_msg, test_array2=test_array2, final_array=final_array, inserted=inserted)


@app.route("/usr/<username>")
def usr(username):

#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "usr" + str(username), "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####


	user = db.execute("SELECT * FROM users WHERE username='%s'" % username).fetchone()
	user_id = user.id
	logged_in_and_not_user_himself = 0
	if session.get("user_id") is not None:
		session_user_id = session["user_id"]
		if session_user_id != user_id:
			logged_in_and_not_user_himself = 1

	videos = db.execute("SELECT * FROM lecture_video WHERE user_id='%s'" % user_id).fetchall()
	if investoraccess:
		return render_template("usr.html", logged_in_and_not_user_himself=logged_in_and_not_user_himself, username=username, user=user, videos=videos, user_id=user_id)


@app.route("/quiz_results/<int:video_id>/<int:display_user_id>")
def quiz_results(video_id, display_user_id):

#### INVESTOR SECTION ###
    investor_id = session.get("investorid")
    expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
    firstaccess = expiration.firstaccess
    timelimit = expiration.timelimit
    now = time.time()

    if(now < (firstaccess + timelimit)):
        investoraccess = 1
    else:
        investoraccess = 0

    ip_address = str(request.remote_addr)
    submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "quiz_results" + str(video_id), "unixtime": now})
    db.commit()
#### END INVESTOR SECTION ####

    logged_in = 0 
    if session.get("username") is None:
        session["username"] = []
        session["logged_in"] = 0
        logged_in = 0
    elif (session["logged_in"] == 1):
        logged_in = 1    
        user_id = session["user_id"]
    else:
        session["logged_in"] = 0
        logged_in = 0
    j = 1
    test_array = []
    test_array2 = []
    final_display_arr = []
    final_question_vs_answer = []

    video = db.execute("SELECT * FROM lecture_video WHERE id='%s'" % video_id).fetchone()

    number_of_questions = video.number_of_questions

    while(j <= number_of_questions):
            
        query_string = "SELECT * FROM questions WHERE lecture_video_id = " + str(video_id) + " AND question_number = " + str(j)

        question = db.execute(query_string).fetchall() 
                
        num_q = len(question)
        if(num_q > 1):
            query_string = "SELECT * FROM quiz_questions WHERE user_id = " + str(display_user_id) + " AND lecture_video_id = " + str(video_id) + " AND question_num = " + str(j)
            quiz_question = db.execute(query_string).fetchone()
            question_id = quiz_question.question_id
            question_stored = db.execute("SELECT * FROM questions WHERE id = '%s'" % question_id).fetchone()
            choices = question_stored.choices
            num_actual_answer = question_stored.answer#just the number
            display_question = question_stored.question
        else:
            num_actual_answer = question[0][2]#the answer column - just the number
            display_question = question[0][1]
            question_id = question[0][0]#this accesses the id if there is only one question
            choices = question[0][3]
        final_display_arr.append(display_question)
         
        query_string = "SELECT * FROM answers WHERE lecture_video_id = " + str(video_id) + " AND question_id = " + str(question_id) + " AND user_id = " + str(display_user_id)

        answer = db.execute(query_string).fetchone()
        num_provided_answer = answer.answer

 
        choices_array = choices.split(';;;&&&')

        str_provided_answer = choices_array[int(num_provided_answer) - 1]
        str_actual_answer = choices_array[int(num_actual_answer) - 1]

        final_display_arr.append(str_provided_answer)

        final_display_arr.append(str_actual_answer)

        if(num_provided_answer == num_actual_answer):
            final_display_arr.append("CORRECT")
        else:
            final_display_arr.append("INCORRECT")

        final_display_arr.append(j)
        final_question_vs_answer.append(final_display_arr)

        final_display_arr = []
        j = j + 1


    query_string = "SELECT * FROM quiz_grades WHERE user_id = " + str(display_user_id) + " AND video_id = " + str(video_id)
    quiz_question = db.execute(query_string).fetchone()
    num_correct = quiz_question.num_correct
    num_total_questions = quiz_question.num_total_questions
    quiz_score = 100 * (num_correct / num_total_questions)
    quiz_score = round(quiz_score ,2)
    result = db.execute("SELECT username FROM users WHERE id = %s" % display_user_id).fetchone()
    display_username = result.username

    if investoraccess:
        return render_template("quiz_results.html", video_id=video_id, test_array=test_array, j=j, test_array2=test_array2, final_question_vs_answer=final_question_vs_answer, logged_in=logged_in, quiz_score=quiz_score, user_id=user_id, display_user_id=display_user_id, display_username=display_username)

@app.route("/request_friend/<int:user_id>")
def request_friend(user_id):
	
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "request_friend", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####

	requester_id = session["user_id"]
	requested_id = user_id	
	proceed = 0

	requested_already_check = db.execute("SELECT * FROM friends WHERE time_denied IS NULL AND time_deleted IS NULL AND ((user_id_requester = :user_id_requester AND user_id_accepter = :user_id_accepter) OR (user_id_accepter = :user_id_requester AND user_id_requester = :user_id_accepter))", {"user_id_requester": requester_id, "user_id_accepter": requested_id}).fetchone()
	db.commit()

	if(requested_already_check):
		message = "You have already requested to be this user's friend or you're already friends"
	else:
		proceed = 1
	
	now = time.time()
	if(proceed):
		submitted = db.execute("INSERT INTO friends (user_id_requester, user_id_accepter, time_requested) VALUES (:user_id_requester, :user_id_accepter, :time_requested)", {"user_id_requester": requester_id, "user_id_accepter": requested_id, "time_requested": now})
		db.commit()
		message = "Your friend request has been sent"
	if investoraccess:	
		return render_template("request_friend.html", user_id=user_id, requester_id=requester_id, message=message)

@app.route("/notifications")
def notifications():
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "notifications", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####

	user_id = session["user_id"]
	
	friend_requests = db.execute("SELECT * FROM friends LEFT JOIN users ON friends.user_id_requester = users.id WHERE friends.user_id_accepter = :user_id AND time_accepted IS NULL AND time_denied IS NULL AND time_deleted IS NULL", {"user_id": user_id}).fetchall()
	db.commit()

	video_requests = db.execute("SELECT * FROM student_request INNER JOIN users ON student_request.student_id = users.id WHERE instructor_id = %s AND permission = False ORDER BY date_requested DESC" % user_id).fetchall()
	db.commit()

	new_messages = db.execute("SELECT * FROM messages WHERE user_id_receiver = %s AND time_viewed IS NULL" % user_id).fetchall()
	num_new_messages = len(new_messages)
	if investoraccess:	
		return render_template("notifications.html", requests=video_requests, friend_requests=friend_requests, num_new_messages=num_new_messages)

@app.route("/accept_deny_friend/<int:user_id>/<int:accept>")
def accept_deny_friend(user_id, accept):

#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "accept_deny_friend", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####

	now = time.time()
	requester_id = user_id
	accepter_id = session["user_id"]
	if(accept):
		db.execute("UPDATE friends SET time_accepted = :unixtime WHERE user_id_requester = :requester_id AND user_id_accepter = :accepter_id", {"unixtime": now, "requester_id": requester_id, "accepter_id": accepter_id})
		db.commit()
	else:
		db.execute("UPDATE friends SET time_denied = :unixtime WHERE user_id_requester = :requester_id AND user_id_accepter = :accepter_id", {"unixtime": now, "requester_id": requester_id, "accepter_id": accepter_id})
		db.commit()	
	if investoraccess:
		return render_template("accept_deny_friend.html", accepted=accept, user_id=user_id)

@app.route("/account")
def account():
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "account", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####

	user_id = session["user_id"]
	num_friends = 0
	num_new_messages = 0
	friends1 = db.execute("SELECT * FROM friends LEFT JOIN users ON friends.user_id_accepter = users.id WHERE friends.user_id_requester = :user_id AND time_deleted IS NULL AND time_denied IS NULL AND time_accepted IS NOT NULL", {"user_id": user_id}).fetchall()
	db.commit()
	num_friends = len(friends1)
	
	friends2 = db.execute("SELECT * FROM friends LEFT JOIN users ON friends.user_id_requester = users.id WHERE friends.user_id_accepter = :user_id AND time_deleted IS NULL AND time_denied IS NULL AND time_accepted IS NOT NULL", {"user_id": user_id}).fetchall()
	db.commit()
	num_friends = num_friends + len(friends2)
	
	#compute number of new messages

	messages = db.execute("SELECT * FROM messages WHERE user_id_receiver = :user_id AND time_viewed IS NULL", {"user_id": user_id}).fetchall()
	db.commit()

	num_new_messages = len(messages)
	if investoraccess:
		return render_template("account.html", friends1=friends1, friends2=friends2, user_id=user_id, num_friends=num_friends, num_new_messages=num_new_messages)

@app.route("/delete_friend/<int:user_id>")
def delete_friend(user_id):
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "delete_friend", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####

	deleting_user_id = session["user_id"]
	other_user_id = user_id
	now = time.time()
	db.execute("UPDATE friends SET time_deleted = :unixtime WHERE user_id_requester = :deleting_user_id AND user_id_accepter = :other_user_id", {"unixtime": now, "deleting_user_id": deleting_user_id, "other_user_id": other_user_id})
	db.commit()

	db.execute("UPDATE friends SET time_deleted = :unixtime WHERE user_id_accepter = :deleting_user_id AND user_id_requester = :other_user_id", {"unixtime": now, "deleting_user_id": deleting_user_id, "other_user_id": other_user_id})
	db.commit()

	if investoraccess:	
		return render_template("delete_friend.html")

@app.route("/friends")
def friends():
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "friends", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####

	user_id = session["user_id"]
	num_friends = 0
	msg = ""
	
	friends1 = db.execute("SELECT * FROM friends LEFT JOIN users ON friends.user_id_accepter = users.id WHERE friends.user_id_requester = :user_id AND time_deleted IS NULL AND time_denied IS NULL AND time_accepted IS NOT NULL", {"user_id": user_id}).fetchall()
	db.commit()
	num_friends = len(friends1)

	friends2 = db.execute("SELECT * FROM friends LEFT JOIN users ON friends.user_id_requester = users.id WHERE friends.user_id_accepter = :user_id AND time_deleted IS NULL AND time_denied IS NULL AND time_accepted IS NOT NULL", {"user_id": user_id}).fetchall()
	db.commit()
	num_friends = num_friends + len(friends2)

	if(num_friends == 0):
		msg = "You have no friends."
	if investoraccess:
		return render_template("friends.html", friends1=friends1, friends2=friends2, num_friends=num_friends, msg=msg)

@app.route("/messages")
def messages():
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####

	user_id = session["user_id"]
	result = db.execute("SELECT DISTINCT ON (user_id_receiver) user_id_sender, user_id_receiver, time_sent FROM messages WHERE user_id_sender = :user_id LIMIT 50", {"user_id": user_id}).fetchall()
	db.commit()

	time_sent_int = 0
	users_communicated_with = []
	for i in result:
		user_communicated_with = i[1]
		time_sent = db.execute("SELECT time_sent FROM messages WHERE user_id_receiver = :user_communicated_with AND user_id_sender = :user_id ORDER BY time_sent DESC LIMIT 1", {"user_communicated_with": user_communicated_with, "user_id": user_id})
		db.commit()

		for j in time_sent:
			time_sent_int = j[0]

		users_communicated_with.append([user_communicated_with, time_sent_int])

	

	result2 = db.execute("SELECT DISTINCT ON (user_id_sender) user_id_sender, user_id_receiver, time_sent FROM messages WHERE user_id_receiver = :user_id LIMIT 50", {"user_id": user_id}).fetchall()
	db.commit()

	other_users_communicated_with = []

	for i in result2:
                user_communicated_with = i[0]
                time_sent = db.execute("SELECT time_sent FROM messages WHERE user_id_receiver = :user_id AND user_id_sender = :user_communicated_with ORDER BY time_sent DESC LIMIT 1", {"user_communicated_with": user_communicated_with, "user_id": user_id})
                db.commit()

                for j in time_sent:
                        time_sent_int = j[0]

                other_users_communicated_with.append([user_communicated_with, time_sent_int])

	
	users_communicated_with = users_communicated_with + other_users_communicated_with

	j = 1
	users_array_final = []
	display_array_final = []
	users_array_with_time = []
	for i in users_communicated_with:
		user_num = i[0]
		this_index_time = i[1]
		if user_num in users_array_final:
			#compare the times and select the higher number
			index_num_to_lookup = 0
			time_user_pair = users_array_with_time[index_num_to_lookup]
			earlier_time = time_user_pair[1]
			if(this_index_time > earlier_time):
				#find the earlier entry and update the time
				for idx, j in enumerate(display_array_final):
					if j[0] == user_num:
					
						display_array_final[idx][2] = this_index_time
								
		else:
			users_array_final.append(user_num)
			users_array_with_time.append([user_num, this_index_time])
			user = db.execute("SELECT username FROM users WHERE id='%s'" % user_num).fetchone()
			display_array_final.append([user_num, user[0], this_index_time])
	
	display_array_final_sorted = sorted(display_array_final, key=lambda x : x[2])

	for idx, i in enumerate(display_array_final_sorted):
		friend_user_id = i[0]
		messages = db.execute("SELECT * FROM messages WHERE (user_id_sender = :friend_user_id AND user_id_receiver = :user_id) AND time_viewed IS NULL", {"user_id": user_id, "friend_user_id": friend_user_id}).fetchall()
		db.commit()

		num_new_messages = len(messages)
		
		display_array_final_sorted[idx].append(num_new_messages)
	if investoraccess:
		return render_template("messages.html", result=result, result2=result2, merged=display_array_final_sorted, display_array_final=display_array_final_sorted)

@app.route("/send_message/<int:to_user>")
def send_message(to_user):
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####

	user_id_sender = session["user_id"]
	result = db.execute("SELECT username FROM users where id = :to_user", {"to_user": to_user}).fetchone()
	db.commit()

	result2 = db.execute("select * from messages left join users on users.id = user_id_sender where (user_id_sender = :user_id_sender and user_id_receiver = :to_user) OR (user_id_sender = :to_user and user_id_receiver = :user_id_sender) ORDER BY time_sent ASC", {"user_id_sender": user_id_sender,  "to_user": to_user}).fetchall()
	db.commit()
	
	messages = "<br>"
	for i in result2:
		seconds = i.time_sent
		timestamp = time.ctime(seconds)	
		message_plus_formatting = i.username + ": " + i.message + "<br> Msg sent " + timestamp  + "<br><br>"
		messages = messages + message_plus_formatting


	username_to = result.username

	now = time.time()
	viewed_update = db.execute("UPDATE messages set time_viewed = :now WHERE (user_id_sender = :to_user AND user_id_receiver = :user_id_sender)", {"user_id_sender": user_id_sender,  "to_user": to_user, "now": now})
	db.commit()

	if investoraccess:
		return render_template("send_message.html", messages=messages, result2=result2, to_user=to_user, username_to=username_to, message_page=1, page_owner=user_id_sender)

@app.route("/profile/<int:user_id>", methods=['POST', 'GET'])
def profile(user_id):
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	owner_id = session["user_id"]
	logged_in = 0
	if user_id == owner_id:
		logged_in = 1
	result = db.execute("SELECT username FROM users WHERE id = %s" % user_id).fetchone()
	db.commit()
	result2 = db.execute("SELECT profile FROM user_profile WHERE user_id = %s" % user_id).fetchone()
	db.commit()
	profile = result2.profile	
	username = result.username

	if investoraccess:
		return render_template("profile.html", profile=profile, logged_in=logged_in, user_id=user_id, username=username)

@app.route("/edit_profile", methods=['POST', 'GET'])
def edit_profile():
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	user_id = session["user_id"]
	profile = ""
	updating = 0
	if request.method == "POST":
		updated_profile = request.form.get("profile")
		updating = 1
		db.execute("UPDATE user_profile SET profile = :updated_profile WHERE user_id = :user_id", {"updated_profile": updated_profile, "user_id": user_id})
		db.commit()
	else:
		result = db.execute("SELECT profile FROM user_profile WHERE user_id = %s" % user_id).fetchone()
		db.commit()
		profile = result.profile

	if investoraccess:	
		return render_template("edit_profile.html", user_id=user_id, profile=profile, updating=updating)


@app.route("/reply_to_comment/<int:commentnum>", methods=['POST', 'GET'])
def reply_to_comment(commentnum):
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	posting = 0
	video_id = 0
	reply_page = 0 #triggers javascript to update other users' screens with the reply using websocket
	if request.method == "POST":
		user_id = session["user_id"]
		reply = request.form.get("reply")
		seconds = time.time()
		submitted = db.execute("INSERT INTO video_comment_replies (video_comment_id, replying_user, created_on, reply) VALUES (:commentnum, :user_id, :seconds, :reply)", {"commentnum": commentnum, "user_id": user_id, "seconds": seconds, "reply": reply})
		db.commit()
		posting = 1
		result = db.execute("SELECT video_id FROM video_comments WHERE id = %s" % commentnum).fetchone()
		db.commit()
		video_id = result.video_id
		reply_page = 1
		
	if investoraccess:
		return render_template("reply_to_comment.html", video_id = video_id, commentnum = commentnum, posting = posting, reply_page = reply_page)

@app.route("/comments", methods=['POST', 'GET'])
def comments():
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	if investoraccess:
		return render_template("comments.html")

@app.route("/view_batch_code", methods=['POST', 'GET'])
def view_batch_code():
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	if investoraccess:
		return render_template("view_batch_code.html")

@app.route("/view_batch_code_generator", methods=['POST', 'GET'])
def view_batch_code_generator():
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	if investoraccess:
		return render_template("view_batch_code_generator.html")


@app.route("/wall/<int:wall_owner>", methods=['POST', 'GET'])
def wall(wall_owner):
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	user_id = session["user_id"]
	your_wall = 0
	session["last_wall"] = wall_owner
	if wall_owner == user_id:
		your_wall = 1
	
	seconds = time.time()
	
	if your_wall:
		friends = db.execute("SELECT * FROM friends where user_id_requester = :user_id OR user_id_accepter = :user_id AND time_deleted IS NULL AND time_denied IS NULL", {"user_id": user_id})
		wall_posts_search_string = "user_id = " + str(user_id)
		comments_search_string = str(user_id)
		for i in friends:
			if i.user_id_accepter == user_id:
				id_to_search_for = i.user_id_requester
			else:
				id_to_search_for = i.user_id_accepter
			comments_search_string = comments_search_string + " OR posting_user = " + str(id_to_search_for)  		
			wall_posts_search_string = wall_posts_search_string + "OR user_id = " + str(id_to_search_for)


		result = db.execute("SELECT wall_posts.*, users.username FROM wall_posts LEFT JOIN users ON users.id = wall_posts.user_id WHERE (%s) ORDER BY time_created DESC LIMIT 20" % wall_posts_search_string).fetchall()
		db.commit()

		wall_posts_array = []
		for i in result:
			most_recent_post = i.time_created
			wall_post_id = i.id

			result2 = db.execute("SELECT *, users.username FROM wall_post_replies LEFT JOIN users ON users.id = wall_post_replies.user_id WHERE wall_post_id = :wall_post_id", {"wall_post_id": wall_post_id}).fetchall()
	
			replies_array = []
			for j in result2:
				replies_array.append([j.id, j.user_id, j.time_created, j.content, j.username])
				if most_recent_post < j.time_created:
					most_recent_post = j.time_created
				
			wall_posts_array.append([i.id, i.user_id, i.time_created, i.content, i.username, replies_array, "wall post", most_recent_post])


		video_comments = db.execute("SELECT * FROM video_comments LEFT JOIN users ON users.id = video_comments.posting_user LEFT JOIN lecture_video ON lecture_video.id = video_comments.video_id WHERE (posting_user = %s) ORDER BY video_comments.created_on DESC LIMIT 20" % comments_search_string).fetchall()

		for i in video_comments:
			most_recent_post = i[3]
			created_on = i[3]
			comment_id = i[0]	

			result2 = db.execute("SELECT video_comment_replies.*, users.username FROM video_comment_replies LEFT JOIN users ON users.id = video_comment_replies.replying_user WHERE video_comment_replies.video_comment_id = %s ORDER BY created_on ASC LIMIT 10" % comment_id)

			replies_array = [] 
			for j in result2:
				replies_array.append([j.id, j.replying_user, j.created_on, j.reply, j.username])
				if most_recent_post < j.created_on:
                                        most_recent_post = j.created_on


			wall_posts_array.append([i.id, i.posting_user, created_on, i.comment, i.username, replies_array, "video_comment", most_recent_post, i.video_id, i.video_title]) 
	
		def takeSecond(elem):
			return elem[7]

		wall_posts_array.sort(key=takeSecond, reverse=True)
		wall_posts_array = wall_posts_array[:20]
	else:
		result = db.execute("SELECT wall_posts.*, users.username FROM wall_posts LEFT JOIN users ON users.id = wall_posts.user_id WHERE user_id = %s ORDER BY time_created DESC LIMIT 20" % wall_owner).fetchall()
		
		wall_posts_array = []
		for i in result:
			wall_post_id = i.id
			replies_array = []
			result2 = db.execute("SELECT *, users.username FROM wall_post_replies LEFT JOIN users ON users.id = wall_post_replies.user_id WHERE wall_post_id = :wall_post_id", {"wall_post_id": wall_post_id}).fetchall()	
			
			for j in result2:
				replies_array.append([j.id, j.user_id, j.time_created, j.content, j.username])

			wall_posts_array.append([i.id, i.user_id, i.time_created, i.content, i.username, replies_array])	
		
	
	if investoraccess:
		return render_template("wall.html", wall_data=result, wall_page=1, user_id=user_id, wall_posts_array=wall_posts_array, wall_owner=wall_owner)


@app.route("/wall_post_replies/<int:wall_post_num>", methods=['POST', 'GET'])
def wall_post_replies(wall_post_num):
#### INVESTOR SECTION ###
	investor_id = session.get("investorid")
	expiration = db.execute("SELECT timelimit, firstaccess FROM investorinfo WHERE id = :investorid", {"investorid": investor_id}).fetchone()
	firstaccess = expiration.firstaccess
	timelimit = expiration.timelimit
	now = time.time()

	if(now < (firstaccess + timelimit)):
		investoraccess = 1
	else:
		investoraccess = 0

	ip_address = str(request.remote_addr)
	submitted = db.execute("INSERT INTO investorpage (investor_id, ip_address, page, time) VALUES (:investor_id, :ip_address, :page, :unixtime)", {"investor_id": investor_id, "ip_address": ip_address, "page": "messages", "unixtime": now})
	db.commit()
#### END INVESTOR SECTION ####
	posting = 0
	user_id = session["user_id"]
	last_wall = session["last_wall"]
	reply_wall_page = 0
	if request.method == "POST":
		content = request.form.get("reply")
		seconds = time.time()
		submitted = db.execute("INSERT INTO wall_post_replies (wall_post_id, user_id, time_created, content) VALUES (:wall_post_id, :user_id, :seconds, :content)", {"wall_post_id": wall_post_num, "user_id": user_id, "seconds": seconds, "content": content})
		db.commit()
		posting = 1
		reply_wall_page = 1

	if investoraccess:
		return render_template("wall_post_replies.html", wall_post_num = wall_post_num, posting = posting, user_id=user_id, last_wall=last_wall, reply_wall_page = reply_wall_page)

@app.route("/admin", methods=['POST', 'GET'])
def admin():
	now = time.time()
	if session.get("admin_logged_in") is None:	
		session['admin_logged_in'] = 0
	last_login = db.execute("SELECT time_logged_in FROM admin_logins ORDER BY time_logged_in DESC LIMIT 1").fetchone()
	result = "unset"
	if request.method == "POST":
		password = request.form.get("password")
		result = db.execute("SELECT password FROM admin WHERE id = 1").fetchone()
		password_from_db = result.password
		if password == password_from_db:
			session['admin_logged_in'] = 1
			ip_address = str(request.remote_addr)
			logged_in = db.execute("INSERT INTO admin_logins (time_logged_in, ip_logged_in) VALUES (:now, :ip_address)", {"now": now, "ip_address": ip_address})
			db.commit() 
	logged_in = session['admin_logged_in']

	return render_template("admin.html", logged_in=logged_in, result=result, last_login=last_login.time_logged_in)

@app.route("/admin_logout")
def admin_logout():
	session['admin_logged_in'] = 0
	return render_template("admin_logout.html")

@app.route("/investors", methods=['POST', 'GET'])
def investors():
	result = db.execute("SELECT id, name FROM investorinfo WHERE deleted = FALSE").fetchall()

	return render_template("investors.html", result=result)

@app.route("/delete_investor/<int:investor_id>", methods=['GET'])
def delete_investor(investor_id):
	submitted = db.execute("UPDATE investorinfo SET deleted = TRUE WHERE id = %s" % investor_id)
	db.commit()
	return render_template("delete_investor.html")

@app.route("/add_investor", methods=['POST', 'GET'])
def add_investor():
	investor_added = 0
	if request.method == "POST":
		name = request.form.get("name")
		accesscode = request.form.get("accesscode")
		address = request.form.get("address")
		phone = request.form.get("phone")
		email = request.form.get("email")
		notes = request.form.get("notes")
		notes = notes.strip("\r+")
		timelimit = request.form.get("timelimit")
		
		submitted = db.execute("INSERT INTO investorinfo (name, accesscode, address, phone, email, timelimit, expiry, firstaccess, notes, deleted) VALUES (:name, :accesscode, :address, :phone, :email, :timelimit, 0, 0, :notes, FALSE)", {"name": name, "accesscode": accesscode, "address": address, "phone": phone, "email": email, "timelimit": timelimit, "notes": notes})
		db.commit()
		investor_added = 1
	return render_template("add_investor.html", investor_added=investor_added)

@app.route("/investor_details/<int:investor_id>", methods=['POST', 'GET'])
def investor_details(investor_id):
	result = db.execute("SELECT * FROM investorinfo WHERE id = %s" % investor_id).fetchall()

	return render_template("investor_details.html", result=result, investor_id=investor_id)

@app.route("/edit_investor_details/<int:investor_id>", methods=['POST', 'GET'])
def edit_investor_details(investor_id):
	email = "test1"
	if request.method == "POST":
		name = request.form.get("name")
		accesscode = request.form.get("accesscode")
		address = request.form.get("address")
		phone = request.form.get("phone")
		email = request.form.get("email")
		notes = request.form.get("notes")
		notes = notes.strip("\r+")
		timelimit = request.form.get("timelimit")
		firstaccess = request.form.get("firstaccess")

		submitted = db.execute("UPDATE investorinfo SET name = :name, accesscode = :accesscode, address = :address, phone = :phone, email = :email, timelimit = :timelimit, firstaccess = :firstaccess, notes = :notes WHERE id = :investor_id", {"name": name, "accesscode": accesscode, "address": address, "phone": phone, "email": email, "notes": notes, "timelimit": timelimit, "firstaccess": firstaccess, "investor_id": investor_id})
		db.commit()
		

	result = db.execute("SELECT * FROM investorinfo WHERE id = %s" % investor_id).fetchall()

	return render_template("edit_investor_details.html", result=result, email=email, investor_id=investor_id)

@app.route("/investor_page_views/<int:investor_id>", methods=['POST', 'GET'])
def investor_page_views(investor_id):
	if request.method == "POST":
		start_value = request.form.get("start")
		end_value = request.form.get("end")
		result = db.execute("SELECT * FROM investorpage WHERE investor_id = :investor_id AND time > :start_value AND time < :end_value ORDER BY time DESC LIMIT 2000", {"investor_id": investor_id, "start_value": start_value, "end_value": end_value}).fetchall()
		result_length = len(result)	
	else:
		result = db.execute("SELECT * FROM investorpage WHERE investor_id = %s ORDER BY time DESC LIMIT 70" % investor_id).fetchall()
		end_value = result[0][4]	
		result_length = len(result)
		start_value = result[result_length - 1][4]

	return render_template("investor_page_views.html", result=result, investor_id=investor_id, start_value=start_value, end_value=end_value, result_length=result_length)


message_data = {'message': '', 'user_id_receiver': 0, 'user_id_sender': 0}

@socketio.on("submit message")
def message(data):
	seconds = time.time()
	msg = "24"

	message = data['msg']
	to_user = int(data['to_user'])
	username = data['username_to']
	user_id_sender = int(session["user_id"])
	seconds = time.time()
	submitted = db.execute("INSERT INTO messages (user_id_sender, user_id_receiver, message, time_sent) VALUES (:user_id_sender, :user_id_receiver, :message, :time_sent)", {"user_id_sender": user_id_sender, "user_id_receiver": to_user, "message": message, "time_sent": seconds})
	db.commit()

	message_data.update(user_id_receiver = to_user)
	message_data.update(user_id_sender = user_id_sender)
	emit("message step", message_data, broadcast=True)
 
@socketio.on("look up messages")
def test_message(data):
	seconds = time.time()
	user_id_receiver = int(data['to_user'])
	user_id_sender = int(data['user_id_sender'])
	test_variable = int(data['user_id_sender'])
	logged_in_user = session["user_id"]
	sender_str = "user_id_receiver is: " + str(user_id_receiver) + "logged_in_user is: " + str(logged_in_user)
	if int(user_id_receiver) == int(logged_in_user):
		submitted = db.execute("UPDATE messages SET time_viewed = :now WHERE user_id_receiver = :user_id_receiver AND user_id_sender = :user_id_sender AND time_viewed IS NULL", {"user_id_sender": user_id_sender, "user_id_receiver": user_id_receiver, "message": message, "now": seconds})
		db.commit()

	timestamp = time.ctime(seconds)
	message_plus_formatting = ""
	messages = "<br>"

	result2 = db.execute("select * from messages left join users on users.id = user_id_sender where (user_id_sender = :user_id_sender and user_id_receiver = :user_id_receiver) OR (user_id_sender = :user_id_receiver and user_id_receiver = :user_id_sender) ORDER BY time_sent ASC", {"user_id_sender": user_id_sender, "user_id_receiver": user_id_receiver}).fetchall()
	db.commit()
	
	for i in result2:
		seconds = i.time_sent
		timestamp = time.ctime(seconds)
		message_plus_formatting = i.username + ": " + i.message + "<br> Msg sent: " + timestamp + "<br><br>"
		messages = messages + message_plus_formatting
	
	message_data.update(message = messages)
	message_data.update(user_id_receiver = user_id_receiver)
	message_data.update(user_id_sender = user_id_sender)
	emit("display messages final", message_data, broadcast=False)

message_data.update( {'comments': ''} )

@socketio.on("submit comment")
def comment(data):
	seconds = time.time()
	comment = data['comment']
	video_id = data['to_video']
	posting_user = session["user_id"]
	if comment != "from reply page":
		submitted = db.execute("INSERT INTO video_comments (video_id, posting_user, created_on, comment) VALUES (:video_id, :posting_user, :seconds, :comment)", {"video_id": video_id, "posting_user": posting_user, "seconds": seconds, "comment": comment})
		db.commit()
	
	video_id_int = int(video_id)
	result = db.execute("SELECT * FROM video_comments LEFT JOIN users ON users.id = video_comments.posting_user WHERE video_id = :video_id_int ORDER BY video_comments.created_on DESC", {"video_id_int": video_id_int}).fetchall()
	db.commit()
	
	
	comments = ""
	comments_array = []
	for i in result:

		comment_id = i[0]
		seconds = i[3] #must access it by index number or it formats the time automatically
		timestamp = time.ctime(seconds)
		result2 = db.execute("SELECT video_comment_replies.*, users.username FROM video_comment_replies LEFT JOIN users ON users.id = video_comment_replies.replying_user WHERE video_comment_id = %s ORDER BY video_comment_replies.created_on DESC" % comment_id).fetchall()
		db.commit()

		comments = comments + i.username + ": " + i.comment + "&nbsp; - &nbsp;" + timestamp + "&nbsp;<a href=\" /reply_to_comment/" + str(comment_id) + " \">Reply</a><br>Replies:<br>"
		for j in result2:
			timestamp = time.ctime(seconds)
			comments = comments + "&nbsp; - &nbsp;" + str(j.username) + ": " + str(j.reply) + " &nbsp;" + timestamp + "<br>"

		comments = comments + "<br>"

	message_data.update(comments = comments)
	message_data.update(video_id = video_id)
	emit("display comments", message_data, broadcast=True)
	emit("update wall broadcast true", "", broadcast=True)
walldata = {'walldata': ''}


@socketio.on("submit wall post")
def wall_post(data):
	user_id = session["user_id"]
	wallpost = data['wallpost']
	wall_owner = int(data['wall_owner'])
	seconds = time.time()
	your_wall = 0
	video_comments = 0
	comments_search_string = ""
	wall_posts_search_string = ""
	wall_posts_array = []	
	if(len(wallpost)):
		if 'no_submit' not in data:
			submitted = db.execute("INSERT INTO wall_posts (user_id, time_created, content) VALUES (:user_id, :seconds, :content)", {"user_id": user_id, "seconds": seconds, "content": wallpost})
			db.commit()
		emit("update wall broadcast true", "", broadcast=True)
	else:
		session["last_wall"] = wall_owner
		if wall_owner == user_id:
			your_wall = 1

		seconds = time.time()
	
		wallposts = "<br><br><br><br>"
		wall_string = str(wall_posts_array)
		if your_wall:
			friends = db.execute("SELECT * FROM friends where (user_id_requester = :user_id OR user_id_accepter = :user_id) AND (time_deleted IS NULL AND time_denied IS NULL)", {"user_id": user_id})
			wall_posts_search_string = "user_id = " + str(user_id)
	
			comments_search_string = str(user_id)
			for i in friends:
				if i.user_id_accepter == user_id:
					id_to_search_for = i.user_id_requester
				else:
					id_to_search_for = i.user_id_accepter
				comments_search_string = comments_search_string + " OR posting_user = " + str(id_to_search_for)
				wall_posts_search_string = wall_posts_search_string + " OR user_id = " + str(id_to_search_for)


			result = db.execute("SELECT wall_posts.*, users.username FROM wall_posts LEFT JOIN users ON users.id = wall_posts.user_id WHERE (%s) ORDER BY time_created DESC LIMIT 20" % wall_posts_search_string).fetchall()
			db.commit()

			wall_posts_array = []
			for i in result:
				most_recent_post = i.time_created
				wall_post_id = i.id

				result2 = db.execute("SELECT *, users.username FROM wall_post_replies LEFT JOIN users ON users.id = wall_post_replies.user_id WHERE wall_post_id = :wall_post_id", {"wall_post_id": wall_post_id}).fetchall()


				replies_array = []
				for j in result2:
					replies_array.append([j.id, j.user_id, j.time_created, j.content, j.username])
					if most_recent_post < j.time_created:
						most_recent_post = j.time_created

				wall_posts_array.append([i.id, i.user_id, i.time_created, i.content, i.username, replies_array, "wall post", most_recent_post])



			video_comments = db.execute("SELECT * FROM video_comments LEFT JOIN users ON users.id = video_comments.posting_user LEFT JOIN lecture_video ON lecture_video.id = video_comments.video_id WHERE (posting_user = %s) ORDER BY video_comments.created_on DESC LIMIT 20" % comments_search_string).fetchall()

			for i in video_comments:
				most_recent_post = i[3]
				created_on = i[3]
				comment_id = i[0]

				result2 = db.execute("SELECT video_comment_replies.*, users.username FROM video_comment_replies LEFT JOIN users ON users.id = video_comment_replies.replying_user WHERE video_comment_replies.video_comment_id = %s ORDER BY created_on ASC LIMIT 10" % comment_id)

				replies_array = []
				for j in result2:
					replies_array.append([j.id, j.replying_user, j.created_on, j.reply, j.username])
					if most_recent_post < j.created_on:
						most_recent_post = j.created_on


				wall_posts_array.append([i.id, i.posting_user, created_on, i.comment, i.username, replies_array, "video_comment", most_recent_post, i.video_id, i.video_title])


			def takeSecond(elem):
				return elem[7]

			wall_posts_array.sort(key=takeSecond, reverse=True)
			wall_posts_array = wall_posts_array[:20]
		

			for i in wall_posts_array:
				if i[6] == "wall post":
					if i[1] == user_id:
						wallposts = wallposts + "Post to wall - You:<br>"
					else:
						wallposts = wallposts + '<a href="/wall/' + str(i[1]) + '">' + str(i[4]) + "'s wall</a>:<br>" 
					wallposts += i[3] + "<br>"
					timestamp = time.ctime(i[2])
					wallposts += timestamp + '&nbsp;<a href="/wall_post_replies/' + str(i[0]) + '">Reply</a>:<br>'
					for k in i[5]:
						#wallposts += "&nbsp; - &nbsp;" + k[4] + ": " + k[3] + "<br>
						timestamp = time.ctime(k[2])
						wallposts += "&nbsp; - &nbsp;" + k[4] + ": " + k[3] + "&nbsp;" + timestamp + "<br>"
					wallposts += "<br><br>"
				else:
					if i[1] == user_id:
						wallposts += "You commented on the video " + '<a href="/video/' + str(i[8]) + '">' + i[9] + '</a><br>'
					else:
						wallposts += i[4] + " commented on the video " + '<a href="/video/' + str(i[8]) + '">' + i[9] + '</a><br>'
					wallposts += i[3] + "<br>"
					timestamp = time.ctime(i[2])
					wallposts += timestamp + "<br>"
					for k in i[5]:
						timestamp = time.ctime(k[2])
						wallposts += "&nbsp; - &nbsp;" + k[4] + ": " + k[3] + " &nbsp;" + timestamp + "<br>"
					wallposts += "<br><br>"



		else:
			result = db.execute("SELECT wall_posts.*, users.username FROM wall_posts LEFT JOIN users ON users.id = wall_posts.user_id WHERE user_id = %s ORDER BY time_created DESC LIMIT 20" % wall_owner).fetchall()
			wall_posts_array = []
			most_recent_post = 0
			for i in result:
				wall_post_id = i.id
				replies_array = []
				most_recent_post = i[4]
				result2 = db.execute("SELECT *, users.username FROM wall_post_replies LEFT JOIN users ON users.id = wall_post_replies.user_id WHERE wall_post_id = :wall_post_id", {"wall_post_id": wall_post_id}).fetchall()
				
				for j in result2:
					replies_array.append([j.id, j.user_id, j.time_created, j.content, j.username])
					if most_recent_post < j.time_created:
						most_recent_post = j.time_created
	
				wall_posts_array.append([i.id, i.user_id, i.time_created, i.content, i.username, replies_array, most_recent_post])

			def takeSecond(elem):
				return elem[6]

			wall_posts_array.sort(key=takeSecond, reverse=True)

			for i in wall_posts_array:
				timestamp = time.ctime(i[2])
				wallposts += "Wall post by " + i[4] + "<br>"
				wallposts += i[3] + "<br>"
				wallposts += timestamp + '&nbsp;'
				wallposts += '<a href="/wall_post_replies/' + str(i[0]) + '">Reply</a><br>'
				for k in i[5]:
					timestamp = time.ctime(k[2])
					wallposts += '&nbsp; - &nbsp;' + k[4] + ": " + k[3]
					wallposts += ' &nbsp;' + timestamp + "<br>"
				wallposts += "<br><br>"	

		wallposts += "<br><br>"
		walldata.update(walldata = wallposts)
		emit("display wall posts", walldata, broadcast=False)


if __name__ == '__main__':
        socketio.run(app)
