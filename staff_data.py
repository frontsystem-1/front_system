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

import timeout_decorator



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

class MyCardReader(object):
    def __init__(self):
            self.idm_data = ''
            
    def on_connect(self, tag):
        now = datetime.datetime.now()
        now_format = str(now)[:-7]
        idm = binascii.hexlify(tag._nfcid)
        print(idm)
        self.idm_data = str(idm)[2:-1]
        print(self.idm_data)
        #self.add_record_database()

    def read_id(self):
        try:
                print('start')
                clf = nfc.ContactlessFrontend('usb')
                try:
                    clf.connect(rdwr={'on-connect': self.on_connect})
                    
                finally:
                    clf.close()
                    print('end')
        except timeout_decorator.timeout_decorator.TimeoutError:
                
                print('timeout')
                return 'break'
        except Exception as e:
                print('エラー')
                print(e)
                error_push(e)
                os.system(f'sudo pkill -f staff_data.py')
                return 'break'

    def card_data(self):
        #タッチ待ち
        self.read_id()
        return self.idm_data

#t = MyCardReader()
#print(t.read_id() == 'break')
#while True:
    #if t.read_id() == 'break':
       # break
#t.read_id()
