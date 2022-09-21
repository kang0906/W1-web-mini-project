from datetime import datetime, timedelta
from time import strftime
import hashlib
import jwt
import requests
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename

from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)
from pymongo import MongoClient
client = MongoClient('mongodb+srv://ParkBigKing:anjfqhk@cluster0.cfmmcms.mongodb.net/?retryWrites=true&w=majority')
db = client.gamestorytest


SECRET_KEY = 'game is my life'


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


##로그인 코드
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    #비밀번호 암호화(hash)
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

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


@app.route('/content', methods=['GET'])
def show_diary():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username_receive = request.args.get("username_give")
        if username_receive=="":
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
        else:
            posts = list(db.posts.find({"username":username_receive}).sort("date", -1).limit(20))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
        return jsonify({"posts":posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/content', methods=['POST'])
def save_content():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload["id"]})
    today = datetime.now()
    now = today.strftime('%y-%m-%d-%H-%M-%S')
    date = today.strftime('%y년 %m월') 
    content_receive = request.form['content_give']
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    # 좋아요 수 변경
    user_info = db.users.find_one({"username": payload["id"]})
    try :
        file = request.files["file_give"]
        extension = file.filename.split('.')[-1]
        filename = f'file-{now}'
        save_to = f'static/img/{filename}.{extension}'
        file.save(save_to)
        doc ={
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            'content':content_receive,
            'file':f'{filename}.{extension}',
            'date':datetime.now().isoformat(),
            "username": user_info["username"]
        }
        db.posts.insert_one(doc)
        return jsonify({'msg': '저장완룡'})
    except :
        doc ={
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            'content':content_receive,
            'file':'none',
            'date':datetime.now().isoformat(),
            "username": user_info["username"]
        }
        db.posts.insert_one(doc)
        return jsonify({'msg': '저장완룡'})


# 로그인파트##################################################################### 추가내용

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('signup.html', msg=msg)


##회원가입 코드
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""   
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 클라이언트에서 통과 한 값을 db에 있는지 없는지 체크해서 알려준다.
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 마이페이지파트##################################################################### 추가내용

@app.route('/user/<username>')
def user(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    username = payload["id"]
    today = datetime.now()
    now = today.strftime('%y-%m-%d-%H-%M-%S')
    name_receive = request.form["name_give"]
    about_receive = request.form["about_give"]
    new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
    try:
        file = request.files["file_give"]
        filename = secure_filename(file.filename)###
        extension = file.filename.split('.')[-1]
        file_path = f"profile_pics/{username}.{extension}"###
        file.save("./static/"+file_path)##
        new_doc["profile_pic"] = filename
        new_doc["profile_pic_real"] = f"{username}.{extension}"
        db.users.update_one({'username': payload['id']}, {'$set':new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except:
        db.users.update_one({'username': payload['id']}, {'$set':new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})

@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 좋아요 수 변경
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":

            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
