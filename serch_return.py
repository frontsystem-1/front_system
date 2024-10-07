import os
from dotenv import load_dotenv
import subprocess
import datetime
import time
import MySQLdb
import use_motor

load_dotenv()

start_time = datetime.datetime.now()

#db接続
"""
connection = MySQLdb.connect(
host=os.environ['CONTAINER_ID'],
user=os.environ['DB_USER'],
password=os.environ['DB_PASS'],
db=os.environ['DB_NAME'],
charset='utf8'
)
"""
connection = MySQLdb.connect(
host='172.18.0.2',
user='root',
password='mypassword',
db='exit_entrance_management',
charset='utf8',
)
cursor = connection.cursor()
cursor.execute('set global wait_timeout=86400')

class SerchReturn(object):
	def __init__(self):
		self.serch_return = ''

switch_motor = SerchReturn()

cursor.execute("SELECT * FROM card_record WHERE type = 'return' ORDER BY id DESC LIMIT 1")
last_data = cursor.fetchone()
last_id = last_data[0]
last_time = last_data[1]
if __name__ == "__main__":
	while True:
		print('serch now...')
		cursor.execute("SELECT * FROM card_record WHERE type = 'return' ORDER BY id DESC LIMIT 1")
		current_data = cursor.fetchone()
		print(current_data)
		current_id = current_data[0]
		current_time = current_data[1]
		card_name = current_data[3]
		print(card_name)
		cursor.execute("SELECT * FROM resident WHERE name = '%s'" % (card_name))
		resident = cursor.fetchone()
		print(resident)
		print(last_id)
		print(current_id > last_id)
		print(current_time > last_time)
		print(resident is not None)
		if current_id > last_id and current_time > last_time and resident is not None:
			last_id = current_id
			if '一人外出可能' in resident[4]:
				print('MOVE')
				print(current_data)
				
				use_motor.move()
				
				

		time.sleep(1)
		connection.close()
		"""
		connection = MySQLdb.connect(
		host=os.environ['CONTAINER_ID'],
		user=os.environ['DB_USER'],
		password=os.environ['DB_PASS'],
		db=os.environ['DB_NAME'],
		charset='utf8'
		)
		"""
		connection = MySQLdb.connect(
			host='172.18.0.2',
			user='root',
			password='mypassword',
			db='exit_entrance_management',
			charset='utf8',
		)
		cursor = connection.cursor()
