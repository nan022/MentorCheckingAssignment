from pymongo import MongoClient
import jwt
import datetime
import hashlib
from datetime import datetime,timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from collections import defaultdict

client = MongoClient('mongodb+srv://nande:nande@cluster0.8kafc33.mongodb.net/?retryWrites=true&w=majority')
db = client.dbmentorcek

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  
TOKEN_KEY = 'gungnir'
SECRET_KEY = "MENTORNANDA"

def get_mentor_by_institute(institute_name, course_title):
    result = db.kelas.find({"sekolah": institute_name, "program": course_title}, {"_id": 0, "mentor": 1, "sekolah": 1})
    mentor_list = [document["mentor"] for document in result]
    mentor_string = ', '.join(mentor_list)
    return mentor_string

@app.route('/', methods=['GET','POST'])
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode (
            token_receive, 
            SECRET_KEY, 
            algorithms=['HS256']
        )
        # user_info = db.users.find_one({'username': payload.get('email')})
        # return render_template("index.html", user_info=user_info)
        return render_template("home.html")
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was problem logging you in'
        return redirect(url_for('login', msg=msg))
    

@app.route('/sign_in', methods=["POST"])
def sign_in_cek():
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']
    result = db.users.find_one({
        "email": email_receive,
        "password": password_receive,
    })
    print(result)
    if result:
        payload = {
            "email": email_receive,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 2),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({
            "result": "success",
            "token": token,
        })
    else:
        return jsonify({
            "result": "fail",
            "msg": "We could not find a user with that id/password combination",
        })

@app.route('/login')
def login():
    token_receive = request.cookies.get(TOKEN_KEY)
    return render_template("login.html",token=token_receive)

@app.route('/data_kelas')
def data_kelas():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode (
            token_receive, 
            SECRET_KEY, 
            algorithms=['HS256']
        )
        # user_info = db.users.find_one({'username': payload.get('email')})
        # return render_template("index.html", user_info=user_info)
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'mentor': '$mentor',
                        'program': '$program'
                    },
                    'sekolah': {'$addToSet': '$sekolah'}
                }
            },
            {
                '$sort': {
                    '_id.mentor': 1,
                    '_id.program': 1
                }
            }
        ]
        data_institute = db.institute.find()
        mentor_list = list(db.kelas.aggregate(pipeline))
        return render_template("data_mentor.html", mentor_list=mentor_list, data_institute=data_institute)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was problem logging you in'
        return redirect(url_for('login', msg=msg))


@app.route('/data_history')
def data_history():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode (
            token_receive, 
            SECRET_KEY, 
            algorithms=['HS256']
        )
        pipeline = [
            {
                '$group': {
                    '_id': '$waktu',
                    '_status': {
                        '$first': '$status' 
                    },
                    'count': { '$sum': 1 }
                }
            }
        ]
        data = db.record_mentor.aggregate(pipeline)
        return render_template("mentor_history.html", data_list=data)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was problem logging you in'
        return redirect(url_for('login', msg=msg))
    
@app.route('/detail_history/<time>')
def detail_history(time):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive, 
            SECRET_KEY, 
            algorithms=['HS256']
        )
        data = db.record_mentor.find({'waktu': time})
        return render_template("detail_history.html", data_list=data)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))

@app.route('/institute_course')
def institute_course():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode (
            token_receive, 
            SECRET_KEY, 
            algorithms=['HS256']
        )
        # user_info = db.users.find_one({'username': payload.get('email')})
        # return render_template("index.html", user_info=user_info)     
        data = db.institute.find()
        return render_template("institute.html", data=data)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was problem logging you in'
        return redirect(url_for('login', msg=msg))
    

@app.route('/delete_data', methods=['POST'])
def delete_data():
    db.record_mentor.delete_many({})
    return redirect('/data_history')

@app.route('/tambah_data_kelas', methods=["POST"])
def kelas_post():
    mentor_receive = request.form['mentor_give']
    sekolah_receive = request.form['sekolah_give']
    program_receive = request.form['program_give']
    doc = {
        'mentor': mentor_receive,
        'sekolah': sekolah_receive,
        'program': program_receive
    }
    db.kelas.insert_one(doc)
    return jsonify({'msg': 'Data berhasil disimpan!'})

@app.route('/post_institute', methods=["POST"])
def institute_post():
    institute_receive = request.form['institute_give']
    course_receive = request.form['corse_give']
    category_receive = request.form['category_give']
    doc = {
        'institute': institute_receive,
        'course': course_receive,
        'category': category_receive
    }
    db.institute.insert_one(doc)
    return jsonify({'msg': 'Data berhasil disimpan!'})

@app.route('/post_data_checking', methods=["POST"])
def checking_post():
    if 'institute_name[]' in request.form:
        institute_names = request.form.getlist('institute_name[]')
        course_titles = request.form.getlist('course_title[]')
        statuses = request.form.getlist('status[]')
        mentor_lists = request.form.getlist('mentor_list[]')
        date_now = datetime.datetime.now().strftime('%Y-%m-%d')

        for i in range(len(institute_names)):
            doc = {
                'institute_name': institute_names[i],
                'course_title': course_titles[i],
                'status': statuses[i],
                'mentor_list': mentor_lists[i],
                'waktu': date_now
            }
            db.record_mentor.insert_one(doc)
        return redirect('/mentor_check')
    else:
        return jsonify({'msg': 'Tidak ada data yang dipilih.'})

@app.route('/mentor_check', methods=['GET', 'POST'])
def mentor_check():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode (
            token_receive, 
            SECRET_KEY, 
            algorithms=['HS256']
        )
        # user_info = db.users.find_one({'username': payload.get('email')})
        # return render_template("index.html", user_info=user_info)
        if request.method == 'POST':
            file = request.files['file']
            time_off = datetime.datetime.strptime(request.form['time_off'], '%Y-%m-%dT%H:%M')

            if file:
                df = pd.read_csv(file)
                selected_columns = ['Learners Name', 'Institute Name', 'Course Title', 'Submission Date', 'Status']
                selected_data = df[selected_columns]

                current_date = datetime.datetime.now().date()
                previous_day = current_date - datetime.timedelta(days=1)
                cutoff_time = datetime.datetime.combine(previous_day, datetime.time(hour=21, minute=0))

                grouped_data = defaultdict(list)
                for index, row in selected_data.iterrows():
                    date_string = row['Submission Date']
                    date_value = float(date_string)
                    date_format = pd.to_datetime(date_value, unit='ms')

                    if row['Status'] == 'pending' and date_format < time_off:
                        institute_name = row['Institute Name']
                        course_title = row['Course Title']
                        item = {
                            'Learners Name': row['Learners Name'],
                            'Institute Name': institute_name,
                            'Course Title': course_title,
                            'SubmissionDate': date_format.strftime('%Y-%m-%d %H:%M'),
                            'Status': row['Status'],
                            'MentorList': get_mentor_by_institute(institute_name, course_title)
                        }
                        grouped_data[(institute_name, course_title)].append(item)

                result = []
                for key, data_list in grouped_data.items():
                    item = {
                        'Institute Name': key[0],
                        'Course Title': key[1],
                        'DataList': data_list
                    }
                    result.append(item)

                return render_template('checking_mentor.html', result=result)
        return render_template('checking_mentor.html')
        
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was problem logging you in'
        return redirect(url_for('login', msg=msg))
if __name__ == '__main__':
    app.run(debug=True)
