from flask import Flask, request, render_template, jsonify, redirect, url_for
import binascii
import json
import nfc
import os
import sys
import MySQLdb
import subprocess
import requests
import datetime
import time
import staff_data

staff_card = staff_data.MyCardReader()

#db接続
try:
        connection = MySQLdb.connect(
        host='172.18.0.2',
        user='root',
        password='mypassword',
        db='exit_entrance_management',
        charset='utf8',
        )
        
        cursor = connection.cursor()
        cursor.execute('set global wait_timeout=86400')
except Exception as e:
        error_ms = str(e)
        print('error: ',error_ms)
        time.sleep(5)
        subprocess.call(['sudo','systemctl','restart','start_app.service'])

def error_push(e):
    now = datetime.datetime.now()
    now_format = str(now)[:-7]
    url = "https://slack.com/api/chat.postMessage"
    data = {
    "token":'xoxp-5191608585938-5191476628739-6089819331569-498e2e5bbfc16e1d9d2fd25c2756a20a',
    "channel":'app_error',
    "text":"'%s' error: '%s'" % (now_format, e)
    }
    requests.post(url,data=data)


# Flaskアプリケーションの作成
app = Flask(__name__)

# ルートを定義して文字列を表示
@app.route('/')
def hello():
    cursor.execute("SELECT * FROM staff_card")
    staff_data = cursor.fetchall()
    return render_template('select_staff.html',staff_data=staff_data)

@app.route('/create')
def create():
    cursor.execute("SELECT * FROM staff_card")
    staff_data = cursor.fetchall()
    return render_template('staff_create.html',staff_data=staff_data)

@app.route('/submit',methods=['POST'])
def card_post():
    if request.method == 'POST':
        staff_card.read_id()
        print('post')
        name = request.form['option']
        cursor.execute(f"UPDATE staff_card SET card_id = '%s' where name = '%s'" % (staff_card.idm_data, name))
        connection.commit()
    return redirect(url_for('create'))

@app.route('/new',  methods=['POST'])
def new_post():
    try:
        if request.method == 'POST':
            if staff_card.read_id() != 'break':
                staff_card.read_id()
                print('post')
                name = request.form['name']
                # cursor.execute(f"INSERT INTO staff_card(name,card_id) VALUES('%s','%s')" % (name,staff_card.idm_data))
                # connection.commit()
                print('add data')
                return render_template('add_staff_card.html')
            else:
                return redirect(url_for('create'))
    except Exception as e:
           print('エラー')
           print(e)
           #os.system(f'sudo pkill -f staff_data.py')
           return redirect(url_for('create'))

@app.route('/index')
def index():
    try:
        cursor.execute("SELECT * FROM staff_card")
        staff_data = cursor.fetchall()
        return render_template('staff_index.html', staff_data=staff_data)
    except Exception as e:
        return render_template('staff_index.html')

if __name__ == '__main__':
    # アプリケーションを実行
    app.run(port='8088')
