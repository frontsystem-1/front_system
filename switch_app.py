import os
import sys
import subprocess
from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_paginate import Pagination, get_page_parameter
import datetime
import time
import nfc
import requests
import json
import MySQLdb
from flask_bcrypt import Bcrypt
import asyncio
import nfc_reader
from transitions import Machine
import random
import psutil
from itertools import chain

app = Flask(__name__)
bcrypt = Bcrypt()

cr = nfc_reader.MyCardReader()
print(cr.card_type)


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
    print('apache Trueexit')
    cursor.execute('set global wait_timeout=86400')
except Exception as e:
    print('apache False')
    error_ms = str(e)
    print('error: ',error_ms)
    time.sleep(5)
    subprocess.call(['sudo','systemctl','restart','start_app.service'])

states = ['go', 'return','go_record','return_record','post_go_record','post_return_record']

transitions = [
	{'trigger': 'go','source':['go', 'return'], 'dest': 'go_record'}, #goの信号を受け取る
	{'trigger':'go_record','source':'go_record', 'dest':'post_go_record','after':'insert_door'}, #受け取った信号を登録する
	{'trigger': 'post_go_record', 'source':'post_go_record', 'dest': 'go'},

	{'trigger': 'return','source': ['return', 'go'], 'dest':'return_record'}, #returnの信号を受け取る
	{'trigger':'return_record','source':'return_record', 'dest':'post_return_record','after':'insert_door'}, #returnの信号を受け取り、updateかpostかを識別し登録する
	{'trigger': 'post_return_record', 'source':'post_return_record', 'dest': 'return'}
	]


auth_array = []
post_data = []


class SwitchView(object):
	def __init__(self):
	    self.url_after_create = '' #/createで使用。フロントシステムでは使用しない
	    self.url_after_update = 'no_url' #/updateで使用。フロントシステムでは使用しない
	    self.login_staff = 'no staff' #ログインしているstaffのidを格納
	#全てのstaffのデータを取得し、その中に選択したidがあったらTrueを返す
	def all_staff_id(staff_id):
	    cursor.execute('SELECT id FROM staff')
	    all_staff = tuple(item[0] for item in (cursor.fetchall()))
	    if int(staff_id) in all_staff:
		    return True
	#引数のstaffのidのデータをstaffテーブルから一つだけ取り出す
	def serch_staff(staff_id):
	    cursor.execute('SELECT * FROM staff WHERE id = %s' % (staff_id))
	    serch_staff_data = cursor.fetchone()
	    return serch_staff_data

	def login_staff(login_id):
	    print(login_id)
	    #kettleデータベースよりログインIDと一致する職員のデータを呼び出す
	    command = [
            'curl',
            '-d', 'method=executeQuery',
            '--data-urlencode', f"params=['', 'select id, full_name,username from users where username=?  limit 0, 1', null, ['{login_id}']]",
            '-X', 'POST',
            'http://192.168.88.202/carekettle/public/api/store'
            ]
	    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,encoding='utf-8')
	    json_string = result.stdout
	    json_data = json.loads(json_string)
	    #return_dataに上記で絞り込んだ職員のデータを格納
	    return_data = json_data.get("return") 
	    print('return_data',return_data)
	    login_staff_check = ['No data']
	    #return_dataが空でない場合、ラズパイデータベースのstaffテーブルから名前が一致するデータを取り出す。
	    if return_data != []:
		    print('no []')
		    cursor.execute('''
 	           SELECT * FROM staff
        	    WHERE
	            name = '%s'
	            ''' % (return_data[0]['fullName']))
		    #取り出したデータをauth_staffに格納
		    auth_staff = cursor.fetchone()
		    print(auth_staff)
		    #auth_staffとreturn_dataのusernameを配列としてlogin_staff_checkに格納する
		    login_staff_check = [auth_staff,return_data[0]['username']]
		    #auth_staff = return_data
	    return login_staff_check

	#サインイン画面の処理
	@app.route('/sign_in', methods=['GET','POST'])
	def sign_in():
	    try:
		    cursor.execute('set global wait_timeout=86400')
		    now = datetime.datetime.now()
		    day = str(now)[0:11]
		    home_url = 'no url'
		    if request.method == 'POST':
			    #送られてきたidと一致するstaffデータを取得し、auth_staffに格納
			    login_id = request.form['login_id']
			    password = request.form['password']
			    print(login_id)
			    print(password)
			    """kettleDBに接続する前に使用していた借りのstaffログインパスワードのハッシ変換処理。今は使用していない。
			    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
			    if SwitchView.login_staff(login_id)[0] == 'No data':
				    print('None test')
				    return redirect(url_for('sign_in'))
			    """
			    auth_staff = SwitchView.login_staff(login_id)[0]
			    staff_login_id = SwitchView.login_staff(login_id)[1]
			    print('auth_staff: ',auth_staff)
			    #auth_staffがからなら/sign_inに飛ぶ
			    if auth_staff is None:
				    return render_template('sign_in.html')
			    #auth_staffがNoneでなく、かつ送られてきたパスワードと登録されているパスワード(ハッシュ化を解いた状態)が一致するか
			    #elif bcrypt.check_password_hash(staff_login_id,password):
			    elif staff_login_id == password: #ログイン成功時の処理
				    print('login')
				    #home_url = request.host_url  + '/' + day + '/-1/all_record'
				    login_staff = auth_staff
				    print('staff_id')
				    print(auth_staff[0])
				    auth_array.append(auth_staff[0])
				    post_data.append('更新')
				    print('sign in auth_array')
				    #return redirect(url_for('home_view',staff_id=auth_staff[0]['id'],login_staff=login_staff))
				    return redirect(url_for('home_view',staff_id=auth_staff[0]))
			    else:
				    print('no staff')
				    home_url = 'no url'
				    return render_template('sign_in.html')
	    except MySQLdb.OperationalError as e:
		    print(e)
		    command = "sudo systemctl restart start_app"
		    restart = subprocess.run(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
		    print(restart)
	    return render_template('sign_in.html')

	#職員のカードidmをstaff_cardテーブルに保存
	def add_staff_card(last_name,name,idm_data):
	    cursor.execute('''
	    INSERT INTO staff_card(name,card_id)
	    VALUE('%s','%s')
            ''' % ((last_name + '　' + name),idm_data))
	    connection.commit()
	#新たにstaffテーブルに重複しないデータを追加する
	def staff_setting(last_name,name):
	    cursor.execute("SELECT login_id FROM staff")
	    staffs_login_id = cursor.fetchall()
	    # staffs_login_id内のデータをセットとして扱い、重複しない4桁の数字をランダムに生成
	    while True:
		    random_number = '{:04d}'.format(random.randint(0, 9999))  # 4桁の数字を生成
		    if random_number not in [item[0] for item in staffs_login_id]:
			    break
	    hash_password = bcrypt.generate_password_hash(random_number).decode('utf-8') #ここでパスワードとidを追加しているが、kettleデータベース内のidを使用してのログインに変更したため、要らない機能
	    cursor.execute("""
	    INSERT INTO staff(name,login_id,password)
	    VALUES('%s','%s','%s')
	    """ % (last_name + ' ' + name,random_number,hash_password))
	    connection.commit()
	    #staffテーブルに新しいstaffデータを登録する

	#職員登録ページの処理
	@app.route('/<int:staff_id>/sign_up', methods=['GET','POST'])
	def sign_up(staff_id):
	    try:
		    message = ''
		    login_staff = SwitchView.serch_staff(staff_id) #login_staffのを引数のstaff_idを使って獲得する
		    """
		    if auth_array == [] and request.method == 'GET': #誰もログインしていない状態であれば/sign_inに飛ぶ
			    return redirect(url_for('sign_in'))
		    elif auth_array == []:
			    auth_array.append(staff_id)
		    elif staff_id not in auth_array:
			    return redirect(url_for('sign_in'))
		    """
		    if SwitchView.all_staff_id(staff_id) and request.method == 'POST': #引数のstaff_idがデータベースのstaff内にあり、かつ、登録するデータが送られてきている場合
			    name = request.form['name'] 
			    last_name = request.form['last_name'] 
			    SwitchView.kill_db_use() 
			    #裏で動いている扉開閉用のカードリーダーシステムを一度止める
			    cr.signup_card_data() #フロントのカードリーダーにカードをかざすと、idmを変数に格納(cr.idm_data)
			    print(cr.idm_data == '') 
			    print(name,last_name)
			    SwitchView.restart_db_use() 
			    SwitchView.add_staff_card(last_name,name,cr.idm_data) #staff_cardテーブルに名前・idmデータを保存
			    #再び扉開閉用のカードリーダーシステムを再開する
			    if cr.idm_data != '':
				    message = '職員データを登録できました。'
			    elif cr.idm_data == '':
				    message = ''
			    SwitchView.staff_setting(last_name,name) #staffテーブルに保存。
	    except UnboundLocalError:
		    login_staff = SwitchView.serch_staff(staff_id)
	    except MySQLdb.OperationalError as e:
		    print(e)
	    return render_template('sign_up.html',staff_id=staff_id,login_staff=login_staff,message=message)
	
	#residentの文字列をidとgoing_to_aloneに分ける。indexページで送られてくる入居者データは、idとgoing_to_aloneを繋げて一つの文字列として送ってくる(引数のresident)。
	def select_resident_nb_value(resident):
	    resident_value = []
	    while resident_value == []:
		    #それぞれを配列として[id,going_to_alone]に分ける
		    if resident.endswith('出可能'):
			    resident_value = [resident[:-6],resident[-6:]]
		    elif resident.endswith(')'):
			    resident_value = [resident[:-10],resident[-10:]]
		    elif resident.endswith('不可能'):
			    resident_value = [resident[:-7],resident[-7:]]
		    if resident_value == []:
			    continue
	    return resident_value
	#全ての名前がNoneでない入居者のデータを獲得する
	def all_residents():
	    cursor.execute("SELECT * FROM resident WHERE name != 'None' ORDER BY number ASC")
	    return cursor.fetchall()

	#residentテーブルから一人外出可能な人だけを取り出す
	def residents_value():
	    cursor.execute("""SELECT
			*
			FROM
			resident
			WHERE 
			reason = 'exist'
			AND
			name != 'None'
			ORDER BY number ASC
			""")
	    residents = cursor.fetchall()
	    print(residents)
	    return residents
	
	#日付を選択し、その日の記録を取り出す
	def today_value(day):
	    cursor.execute("""SELECT
			    id
			    FROM
			    card_record
			    WHERE 
			    datetime like '%s' LIMIT 1
			    """% (day + '%'))
	    today = cursor.fetchone()
	    return today

	#送られて来た入居者様のidと一致するデータを取り出す
	def select_name(resident_id):
	    command = [
            'curl',
            '-d', 'method=executeQuery',
            '--data-urlencode', f"params=['', 'select name from service_user_ekimae where active=? and id =? limit 0, 1', null, [1,'{resident_id}']]",
            '-X', 'POST',
            'http://192.168.88.202/carekettle/public/api/store'
	    ]
	    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,encoding='utf-8')
	    json_string = result.stdout
	    json_data = json.loads(json_string)
	    resident_data = json_data.get("return")
	    #cursor.execute('SELECT name FROM resident where id = %s' % (resident_id))
	    #resident_data = cursor.fetchone()
	    return resident_data

	#すべてのdoor_recordか、entrance_dayにデータが入っている物のみか、entrance_dayがNullの物かを選択し、呼び出す
	def serch_today_value(day,resident_id,return_check):
	    print('resident_id: ',resident_id)
	    select_value = 1
	    resident_name = '-1'
	    print(day)
	    day_format = datetime.datetime.strptime(day, '%Y-%m-%d')
	    new_day = day_format + datetime.timedelta(days=1)
	    tomorrow = new_day.strftime('%Y-%m-%d')
	    if int(resident_id) == -1: #入居者様の指定がされていない場合は、indexページから-1が送られてくる
		    select_value = 'IS NOT NULL' #select_valueに IS NOt NULL を入れ、nameがnullでない場合のデータを取り出す
	    if int(resident_id) != -1: #入居者様を指定した場合
		    resident_data = SwitchView.select_name(resident_id) #resident_dataに指定した入居者様のデータを格納
		    print('resident:',resident_data[0]['name'])
		    #resident_name = resident_data[0]
		    resident_name = resident_data[0]['name']
		    select_value = "= '" +  str(resident_name) + "'" #select_valueは、SQL文内で入居者様の名前で絞り込む用の文字列を格納
		    print('select_value',select_value)
	    if SwitchView.today_value(day) is None: #その日のデータがcard_recordテーブルに無ければ、error block record(架空の名前) 年月日 00:00:00と表示しないデータを作成
		    cursor.execute("""INSERT INTO card_record(datetime,type,idm) 
		    VALUES('%s','go','error block record')
		    """ % (day + ' 00:00:00'))
		    connection.commit()
	    today = '' #最後にreturnするtodayの空のデータ
	    if return_check == 'all_record': #今日の全てのデータ
		    print('1')
		    cursor.execute("""
		    SELECT r.name,
			t1.datetime,
			t1.staff_name,
			t1.reason,
			t1.update_time,
			t2.datetime,
			t2.staff_name,
			t2.reason,
			t2.update_time,
			t1.id,
			t2.id,
			t1.first_time,
			t2.first_time,
			t1.return_id,
			t2.go_id,
			t1.return_complete
			FROM resident r
			LEFT JOIN card_record t1
			ON r.name = t1.idm
			AND t1.datetime >= '%s 00:00:00'
			AND t1.datetime < '%s 00:00:00'
			LEFT JOIN return_data t2
			ON r.name = t2.idm
			AND t2.datetime >= '%s 00:00:00'
			AND t2.datetime < '%s 00:00:00'
			AND (t1.datetime <= t2.datetime OR t1.datetime = '%s 00:00:00' 
			OR t2.datetime = '%s 00:00:00')
			WHERE 
			(t1.datetime IS NOT NULL OR t2.datetime IS NOT NULL)
			AND (t1.id = t2.go_id AND t1.return_id = t2.id)
			AND r.name %s
			ORDER BY COALESCE(t1.datetime, t2.datetime) DESC
		   """  % (day,tomorrow,day,tomorrow,day,day,select_value))
		    today = cursor.fetchall()
	    elif return_check == 'no_return': #今日のreturn_dataがないもの、未帰館
		    print('2')
		    cursor.execute("""
		    SELECT r.name,
			t1.datetime,
			t1.staff_name,
			t1.reason,
			t1.update_time,
			t2.datetime,
			t2.staff_name,
			t2.reason,
			t2.update_time,
			t1.id,
			t2.id,
			t1.first_time,
			t2.first_time,
			t1.return_id,
			t2.go_id,
			t1.return_complete
			FROM resident r
			LEFT JOIN card_record t1
			ON r.name = t1.idm
			AND t1.datetime >= '%s 00:00:00'
			AND t1.datetime < '%s 00:00:00'
			LEFT JOIN return_data t2
			ON r.name = t2.idm
			AND t2.datetime >= '%s 00:00:00'
			AND t2.datetime < '%s 00:00:00'
			AND (t2.datetime = '%s 00:00:00'
			AND t1.return_complete = FALSE)
			WHERE 
			(t1.datetime IS NOT NULL AND t2.datetime IS NOT NULL)
			AND (t1.id = t2.go_id AND t1.return_id = t2.id)
			AND r.name %s
			ORDER BY COALESCE(t1.datetime, t2.datetime) DESC
		    """ % (day,tomorrow,day,tomorrow,day,select_value))
		    today = cursor.fetchall()
	    elif return_check == 'return': #今日のreturn_dataにデータがあるもの、帰館
		    print('3')
		    cursor.execute("""
		    SELECT r.name,
			t1.datetime,
			t1.staff_name,
			t1.reason,
			t1.update_time,
			t2.datetime,
			t2.staff_name,
			t2.reason,
			t2.update_time,
			t1.id,
			t2.id,
			t1.first_time,
			t2.first_time,
			t1.return_id,
			t2.go_id,
			t1.return_complete
			FROM resident r
			LEFT JOIN card_record t1
			ON r.name = t1.idm
			AND t1.datetime >= '%s 00:00:00'
			AND t1.datetime < '%s 00:00:00'
			LEFT JOIN return_data t2
			ON r.name = t2.idm
			AND t2.datetime >= '%s 00:00:00'
			AND t2.datetime < '%s 00:00:00'
			AND (t1.datetime <= t2.datetime 
			OR t1.datetime = '%s 00:00:00'
			AND t2.datetime != '%s 00:00:00')
			OR (t2.datetime = '%s 00:00:00' 
			AND t1.return_complete = TRUE)
			WHERE
			(t1.datetime IS NOT NULL AND t2.datetime IS NOT NULL)
			AND (t1.id = t2.go_id AND t1.return_id = t2.id)
			AND r.name %s
			ORDER BY COALESCE(t1.datetime, t2.datetime) DESC
		    """ % (day,tomorrow,day,tomorrow,day,day,day,select_value))
		    today = cursor.fetchall()
	    return today
	
	#最後にデータベース上に登録したデータのidを獲得
	def search_last_id():
	    cursor.execute("SELECT LAST_INSERT_ID()")
	    last_insert_id = cursor.fetchone()[0]
	    return last_insert_id
	    
	#exitかentranceか選択し、新たにrecordを登録する
	def post_door_record(resident_id,day,time,nb,resident_name,go_out_reason,staff_name,request):
	     print('home page error')
	     print('not add record')
	     #最後に登録してあるreturn_dataのidを取得し、そこに+1をする
	     cursor.execute("""
	     SELECT id FROM return_data ORDER BY id DESC LIMIT 1
	     """)
	     new_return_id = int(cursor.fetchone()[0]) + 1
	     if type(staff_name) is list:
	     	staff_name = staff_name[1]
	     #card_recordを追加し、先ほど取得したnew_return_idをreturn_idとして登録
	     cursor.execute("""
	     INSERT INTO card_record(datetime,type,idm,staff_name,reason,first_time,return_id)
	     VALUES ('%s','%s','%s','%s','%s','%s','%s')
	     """ % (day + ' ' + time,request,resident_name,staff_name,go_out_reason,day + ' ' + time,new_return_id))
	     connection.commit()
	     #最後に追加されたIDを獲得するコード。上記のcard_recordのidを取得する
	     last_insert_id = SwitchView.search_last_id()
	     #return_dataを日付+00:00:00で追加し、上記で獲得したlast_insert_idをgo_idに登録
	     cursor.execute("""
	     INSERT INTO return_data(datetime,type,idm,go_id) VALUES ('%s','return','%s','%s')
	     """ % (day,resident_name,last_insert_id))
	     connection.commit()
	     #この処理で、card_recordを追加すると同時に、00:00:00のreturn_dataを追加する。
	     #この二つはgo_idとreturn_idで結びつけられる
	     	
	#goかreturnかの信号を受け取り、外出記録を登録する
	def insert_door(event):
	    print('event',event)
	    if type(event) == list: #homeページからpostされたデータは、配列で届く
		    print('if list')
		    request = event[0]
		    page_value = event[1]
		    resident_nb = [event[4],event[2]]
		    resident_name = event[5]
		    go_out_reason = event[6]
		    staff_name = event[7]
		    print(resident_nb)
		    print(event[2])
		    door_time = event[3]
		    print(resident_nb)
		    day = 'exit_day'
		    time = 'exit_time'
		    return_value = ''
	    elif type(event) != list: #indexページからpostされたデータは、transitionsの影響で'event.kwargs.get'で呼び出す
		    print('event.kwargs.get: ',event.kwargs.get('resident_name'))
		    request = event.kwargs.get('data')
		    page_value = event.kwargs.get('page')
		    resident_nb = event.kwargs.get('resident_nb')
		    resident_name = event.kwargs.get('resident_name')
		    door_time = event.kwargs.get('door_time')
		    go_out_reason = ''
		    staff_name = event.kwargs.get('staff_name')
		    print(resident_nb)
		    return_value = ''
		    print('staff_name: ',staff_name)
		    print('resident_name: ',resident_name)
	    if request == 'return': #帰宅のリクエストの場合
		    if type(staff_name) is list:
			    staff_name = staff_name[1]
		    #名前が一致し、かつdatetimeが00:00:00のreturn_dataを取得
		    cursor.execute(""" SELECT id FROM return_data WHERE idm = '%s' AND datetime = '%s'ORDER BY id DESC
		    """ % (resident_name,page_value + ' 00:00:00'))
		    return_data_id = cursor.fetchone()
		    #もし、return_dataデータがあれば
		    if return_data_id is not None:
			    print('update root')
			    #獲得したreturn_dataのidで、そのデータを更新する
			    cursor.execute("""UPDATE return_data SET datetime = '%s',staff_name = '%s',reason='%s',first_time = '%s' where id = '%s'
			    """ % (page_value + ' ' + door_time,staff_name,go_out_reason,page_value + ' ' + door_time,return_data_id[0]))
			    connection.commit()
		    #return_dataがない場合は
		    elif return_data_id is None:
			    print('else root')
			    #card_recordの最後のidを獲得
			    cursor.execute(""" SELECT id FROM card_record ORDER BY id DESC""")
			    card_record_id = cursor.fetchone()
			    #return_dataを新規作成
			    #作成したreturn_dataのgo_idを獲得したcard_record_id+1として登録
			    cursor.execute("""INSERT INTO
			    return_data(idm,datetime,type,staff_name,reason,first_time,go_id)
			    VALUES('%s','%s','return','%s','%s','%s','%s')
			    """ % (resident_name,page_value + ' ' + door_time,staff_name,go_out_reason,page_value + ' ' + door_time,int(card_record_id[0]) + 1))
			    connection.commit()
			    #先後に登録したIDを獲得
			    #この場合はreturn_dataを登録したばかりのため、return_dataのidを獲得
			    last_insert_id = SwitchView.search_last_id()
			    #card_recordを00:00:00として新規登録
			    #return_idに先ほど獲得したlast_insert_idを登録
			    #card_recordを登録した際にreturn_dataも作成しされる
			    #そもそもreturn_dataがないという事は、一致するcard_recordもない状態
			    #そのためreturn_idの一致するcard_recordを登録する必要がある
			    cursor.execute("""INSERT INTO card_record(idm,datetime,type,return_id)
			    VALUES('%s','%s','go','%s')""" % (resident_name,page_value + ' 00:00:00',last_insert_id))
			    connection.commit()
		    #新たに登録したreturn_dataを下に、
		    #その入居者の登録した日時よりも前のcard_recordに、return_completeをTRUEにする
		    #return_completeがTRUEの場合は、retrun_dataが00:00:00でも帰宅済みとする
		    cursor.execute("""
                    UPDATE card_record SET return_complete = TRUE  WHERE idm = '%s' AND  return_complete = FALSE  AND  datetime like '%s' AND datetime < '%s'
                    """ % (resident_name,page_value + '%',page_value + ' ' + door_time))
		    connection.commit()
		    return		    
	    SwitchView.post_door_record(resident_nb,page_value,door_time,resident_nb,resident_name,go_out_reason,staff_name,request)	    
	

	@app.route('/record_update',methods=['POST']) #indexページから送られてきたデータを元に記録更新を行う
	def record_update() :
	    try:
		    now = datetime.datetime.now()
		    day = now.strftime("%Y-%m-%d")
		    time = now.strftime("%H:%M:%S")
		    data = request.get_json()
		    resident_name = data.get('resident_name')
		    go_id = data.get('go_id')
		    return_id = data.get('return_id')
		    go_time = data.get('go_time')
		    return_time = data.get('return_time')
		    reason = data.get('reason')
		    go_first_time = data.get('go_first_time')
		    return_first_time = data.get('return_first_time')
		    print(go_first_time,return_first_time)
		    print('go_id: ',go_id)
		    print('return_id: ',return_id)
		    if go_id != 'None': #外出データが送られてきたら、それをもとにcard_recordにデータを登録
			    cursor.execute("""
			    UPDATE card_record SET datetime = '%s',reason = '%s',update_time = '%s',first_time = '%s'
			    WHERE id = %s
			    """ % (go_time,reason,day+ ' ' + time,go_first_time,go_id))
			    connection.commit()
			    cursor.execute("SELECT first_time FROM card_record WHERE id = %s" % (go_id))
			    #更新したデータのfirst_time(初期登録時間)を獲得
			    if cursor.fetchone() is not None: #上記でデータを獲得出来たら、以下の処理を行う
				    cursor.execute("UPDATE card_record SET first_time = '%s' WHERE id = %s" % (go_first_time,go_id))
				    connection.commit() #調べたデータのfirst_time(初期登録時間)に元の外出時間を入れる
		    if return_id != 'None' and go_id == 'None' and go_time != day + ' 00:00:00': #帰宅時間が登録してあるが、外出記録が00:00:00の場合の処理
			    cursor.execute("""
	                    SELECT id FROM card_record WHERE datetime = '%s' and idm = '%s' and  return_id = '%s' LIMIT 1
	                    """ % (go_time,resident_name,return_id))
			    card_record_id = cursor.fetchone() #returnのidとreturn_idが一致、名前が一致、時間が一致するcard_recordのデータをcard_record_idに追加
			    cursor.execute("""
	                    UPDATE return_data SET datetime = '%s',reason = '%s',update_time = '%s', first_time = '%s',go_id = '%s'
	                    WHERE id = %s
	                    """ % (return_time,reason,day + ' ' + time,return_first_time,card_record_id[0],return_id)) #帰宅時間に現在日時と、リンクしているcard_recordのidを登録
		    elif return_id != 'None': #帰宅記録が送られてきた場合
			    cursor.execute("""
			    SELECT datetime FROM return_data WHERE id = %s
			    """ % (return_id))
			    check_time = cursor.fetchone()[0] #return_data内でreturnのidが一致する新しい記録(時間のみ)をcheck_timeに登録
			    if str(check_time) == day + ' 00:00:00': #check_timeが00:00:00の場合
					    return_first_time = return_time
			    cursor.execute("""
			    UPDATE return_data SET datetime = '%s',reason = '%s',update_time = '%s', first_time = '%s'
	                    WHERE id = %s
			    """ % (return_time,reason,day + ' ' + time,return_first_time,return_id))
			    connection.commit() #更新時間と最初に登録した時間をidの一致するreturn_dataに登録
		    
			    cursor.execute("""	
	                    UPDATE card_record SET return_complete = TRUE  WHERE idm = '%s' AND  return_complete = FALSE  AND  datetime like '%s' AND datetime < '%s'
	                    """ % (resident_name,day + '%',return_time))
			    connection.commit() #return_idの一致するcard_recordのreturn_completeをTRUEにする(帰宅済みにする)
		    elif return_id == 'None' and return_time != day + ' 00:00:00': #帰宅時間が送られてきていない場合
			    cursor.execute("""
			    INSERT INTO return_data(datetime,type,idm,reason,update_time,first_time,go_id)
			    VALUES ('%s','return','%s','%s','%s','%s','%s')
			    """ % (return_time,resident_name,reason,day + ' ' + time,return_first_time,go_id))
			    connection.commit() #return_dataに送られて来たデータを登録
			    cursor.execute("""
			    SELECT id FROM return_data WHERE datetime = '%s' and idm = '%s' and go_id = '%s'
			    """ % (return_time,resident_name,go_id))
			    return_data_id = cursor.fetchone() #時間、名前、go_idが一致するreturn_dataを選択
			    cursor.execute("""
			    UPDATE card_record
			    SET return_id = '%s' WHERE id = %s
			    """ % (return_data_id[0],go_id))
			    connection.commit() #card_recordのidと上記のretrun_dataで取り出したgo_idが一致するcard_recordデータに、上記のidをretrun_idとして登録する
			    cursor.execute("""
	                    UPDATE card_record SET return_complete = TRUE  WHERE idm = '%s' AND  return_complete = FALSE  AND  datetime like '%s' AND datetime < '%s'
	                    """ % (resident_name,day + '%',day + ' ' + time))
			    connection.commit() #card_recordの名前、未帰宅、日時が現在より前のデータで絞り込み、一致したデータのreturn_completeをTRUEにする(帰宅済にする)
		    return jsonify({'status': 'success'})

	    except ValueError:
		    print('ValueError')


	#入居者を登録するフロントシステムでは/createページは使っていない
	def post_resident(self,staff_id,name,number,room_number,going_to_alone,card_id):
	    try:
		    if staff_id not in auth_array:
			    return redirect(url_for('sign_in'))
		    self.url_after_create = 'no url'
		    now = datetime.datetime.now()
		    day = str(now)[0:11]
		    cursor.execute("""
		    INSERT INTO 
		    resident
		    (name,number,number_people,going_to_alone,card_id) 
		    VALUES
		    ('%s',%s,%s,'%s','%s')
		    """ % (name,int(number),int(room_number),going_to_alone,card_id))
		    connection.commit()
		    self.url_after_create = request.host_url +'/' + str(staff_id) + '/' + day + '/-1/all_record' #登録後に/createからindexページに飛ぶように全体のurlデータに格納しておく
	    except ValueError:
		    print('ValueError')
		    self.url_after_create = request.host_url + '/' + str(staff_id) + '/create'
	    print(self.url_after_create)
	#入居者のデータを更新するページ フロントシステムでは/updateページは使っていない
	def post_update_resident(self,staff_id,resident_id,name,number,room_number,going_to_alone,card_id):
	    try:
		    if auth_array == [] and request.method == 'GET':
			    return redirect(url_for('sign_in'))
		    elif auth_array == []:
			    auth_array.append(staff_id)
		    elif staff_id not in auth_array:
			    return redirect(url_for('sign_in'))
		    self.url_after_update = 'no url'
		    now = datetime.datetime.now()
		    day = str(now)[0:11]
		    cursor.execute("""
		    UPDATE resident
		    SET name = '%s',number = %s,number_people= %s,going_to_alone='%s',card_id='%s'
		    WHERE id = %s
		    """ % (name,int(number),int(room_number),going_to_alone,card_id,resident_id))
		    connection.commit()
		    self.url_after_update = request.host_url +'/' + str(staff_id) + '/' + day + '/-1/all_record' #登録後に/updateからindexページに飛ぶように全体のurlデータに格納しておく
	    except ValueError:
		    print('ValueError')
		    self.url_after_update = request.host_url + '/' + str(staff_id) + '/update'
	    print(self.url_after_update)
    
	def kill_db_use():
		# 停止したいプロセス名を指定する
		process_name = "db_use.py"
		print('kill db_use')
		os.system(f'sudo pkill -f {process_name}')

	#入退館用のカードリーダーを再開する
	def restart_db_use():
		process_name = "/var/www/html/db_use.py"
		process = subprocess.Popen(["python3", process_name])

	#/sign_outページ、ログアウト機能
	@app.route('/<int:staff_id>/sign_out', methods=['GET','POST'])
	def sign_out(staff_id):
	    try:
		    user_agent = request.headers.get('User-Agent')
		    print(user_agent)
		    print(request.method == 'POST')
		    if request.method == 'POST':
			    print('POST')
			    data = request.get_json()
			    post_data.append(data) #ページから送られてくる信号を格納する配列
			    print('auth_array')
			    print(auth_array)
			    if 'ログアウト' in post_data: #layout.htmlのログアウトボタンを押すと'ログアウト'の文字列をpostするようにしている。
				    auth_array.remove(staff_id) #その際にページURLから渡されたログインユーザーをauth_array（ログインユーザーを格納している配列）から取り除く
				    post_data.clear()
			    elif auth_array.count(staff_id) >= 2: #同じユーザーが2人以上の場合片方を取り除く。そのような場合は2窓で同じユーザーでログインしている
				     auth_array.remove(staff_id)
			    print('auth_array')
			    print(auth_array)
			    return 'page change'
		    print('auth_array last')
		    auth_array.remove(int(staff_id))
		    print(auth_array)
	    except  ValueError:
		    return redirect(url_for('sign_in'))
	    return redirect(url_for('sign_in'))

	#現在登録されている1015までの入居者データをfloor(3から10)を各階1から順に16部屋に分ける
	def resident_data(floor):
		start_id = int(floor + '01') #引数の数(3～10)+01をstart_idに格納する
		end_id = int(floor + '16') #引数の数(3～10)+15をend_idに格納する
		floor_office = {
		'3':10,
		'4':9,
		'5':8,
		'6':7,
		'7':6,
		'8':5,
		'9':4,
		'10':3
		}
		print(floor_office[floor])
		db_serch_value = floor_office[floor]
		command = [
	            'curl',
	            '-d', 'method=executeQuery',
	            '--data-urlencode', f"params=['', 'select id, name, room from service_user_ekimae where room like? and room!=? and active=1 and id != ? order by room ASC', null, ['{floor_office[floor]}%','300',216]]",
	            '-X', 'POST',
	            'http://192.168.88.202/carekettle/public/api/store'
	            ]
		result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,encoding='utf-8')
		json_string = result.stdout
		json_data = json.loads(json_string)
		return_data = json_data.get("return")
		print('return_data: ',return_data)	
		array_room = []
		count = 0
		previous_count = 0
		id_list = list(range(start_id, end_id + 1)) #start_idからend_idに+1した間の数を配列化
		#上記で配列化したデータをforで回し、aray_roomにid,name,roomデータを追加する
		for resident_data in return_data:
			array_room.append([resident_data['room'][:-2],resident_data['room'][-1:],resident_data['name']])
		print(array_room)
		#上記同様、raspberry pi側のdbからstart_id～end_id間のresidentデータを引き出しresultsに格納
		cursor.execute("""SELECT * FROM resident 
		WHERE (number BETWEEN %s AND %s)
		AND (number <= 1015)
		ORDER BY number ASC, (CASE WHEN number_people = 0 THEN 1 ELSE 2 END);
		""" % (int(start_id), int(end_id)));
		results = cursor.fetchall()
		return [results,array_room]
	
	#全ての登録されている共有スペースのデータ
	def all_space_name():
		cursor.execute("SELECT * FROM space_data");
		results = cursor.fetchall()
		return results

	#/homeページ
	@app.route('/<int:staff_id>/home',methods=['GET','POST'])
	def home_view(staff_id):	
		now = datetime.datetime.now()
		day = now.strftime("%Y-%m-%d")
		d_time = now.strftime("%H:%M:%S")
		db_check = 'check'
		print('home page?')
		cursor.execute("DELETE FROM card_record where idm like 'error%'") #空のデータエラー用のでーたを削除する
		connection.commit()
		time.sleep(0.5)
		cursor.execute("""INSERT INTO card_record(datetime,type,idm)
                    VALUES('%s','go','error block record')
                    """ % (day + ' 00:00:00'))
		connection.commit()
		current_year = datetime.datetime.now().year #現在の年数
		current_month = datetime.datetime.now().month #現在の月数
		calendar_month = f"{current_year}-{current_month:02d}" #年月
		cursor.execute("""
                        SELECT 
                        r.name,
                        t1.datetime,
                        t2.datetime,
			t1.reason
                        FROM 
                        resident r
                        LEFT JOIN 
                        card_record t1 ON r.name = t1.idm 
                        AND t1.datetime LIKE '%s'
                        LEFT JOIN 
                        return_data t2 ON r.name = t2.idm 
                        AND t2.datetime LIKE '%s'
                        AND (t1.datetime <= t2.datetime OR t1.datetime is NULL)
                        WHERE 
                        (t1.datetime IS NOT NULL 
                        AND t2.datetime IS NULL )  
                        ORDER BY 
                        t1.datetime DESC
		""" % (day + '%',day + '%'))
		go_value = cursor.fetchall() #外出者の記録(帰宅データのない人)
		go_resident = list(chain(*go_value)) #上記のリスト化
		go_resident_time = go_value
		cursor.execute("SELECT start_time FROM space_rental") #レンタルされている共有スペースの開始時間を獲得し、check_spaceに格納する
		check_space = cursor.fetchall()
		space_rental_all = ''
		all_data = []
		all_resident_name = []
		for i in range(3, 11): #301から1015までの入居者のデータを階毎に配列に格納していく
			data = SwitchView.resident_data(str(i))
			all_data.append(data[0])
			all_resident_name.append(data[1])
		print('all_data',all_data)
		all_space = SwitchView.all_space_name() #全ての共有スペースのデータをall_spaceに格納する
		cursor.execute("SELECT * FROM staff") #全てのstaffのデータをstaff_dataに格納する
		staff_data = cursor.fetchall()
		login_staff = SwitchView.serch_staff(staff_id)
		cursor.execute("""
		SELECT space_name,start_time,end_time FROM space_rental
		WHERE start_time >= '%s' OR end_time >= '%s'
		""" % (day + ' ' + d_time[:-3],day + ' ' + d_time[:-3]))
		print('start_time: ',day + ' ' + d_time[:-3]) #共有スペースをレンタルする際に被ってないか確認するために、現在時間よりも後に登録されているレンタルスペースデータをsdb_checkに格納
		db_check=cursor.fetchall()
		cursor.execute("SELECT * FROM remarks") #備考テンプレートを取得しremarksに格納
		remarks = cursor.fetchall()
	
		command = [
		'curl',
		'-d', 'method=executeQuery',
		'--data-urlencode', f"params=['','select id,name,room from service_user_ekimae where active=? and room !=? and user_id !=? order by CAST(SUBSTRING_INDEX(room, ?, 1) AS UNSIGNED)', null, [1,300,199,'-']]",
		'-X', 'POST',
		'http://192.168.88.202/carekettle/public/api/store'
		]
		result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
		json_string = result.stdout
		json_data = json.loads(json_string)
		residents = json_data.get("return") #入居者一覧
	
		print('residents: ',residents)
		return render_template('home.html',staff_id=staff_id,login_staff=login_staff, all_data=all_data,space_data='',
		space_name='',all_space=all_space,day='',staff_data=staff_data,space_rental_all=space_rental_all,select_month='',
		go_resident=go_resident,space_check='',db_check=db_check,remarks=remarks,all_resident_name=all_resident_name,residents=residents,
		go_resident_time=go_resident_time)

	
	#使っていない
	@app.route('/check_residents',methods=['POST'])
	def check_residents():
		data = request.get_json()
		name = data.get('name')
		room = data.get('room')
		room_number = room[:-2]
		print('room_number:', room_number)
		number_people = room[-2:]
		print(number_people[-1])
		array = [name,room_number,number_people]
		print(array)
		if int(room_number) > 516:
			cursor.execute("INSERT INTO resident(name,number,number_people,going_to_alone,card_id) VALUES('None',%s,2,'None',1)" % (room_number))
			connection.commit()
		cursor.execute("INSERT INTO resident(name,number,number_people,going_to_alone,card_id,reason) VALUES('%s',%s,%s,'一人外出可能',1,'exist')" % (name,room_number,number_people[-1]))
		connection.commit()
		cursor.execute("UPDATE resident SET reason = 'not_exist', number=10000  WHERE number = %s AND number_people = %s and name = 'None'" % (room_number,number_people[-1]))
		connection.commit()
		return jsonify({'status': 'success'})

	#/settingページ
	@app.route('/<int:staff_id>/setting')
	def setting_view(staff_id):
		all_data = []
		#部屋移動時に選択する用の入居者データをmove_residentに格納
		cursor.execute("SELECT id,name,number,number_people,going_to_alone FROM resident WHERE number BETWEEN 301 AND 1015 ORDER BY number,number_people ASC;")
		move_resident = cursor.fetchall()
		cursor.execute("SELECT * FROM staff")
		staff_data = cursor.fetchall()
		login_staff = SwitchView.serch_staff(staff_id)
		space_data = SwitchView.all_space_name() #全ての共有スペースのデータ

		all_data=[]
		all_resident_name = []
		for i in range(3, 11): #301から1015までの入居者のデータを階毎に配列に格納していく
			data = SwitchView.resident_data(str(i))
			all_data.append(data[0])
			all_resident_name.append(data[1])
		all_space = SwitchView.all_space_name() #入居者の部屋データ	

		cursor.execute("SELECT * FROM remarks")
		remarks = cursor.fetchall()
		return render_template('setting.html',staff_id=staff_id,login_staff=login_staff, all_data=all_data,
		space_data=space_data,space_name='',all_space=space_data,day='',staff_data=staff_data,move_resident=move_resident,
		remarks=remarks,all_resident_name=all_resident_name)

	
	#settingページで行われる処理
	@app.route('/setting_update', methods=['POST'])
	def setting_update():
		data = request.get_json()
		post_status = data.get('post_status')
		resident_id = data.get('resident_id')
		number = data.get('number')
		name = data.get('name')
		room_number = data.get('room_number')
		status = data.get('status')
		move_id = data.get('move_id')
		move_name = data.get('move_name')
		move_number = data.get('move_number')
		move_room_number = data.get('move_room_number')
		move_status = data.get('move_status')
		if post_status == 'update': #入居者の状態を更新する場合
			#going_to_aloneのみを変更する それ以外はsetting.htmlでdisplay:none;に設置しているため、選択した初期値のまま
			cursor.execute("UPDATE resident SET name = '%s',number = %s,number_people=%s,going_to_alone='%s',reason='exist' WHERE id = %s" % (name,number,room_number,status,resident_id))
			connection.commit()
		elif post_status == 'disappear': #入居者を退去させる場合
			cursor.execute("SELECT number FROM resident WHERE reason = 'not_exist' order by number DESC") #データベースに登録されている非入居者データの一番後ろの部屋番号を取得
			last_num = int(cursor.fetchone()[0]) + 1
			#選択した入居者をその部屋番号のデータに登録し、非入居者とする
			cursor.execute("UPDATE resident SET number = %s, reason = 'not_exist' WHERE id = %s" % (last_num,resident_id))
			connection.commit()
			#先ほどまで入居していた部屋番号には空のデータを追加
			cursor.execute("INSERT INTO resident(name,number,number_people,going_to_alone,card_id) value('None',%s,%s,'None','1')" % (number,room_number))
			connection.commit()
		elif post_status == 'move': #入居者の部屋を移動させる場合
			#移動先のデータと移動するデータを入れ替える
			cursor.execute("UPDATE resident SET name = '%s',number = %s, number_people = %s,going_to_alone = '%s' WHERE id = %s" % (move_name,number,room_number,move_status,move_id))
			connection.commit()
			#移動するresidentデータの更新
			cursor.execute("UPDATE resident SET name = '%s',number = %s,number_people = %s,going_to_alone = '%s' WHERE id = %s" % (name,move_number,move_room_number,status,resident_id))
			connection.commit()
		return jsonify({'status': 'success'})
	#共有スペースの新規、更新、削除の処理
	@app.route('/setting_space', methods=['POST'])
	def setting_space():
		data = request.get_json()
		post_status = data.get('space_status')
		post_name = data.get('space_name')
		post_update_name = data.get('update_space_name')
		post_new_name = data.get('new_space_name')
		if post_status == 'update': #送られてきたデータを更新
			cursor.execute("UPDATE space_data SET space_name = '%s' WHERE space_name = '%s'" % (post_update_name,post_name))
			connection.commit()
		elif post_status == 'delete': #送られてきたデータを削除
			cursor.execute("DELETE FROM  space_data WHERE space_name = '%s'" % (post_name))
			connection.commit()
		elif post_status == 'new': #送られてきたデータを追加
			cursor.execute("INSERT INTO space_data(space_name) VALUE('%s')" % (post_new_name))
			connection.commit()
		return jsonify({'status': 'success'})
	#備考テンプレートの新規、更新、削除の処理
	@app.route('/setting_remark', methods=['POST'])
	def setting_remark():
		data = request.get_json()
		post_status = data.get('remark_status')
		post_remark = data.get('remark')
		post_update_remark = data.get('update_remark')
		post_new_remark = data.get('new_remark')
		if post_status == 'update': #送られてきたデータの更新
			cursor.execute("UPDATE remarks SET remark = '%s' WHERE remark = '%s'" % (post_update_remark,post_remark))
			connection.commit()
		elif post_status == 'delete': #送られてきたデータを削除
			cursor.execute("DELETE FROM remarks WHERE remark = '%s'" % (post_remark))
			connection.commit()
		elif post_status == 'new': #送られてきたデータを追加
			cursor.execute("INSERT INTO remarks(remark) VALUE('%s')" % (post_new_remark))
			connection.commit()
		return jsonify({'status': 'success'})

	#homeページの処理
	@app.route('/home_submit', methods=['POST'])
	def submit_form():
		now = datetime.datetime.now()
		day = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M:%S") #現在時刻
		data = request.get_json()
		post_resident = data.get('resident_id') #送られてきた入居者id
		post_space = data.get('space_name') #送られてきた部屋名
		post_rental_start = data.get('rental_start_time') #共有スペースレンタル開始時間
		post_rental_end = data.get('rental_end_time') #共有スペースレンタル終了時間
		post_reason = data.get('reason') #備考
		post_go_out = data.get('go_out')
		post_go_out_reason = data.get('go_out_reason')
		staff_name = data.get('staff_name') #登録したstaff
		sleepover_check = data.get('sleepover_check') #外出か外泊か
		sleepover_go = data.get('sleepover_go') #外泊開始日
		sleepover_out = data.get('sleepover_out') #外泊戻り日
		create_space = data.get('create_space') #新規登録スペース
		staff_id = data.get('staff_id') #登録したstafid
		staff_rental_start = data.get('staff_rental_start') #共有スペースレンタル開始時間(staff)
		staff_rental_end = data.get('staff_rental_end') #共有スペースレンタル終了時間(staff)
		staff_reason = data.get('staff_reason') #共有スペースレンタル時備考(staff)
		mail = data.get('mail') #送られてきた郵便物データ
		mail_id = data.get('mail_id') #送られてきた郵便物データのid
		status = data.get('status') #郵便物の状態
		login_staff_id = data.get('login_staff_id') #loginしているstaffのid
		print('check sleepover')
		print(sleepover_go)
		print(sleepover_check)

		day_name = 'exit_day'
		time_name = 'exit_time'
		if post_go_out == 'return': #外出か帰宅か
			day_name = 'entrance_day'
			time_name = 'entrance_time'
		if status == 'complete' and mail_id is not None: #郵便物が返ってきた場合の処理
			cursor.execute("UPDATE resident_mail SET status = 'complete',check_staff = '%s' WHERE id = %s" % (staff_name, mail_id));
			connection.commit()
		elif mail == 'mail': #郵便物を新たに登録する処理
			cursor.execute("""
			INSERT INTO resident_mail(resident_id,reason,keep_mail_day,staff_name,status) VALUES(%s,'%s','%s','%s','keep')
			""" % (post_resident,post_go_out_reason,day,staff_name[1]));
			connection.commit()
		elif create_space is not None and create_space != '': #新規共有スペース登録処理
			print('is not none')
			cursor.execute("INSERT INTO space_data(space_name) VALUES('%s')" % (create_space))
			connection.commit()
		elif post_resident != '' and post_go_out != '' and post_space == '' or post_resident != '' and post_go_out != '' and post_space is None:
			#外出・外泊処理
			cursor.execute("SELECT * FROM resident WHERE id = '%s'" % (post_resident))
			select_resident = cursor.fetchone()
			if sleepover_go != '' and sleepover_check == '外泊': #外泊時の処理
				print(sleepover_go)
				print(sleepover_out)
				end_format = datetime.timedelta(days=1)
				start = datetime.datetime.strptime(sleepover_go + ' 00:00:01','%Y-%m-%d %H:%M:%S')
				end = datetime.datetime.strptime(sleepover_out + ' 00:00:01','%Y-%m-%d %H:%M:%S') + end_format
				print(start,end)
				for n in range((end - start).days): #外泊開始日から終了日までの記録を登録する
					range_time = start + datetime.timedelta(n)
					print(str(range_time)[0:11])
					print(str(range_time)[11:])
					day = str(range_time)[0:11]
					time = str(range_time)[11:]
					event = [post_go_out,day,select_resident[4],time,post_resident,select_resident[1],post_go_out_reason,staff_name]
					SwitchView.insert_door(event)
			if sleepover_go != '' and sleepover_check == '外泊':
					return jsonify({'status': 'success'})

			event = [post_go_out,day,select_resident[4],time,post_resident,select_resident[1],post_go_out_reason,staff_name]
			SwitchView.insert_door(event)

		elif  post_resident != '' and post_go_out == '' and post_space != '' and staff_id == '': #共有スペースレンタル日時登録
			print('space add')
			cursor.execute("""
			SELECT * FROM space_rental
			WHERE
			( (start_time <= '%s' AND end_time >= '%s')
			OR
			(start_time >= '%s' AND end_time <= '%s')
			OR
			(start_time <= '%s' AND end_time >= '%s' AND end_time >= '%s')
			OR
			(start_time >= '%s' AND end_time >= '%s' AND start_time <= '%s') ) AND space_name = '%s'  AND start_time LIKE '%s' 
			""" % (post_rental_start,post_rental_end,post_rental_start,post_rental_end,post_rental_start,post_rental_end,post_rental_start,post_rental_start,post_rental_end,post_rental_end,post_space,(day + '%')));
			calendar_check = cursor.fetchall()
			if calendar_check == ():			
				cursor.execute("""
				INSERT INTO space_rental (staff_or_resident,user_id,date_time,start_time,end_time,space_name,reason) 
				VALUES('resident',%s,'%s','%s','%s','%s','%s')"""
				% (post_resident,(day + ' ' + time),post_rental_start,post_rental_end,post_space,post_reason))
				connection.commit()
			elif calendar_check != ():
				print('test')
		elif post_go_out == '' and post_space != '' and staff_id != '' and post_resident == '': #共有スペースレンタル日時登録(staff)
			cursor.execute("""
			SELECT * FROM space_rental
			WHERE
			( (start_time <= '%s' AND end_time >= '%s')
			OR
			(start_time >= '%s' AND end_time <= '%s')
			OR
			(start_time <= '%s' AND end_time >= '%s' AND end_time >= '%s')
			OR
			(start_time >= '%s' AND end_time >= '%s' AND start_time <= '%s') ) AND space_name = '%s'  AND start_time LIKE '%s'
			""" % (post_rental_start,post_rental_end,post_rental_start,post_rental_end,post_rental_start,post_rental_end,post_rental_start,post_rental_start,post_rental_end,post_rental_end,post_space,(day + '%')));
			calendar_check = cursor.fetchall()
			if calendar_check == ():
				cursor.execute("""INSERT INTO space_rental 
				(staff_or_resident,user_id,date_time,start_time,end_time,space_name,reason) 
				VALUES('staff',%s,'%s','%s','%s','%s','%s')""" 
				% (staff_id,(day + ' ' + time),staff_rental_start,staff_rental_end,post_space,staff_reason))
				connection.commit()
			elif calendar_check != ():
				print('test')
		return jsonify({'status': 'success'})

	@app.route('/<staff_id>/resident_update_db', methods=['POST'])
	def resident_update_db(staff_id):
		print('update')

	@app.route('/<staff_id>/mail/<resident_id>/<mail_status>', methods=['POST','GET'])
	def mail_view(staff_id,resident_id,mail_status): #mailページ
		select_value = 1
		if mail_status == 'all_record':
			select_value = 0
	
		if  resident_id == '-1': #入居者の選択が無ければ-1で登録されている郵便物データを取り出す
			cursor.execute(
			"""
			SELECT *
			FROM (
			SELECT resident_mail.*,
			resident.name AS resident_name,
			CASE WHEN status = '%s' THEN 1 ELSE 0 END AS is_kept
			FROM resident_mail
			LEFT JOIN resident ON resident_mail.resident_id = resident.id
			ORDER BY resident_mail.keep_mail_day DESC
			) AS subquery
			WHERE is_kept = %s
			"""
			% (mail_status,select_value)) #select_valueは受け取り済みか受け取り未遂かを選択
			all_mail = cursor.fetchall()
		elif resident_id != '-1': #入居者が選択された場合、その人の郵便物データを取り出す
			cursor.execute(
			"""
			SELECT *
			FROM (
			SELECT resident_mail.*,
			resident.name AS resident_name,
			CASE WHEN status = '%s' THEN 1 ELSE 0 END AS is_kept
			FROM resident_mail
			LEFT JOIN resident ON resident_mail.resident_id = resident.id
			ORDER BY resident_mail.keep_mail_day DESC
			) AS subquery
			WHERE is_kept = %s
			AND
			subquery.resident_id = %s
			"""
			% (mail_status,select_value,resident_id)) #select_valueは受け取り済みか受け取り未遂かを選択
			all_mail = cursor.fetchall()
		residents = SwitchView.all_residents() #入居者一覧
		cursor.execute("SELECT * FROM staff")
		staff_data = cursor.fetchall()
		login_staff = SwitchView.serch_staff(staff_id)
		page = request.args.get(get_page_parameter(), type=int, default=1)
		limit = all_mail[(page -1)*10:page*10]
		pagination = Pagination(page=page, total=len(all_mail))
		return render_template('mail.html',staff_id=staff_id,login_staff=login_staff,residents=residents,all_mail=limit,pagination=pagination, page=page)

	@app.route('/<staff_id>/<space_name>/<day>', methods=['POST','GET'])
	def return_space_data(staff_id,space_name,day): #共有スペース使用状況ページ
		cursor.execute("""
		SELECT
		resident.name,
		staff.name,
		space_rental.start_time,
		space_rental.end_time,
		space_rental.reason,
		staff.id AS user_id,
		resident.id AS user_id,
		space_rental.id
		FROM space_rental
		LEFT JOIN staff ON space_rental.user_id = staff.id AND space_rental.staff_or_resident = 'staff'
		LEFT JOIN resident ON space_rental.user_id = resident.id AND space_rental.staff_or_resident = 'resident'
		WHERE space_rental.space_name = '%s' and space_rental.start_time LIKE '%s' ORDER BY space_rental.start_time;
		""" % (space_name, (day + '%')))
		space_data = cursor.fetchall() #指定スペースの使用状況
		now = datetime.datetime.now()
		day = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M:%S")
		print(""" 
		SELECT cr.id,         
		cr.datetime,         
		cr.type,         
		MAX(cr.idm) AS max_idm,         
		MAX(c.id) AS return_id,         
		MAX(c.datetime) AS return_datetime,         
		MAX(c.type) AS return_type,         
		MAX(c.idm) AS return_idm 
		FROM card_record AS cr LEFT JOIN card_record AS c ON cr.idm = c.idm AND c.datetime > cr.datetime WHERE cr.datetime 
		LIKE '%s'   AND cr.type = 'go' GROUP BY cr.id HAVING MAX(c.id) IS NULL
		""" % (day + '%'))
		#以下homeページと同様の処理(home.htmlを使いまわしているため)
		cursor.execute("""
                        SELECT 
                        r.name,
                        t1.datetime,
                        t2.datetime
                        FROM 
                        resident r
                        LEFT JOIN 
                        card_record t1 ON r.name = t1.idm 
                        AND t1.datetime LIKE '%s'
                        LEFT JOIN 
                        return_data t2 ON r.name = t2.idm 
                        AND t2.datetime LIKE '%s'
                        AND (t1.datetime <= t2.datetime OR t1.datetime is NULL)
                        WHERE 
                        (t1.datetime IS NOT NULL 
                        AND t2.datetime IS NULL )  
                        ORDER BY 
                        t1.datetime DESC
		""" % (day + '%',day + '%')) 

		go_resident = list(chain(*cursor.fetchall()))
		current_year = datetime.datetime.now().year
		current_month = datetime.datetime.now().month
		calendar_month = f"{current_year}-{current_month:02d}"
		space_rental_all = ''
		all_data = []
		all_resident_name = []
		for i in range(3, 11):
			data = SwitchView.resident_data(str(i))
			all_data.append(data[0])
			all_resident_name.append(data[1])
		all_space = SwitchView.all_space_name()
		cursor.execute("""
		SELECT space_name,start_time,end_time FROM space_rental
		WHERE start_time >= '%s' OR end_time >= '%s'
		""" % (day + ' ' + time[:-3],day + ' ' + time[:-3]))
		db_check=cursor.fetchall()
		cursor.execute("SELECT * FROM staff")
		staff_data = cursor.fetchall()
		login_staff = SwitchView.serch_staff(staff_id)

		command = [
		'curl',
		'-d', 'method=executeQuery',
		'--data-urlencode', f"params=['','select id,name,room from service_user_ekimae where active=? and room !=? order by CAST(SUBSTRING_INDEX(room, ?, 1) AS UNSIGNED)', null, [1,300,'-']]",
		'-X', 'POST',
		'http://192.168.88.202/carekettle/public/api/store'
		]
		result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
		json_string = result.stdout
		json_data = json.loads(json_string)
		residents = json_data.get("return")

		return render_template('home.html',staff_id=staff_id,login_staff=login_staff, all_data=all_data,space_data=space_data,
		space_name=space_name,all_space=all_space,day=day,staff_data=staff_data,space_rental_all=space_rental_all,select_month='',
		go_resident=go_resident,space_check='',db_check=db_check,remarks='',all_resident_name=all_resident_name,residents=residents)
	"""
	return render_template('home.html',staff_id=staff_id,login_staff=login_staff, all_data=all_data,space_data='',
        space_name='',all_space=all_space,day='',staff_data=staff_data,space_rental_all=space_rental_all,select_month='',
        go_resident=go_resident,space_check='',db_check=db_check,remarks=remarks,all_resident_name=all_resident_name)
	"""
	@app.route('/update_rental_space', methods=['POST'])
	def update_rental_space(): #共有スペース使用状況データ更新
		data = request.get_json()
		update_start_time = data.get('update_start_time')[0:10] + ' ' + data.get('update_start_time')[11:] + ':00'
		update_end_time = data.get('update_end_time')[0:10] + ' ' + data.get('update_end_time')[11:] + ':00'
		print('datetime',update_start_time)
		update_id = data.get('update_id')
		update_reason = data.get('update_reason')
		print('rental space')
		cursor.execute("UPDATE space_rental SET start_time = '%s', end_time = '%s', reason = '%s' WHERE id = %s" % (update_start_time,update_end_time,update_reason,update_id))
		connection.commit()
		return jsonify({'status': 'success'})


	@app.route('/<staff_id>/<select_month>/<select_room>/calendar', methods=['POST','GET'])
	def calendar_data(staff_id, select_month,select_room): #カレンダーページ
		now = datetime.datetime.now()
		day = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M:%S")
		where_value = ''
		all_space = SwitchView.all_space_name()
		if select_room != '-1':
			where_value = select_room
			print('where_value:',where_value)
			cursor.execute("""
		SELECT
		space_rental.*,
		staff.name,
		resident.name
		FROM
		space_rental
		LEFT JOIN staff ON space_rental.user_id = staff.id AND space_rental.staff_or_resident = 'staff'
		LEFT JOIN resident ON space_rental.user_id = resident.id AND space_rental.staff_or_resident = 'resident'
		where space_rental.start_time like '%s'
		and space_rental.space_name = '%s'
		ORDER BY start_time ASC
		""" % (select_month + '%',where_value))
			space_rental_all = cursor.fetchall() #その月の共有スペース使用状況

		elif select_room == '-1':
			print('space_name check',select_room)
			cursor.execute("""
			SELECT
			space_rental.*,
		staff.name,
		resident.name
		FROM
		space_rental
		LEFT JOIN staff ON space_rental.user_id = staff.id AND space_rental.staff_or_resident = 'staff'
		LEFT JOIN resident ON space_rental.user_id = resident.id AND space_rental.staff_or_resident = 'resident'
		where space_rental.start_time like '%s'
		ORDER BY start_time ASC
			""" % (select_month + '%'))
			space_rental_all = cursor.fetchall() #その月の共有スペース使用状況
		#以下homeページと同様の処理(home.htmlを使いまわしているため)
		cursor.execute("""
		SELECT space_name,start_time,end_time FROM space_rental
		WHERE start_time >= '%s' OR end_time >= '%s'
		""" % (day + ' ' + time[:-3],day + ' ' + time[:-3]))
		db_check=cursor.fetchall()
		print()
		cursor.execute("SELECT * FROM staff")
		staff_data = cursor.fetchall()
		login_staff = SwitchView.serch_staff(staff_id)

		command = [
		'curl',
		'-d', 'method=executeQuery',
		'--data-urlencode', f"params=['','select id,name,room from service_user_ekimae where active=? and room !=? order by CAST(SUBSTRING_INDEX(room, ?, 1) AS UNSIGNED)', null, [1,300,'-']]",
		'-X', 'POST',
		'http://192.168.88.202/carekettle/public/api/store'
		]
		result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
		json_string = result.stdout
		json_data = json.loads(json_string)
		residents = json_data.get("return")
		space_data = SwitchView.all_space_name() #全ての共有スペースのデータ
		
		"""
		return render_template('home.html',staff_id=staff_id,login_staff=login_staff, all_data=all_data,space_data='',

		"""
		return render_template('calendar.html',staff_id=staff_id,login_staff=login_staff,space_data=space_data,all_space=all_space,
		space_name='',day='',staff_data=staff_data,space_rental_all=space_rental_all,select_month=select_month,
		db_check=db_check,residents=residents)
	
	@app.route('/calendar/update',methods=['POST']) #カレンダーページで更新ボタンを押した時の処理
	def update_space():
		data = request.get_json()
		post_id = data.get('rental_id') #送られてきた入居者id
		post_start = data.get('rental_start')
		post_end = data.get('rental_end')
		post_reason = data.get('rental_reason')
		
		cursor.execute("UPDATE space_rental set date_time = '%s', end_time = '%s', reason = '%s' WHERE id = %s" % (post_start,post_end,post_reason,post_id))
		connection.commit()
		return jsonify({'status': 'success'})

	@app.route('/calendar/delete',methods=['POST']) #カレンダーページで削除ボタンを押した時の処理
	def delete_calendar():
		data = request.get_json()
		post_id = data.get('rental_id') #送られてきた入居者id
		cursor.execute("DELETE FROM space_rental WHERE id = %s" % (post_id))
		connection.commit()
		return jsonify({'status': 'success'})
		
	#js確認用テストページ
	@app.route('/<staff_id>/test', methods=['POST','GET'])
	def test_view(staff_id):

		login_staff = SwitchView.serch_staff(staff_id)
		return render_template('test.html',login_staff=login_staff,staff_id=staff_id)

machine = Machine(model=SwitchView, states=states, transitions=transitions, initial='go',auto_transitions=False, ordered_transitions=False,send_event=True) #transitionsに必要

#indexページ 引数でログインしているstaffと日付、選択している入居者、記録の状態を与えている
@app.route('/<int:staff_id>/<string:page_value>/<string:resident_id>/<string:return_check>', methods=['GET','POST'])
def return_view(staff_id,page_value,resident_id,return_check):
    try:
            """
            if auth_array == [] and request.method == 'GET':
                    return redirect(url_for('sign_in'))
            elif auth_array == []:
                    auth_array.append(staff_id)
            elif int(staff_id) not in auth_array:
                    return redirect(url_for('sign_in'))
            """
            now = datetime.datetime.now()
            day = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")
            data = request.get_json()
            today = ''
            residents = ''
            limit = ''
            page = ''
            pagination = ''
            print('day: ',day)
            residents = SwitchView.residents_value() #全入居者のデータ
            cursor.execute("SELECT * FROM card_record WHERE datetime like '%s' limit 1" % (day + '%'))
            #if cursor.fetchone() is None:
            cursor.execute("DELETE FROM card_record where idm like 'error%'")
            connection.commit()
            cursor.execute("""INSERT INTO card_record(datetime,type,idm)
                    VALUES('%s','go','error block record')
                    """ % (day + ' 00:00:00'))
            connection.commit()
            method_value = request.method #postかgetか
            select_resident_name = '-1' # 最初はは-1、-1でmysqlのwhere文を使うと全てが表示される
            cursor.execute("select name from staff where id = '%s'" % (staff_id)) #ログインしているstaffの名前を取得しstaff_nameに与える
            staff_name = cursor.fetchone()

            command = [
            'curl',
            '-d', 'method=executeQuery',
            '--data-urlencode', f"params=['','select id,name,room from service_user_ekimae where active=? and room !=? order by CAST(SUBSTRING_INDEX(room, ?, 1) AS UNSIGNED)', null, [1,'300','-']]",
            '-X', 'POST',
            'http://192.168.88.202/carekettle/public/api/store'
            ]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
            json_string = result.stdout
            """
            json_string = f'{{"code": 0, "return": [{{"idm": "{self.idm_data}", "name": "", "id": "188"}}]}}'
            """
            json_data = json.loads(json_string)
            return_data = json_data.get("return")
            print('return_data: ',return_data)

            if SwitchView.all_staff_id(staff_id) and request.method == 'POST': #ログインしているstaffが登録されており、データがpostされてきている状態の場合
                    print('data.get', data.get('go_out'),data.get('door_date'),data.get('door_time'),data.get('select_resident_id'))
                    print(data.get('select_resident_id'))
                    #resident_nb = SwitchView.select_resident_nb_value(data.get('select_resident_id')) #postされたデータをselect_resident_nbをidとgoing_to_aloneに分ける
                    #select_resident = SwitchView.select_name(resident_nb[0])
                    #select_resident_name = select_resident[0]
                    select_resident_name = data.get('select_resident_id')
                    today = SwitchView.serch_today_value(page_value,resident_id,return_check) #indexページで選択したpage_value(日付)、入居者のid、記録の状態を使い、それに合った記録を呼び出す
                    if data.get('door_time') is not None and data.get('go_out') is not None:
                    # door_record が None でなく、door_time が送信されていて、かつ door_time が door_record[3] と異なる場合の処理
                    # (indexページのformでデータを送った場合)
                            print('data get',data.get('go_out'))
                            SwitchView.trigger(data.get('go_out'))
                            print('fix error 1')
                            SwitchView.trigger(SwitchView.state,data=data.get('go_out'),page=data.get('door_date'),door_time=data.get('door_time'),
                            resident_nb=data.get('select_resident_id'),resident_name=select_resident_name,staff_name=staff_name[0])
                            print('fix error 2')
                            trigger_name = data.get('go_out') #最後transitionsはgoかreturnに戻るようにしている
                            print('fix error 3')
                            if trigger_name == 'go': #先ほどtrigger_nameに格納したgoかreturnを,SwitchView.state (現在の状態)に代入し、go→go_out→post_go_out→go→の状態を作っていく
                                    SwitchView.state = 'go'
                            elif trigger_name == 'return': #return側も上記と同様
                                    SwitchView.state = 'return'
                            
                    #if resident_nb != []: #postされたデータがselect_resident_nbをidとgoing_to_aloneでもなく空だった場合
                            #today = SwitchView.serch_today_value(page_value,-1,return_check) #指定する引数は記録の状態のみで、他は全ての条件を含めたその日の記録を呼び出す
                            #today = card_record
            if request.method == 'GET':
                    if page_value != 'favicon.ico':
                            day_value = page_value
                            today = SwitchView.serch_today_value(page_value,resident_id,return_check)
                            #today = card_record
            #下記は記録のページ機能に必要な処理
            page = request.args.get(get_page_parameter(), type=int, default=1)
            limit = today[(page-1)*30:page*30]
            print('today len:',len(today))
            print(len(today) / 3)
            pagination = Pagination(page=page, per_page=30,total=len(today))
            login_staff = SwitchView.serch_staff(staff_id) 
            
    except UnboundLocalError:
            login_staff = SwitchView.serch_staff(staff_id)
    except MySQLdb.ProgrammingError as e:
            print('ProgramingError')
            print(e)
            login_staff = SwitchView.serch_staff(staff_id)
            return render_template('index.html', staff_id=staff_id,login_staff=login_staff,residents=residents, today=limit, day_value=day,
           local_time=time, pagination=pagination, page=page, page_value=page_value, resident_data=resident_id, return_check=return_check)

    except MySQLdb.OperationalError as e:
            print(e)
            login_staff = SwitchView.serch_staff(staff_id)
    return render_template('index.html', staff_id=staff_id,login_staff=login_staff,residents=residents, today=limit, day_value=day,
           local_time=time, pagination=pagination, page=page, page_value=page_value, resident_data=resident_id, return_check=return_check,return_data=return_data)

if __name__ == "__main__":
    app.run(port = 8000, debug=True)
