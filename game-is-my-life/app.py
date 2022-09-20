from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'game is my life'

client1 = MongoClient('mongodb+srv://kms1:rlaalstjr1!@cluster0.rsxo4z3.mongodb.net/Cluster0?retryWrites=true&w=majority')
db1 = client1.dbsparta_plus_week4

client = MongoClient('mongodb+srv://ParkBigKing:anjfqhk@cluster0.cfmmcms.mongodb.net/?retryWrites=true&w=majority')
db = client.gamestorytest



@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db1.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    # return render_template('index.html')

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('signup.html', msg=msg)


# @app.route('/user/<username>')
# def user(username):
#     # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
#
#         user_info = db1.users.find_one({"username": username}, {"_id": False})
#         return render_template('user.html', user_info=user_info, status=status)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))



##로그인 코드
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    #비밀번호 암호화(hash)
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db1.users.find_one({'username': username_receive, 'password': pw_hash})

    #회원가입 정보 중 암호화 비밀번호와 로그인 암호화 비밀번호가 일치 하는게 있는지 확인한다.
    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})



##회원가입 코드
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    ##id와 비밀번호 값을 받고 비밀번호를 암호화(hash) 해준다.
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
    }
    db1.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 클라이언트에서 통과 한 값을 db에 있는지 없는지 체크해서 알려준다.
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db1.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})



@app.route('/content', methods=['GET'])
def show_diary():
    alldata = list(db.data.find({},{'_id':False}))

    return jsonify({'data':alldata})

@app.route('/content', methods=['POST'])
def save_content():
    today = datetime.now()
    now = today.strftime('%y-%m-%d-%H-%M-%S')
    date = today.strftime('%y년 %m월') 
    content_receive = request.form['content_give']
    try :
        file = request.files["file_give"]
        extension = file.filename.split('.')[-1]
        filename = f'file-{now}'
        save_to = f'static/img/{filename}.{extension}'
        file.save(save_to)
        doc ={
            'content':content_receive,
            'file':f'{filename}.{extension}',
            'date':date
        }
        db.data.insert_one(doc)
        return jsonify({'msg': '저장완룡'})
    except :
        doc ={
            'content':content_receive,
            'file':'none',
            'date':date
        }
        db.data.insert_one(doc)
        return jsonify({'msg': '저장완룡'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

