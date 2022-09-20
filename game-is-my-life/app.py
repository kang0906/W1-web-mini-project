from datetime import datetime
from time import strftime

from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://ParkBigKing:anjfqhk@cluster0.cfmmcms.mongodb.net/?retryWrites=true&w=majority')
db = client.gamestorytest


@app.route('/')
def home():

    return render_template('index.html')

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
