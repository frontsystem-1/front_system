import binascii
import nfc
import os
import sys
import subprocess
import requests
import datetime
import time
import timeout_decorator
import asyncio
import aiomysql
from nfc.clf import RemoteTarget
import json, requests
from pydub import AudioSegment
from pydub.playback import play



#switchbotのパラメーター（要書き換え）
#DEVICEID="FA9364B2BC98"
#DEVICEID="F5B5D6CF0F0E" #旧フロントで使っていたスイッチボット
DEVICEID="FA9364B2BC98"
#ACCESS_TOKEN="42b8a2cbc94cd3a845eafffce207a3db789ff1bc1fa92d428a6c2e921bf3fa69428fb37b200195e58c4fbaa9dbf454fa"
ACCESS_TOKEN="b4ea0b7201acabdf4fbfb781d5425426475cc9f074d0765a40fb308b3f23fd9c734ba84186c3528eb78b37e0901af291"
API_BASE_URL="https://api.switch-bot.com"

#raspberry piからswitchbotへリクエストを送る
headers = {
    # ヘッダー
    'Content-Type': 'application/json; charset: utf8',
    'Authorization': ACCESS_TOKEN
    }
url = API_BASE_URL + "/v1.0/devices/" + DEVICEID + "/commands"
body = {
    # 操作内容
    "command":"turnOn",
    "parameter":"default",
    "commandType":"command"
    }
ddd = json.dumps(body)
print('開始')


class MyCardReader(object):
    def __init__(self):
            self.idm_data = '' #カードのidをここに格納
            self.resident_id = '' #カードをかざした入居者のidを格納する値
            self.scan_card_name = '' #カードをかざした入居者の名前を格納する値
            self.card_type = 'go' #入退のどちらかを決める値
            self.last_time = datetime.datetime.now() #同じカードを連続で通した際の秒差
            self.motor_run = '' #モータが動いたかの値を入れる。switchbot では使用しない
            self.move_staff = ''

    #上で用意したswitchbotのデータのリクエストを飛ばす
    async def send_command_async(self):
        res = await asyncio.to_thread(requests.post, url, data=ddd, headers=headers)
    #非同期でsound_play()を実行する
    async def sound_play_async(self):
        loop = asyncio.get_event_loop()
        await asyncio.sleep(1) #音の出るタイミングを1秒ずらす
        await loop.run_in_executor(None, self.sound_play)
    #/home/pi/button1.mp3を鳴らす
    def sound_play(self):
        sound = AudioSegment.from_mp3("/home/pi/button1.mp3")
        play(sound)
    #self.idm_dataをもとに入居者のデータを獲得する
    def resident_select(self):
        
        command = [
            'curl',
            '-d', 'method=executeQuery',
            '--data-urlencode', f"params=['', 'select id, name, idm from service_user_ekimae where idm=? limit 0, 1', null, ['{self.idm_data}']]",
            '-X', 'POST',
            'http://192.168.88.202/carekettle/public/api/store'
            ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        json_string = result.stdout
        #time.sleep(0.3)
        print(json_string)
        json_data = json.loads(json_string)
        #idmに一致する入居者データを代入
        return_data = json_data.get("return")
        print('return_data: ',return_data)
        #入居者データがない場合はreturn_dataが[]になる
        if return_data != []:
            self.scan_card_name = return_data[0].get("name")
        print(self.scan_card_name)
    #非同期でmysqlに接続し、受け取ったデータにひとり外出可能な入居者がいるか・職員かを識別。
    async def db_set(self,loop,tag,time_data):
        now = datetime.datetime.now()
        day = now.strftime("%Y-%m-%d")
        #接続するmysqlの設定
        pool = await aiomysql.create_pool(
        host='172.18.0.2',
        user='root',
        password='mypassword',
        db='exit_entrance_management',
        charset='utf8',
        loop=loop,
        )
        #非同期接続の準備
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select * from resident where going_to_alone like '一人外出可%' and name = '{}'".format(self.scan_card_name))
                result = await cur.fetchone()
                #不明なidmを確認するためのデータベース
                print('scan_card_name check add')
                await cur.execute("insert into data_check(datetime,idm,scan_card_name) values('%s','%s','%s')" % (now,self.idm_data,self.scan_card_name))
                await conn.commit()
                await cur.execute('set global wait_timeout=86400')
                if result is not None:
                    #一人外出可能な入居者であればスイッチを起動
                    await asyncio.gather(self.send_command_async(), self.sound_play_async())
                    #最後に登録してあるreturn_dataのidを取得し、そこに+1をする
                    await cur.execute("""
             	    SELECT id FROM return_data ORDER BY id DESC LIMIT 1
                    """)
                    last_return_id = await cur.fetchone()
                    new_return_id = int(last_return_id[0]) + 1
                    #ひとり外出可能な入居者であればカードを通した時間と入館か帰館かを記録
                    await cur.execute("""INSERT INTO card_record(datetime,type,idm,first_time,return_id) VALUE('%s','%s','%s','%s',%s)
                    """ % (datetime.datetime.now(),self.card_type,self.scan_card_name,datetime.datetime.now(),new_return_id))
                    await conn.commit()
                    #最後に登録したIDを取得
                    await cur.execute("SELECT LAST_INSERT_ID()")
                    id_data = await cur.fetchone()
                    last_insert_id = id_data[0]
                    #先ほど作成したcard_recordに繋がるからのreturn_dataを作成
                    await cur.execute("""
                    INSERT INTO return_data(datetime,type,idm,go_id) VALUES ('%s','return','%s','%s')
                    """ % (day + ' 00:00:00',self.scan_card_name,last_insert_id))
                    await conn.commit()
                    final_time = datetime.datetime.now()
                    print('スイッチの信号を送信',final_time - time_data)
                elif result is None:
                    #一人外出可能な入居者でない場合はstaffか確認
                    await cur.execute("select * from staff_card where card_id = '{}'".format(self.idm_data))
                    staff_card = await cur.fetchone()
                    #staffの場合はスイッチを起動
                    if staff_card is not None:
                        print('move staff: ',self.move_staff)
                        self.move_staff = 'staff open door'
                        await asyncio.gather(self.send_command_async(), self.sound_play_async())
                        return
    #カードをかざし、読み取り上記の処理を行う
    async def nfc_start(self,loop):
        try:
            clf = nfc.ContactlessFrontend('usb')
            print(clf)
            tag = clf.connect(rdwr={
             'on-connect': lambda tag: False
            })
            print(tag)
            print(str(tag)[0:7] in 'Type3Tag')
            if str(tag)[0:7] in 'Type3Tag': #Felcaカードでない場合
                self.idm_data = str(binascii.hexlify(tag.idm))[2:-1]
            elif str(tag)[0:7] in 'Type2Tag':
                self.idm_data = str(tag)[-8:]
            start_time = datetime.datetime.now()
            self.resident_select()
            end_time = datetime.datetime.now()
            print('経過時間:', end_time - start_time)
            now = datetime.datetime.now()
            elapsed_time = (now - self.last_time).total_seconds()
            #5秒以内に同じカードをかざした際は反応しない
            #理由は2,3秒以上何度もかざし続けてしまう入居者様がいるため。その場合2度データをとることになる
            if elapsed_time < 5.0 and self.idm_data == str(binascii.hexlify(tag._nfcid))[2:-1]:
                clf.close()
                self.motor_run = 'no'
            else:
                await self.db_set(loop,tag,start_time)
                self.last_time = now
                self.motor_run = 'ok'
            clf.close()
            self.scan_card_name = ''
        except AttributeError as e:
            print("error",e)
            exit()

    #nfc_start()を呼び出す
    async def main(self,):
        loop = asyncio.get_event_loop()
        await self.nfc_start(loop)

    #職員登録の際のカードを読み取る処理
    #非同期ではない
    def staff_signup(self):
        try:
            clf = nfc.ContactlessFrontend('usb')
            tag = clf.connect(rdwr={
             'on-connect': lambda tag: False
            })
            print(tag)
            if str(tag)[0:7] in 'Type3Tag': #Felcaカードでない場合
                self.idm_data = str(binascii.hexlify(tag.idm))[2:-1]
            elif str(tag)[0:7] in 'Type2Tag':
                self.idm_data = str(tag)[-8:]
            clf.close()
        except AttributeError as e:
            print("error",e)
            exit()
    #sraff_signup()で受け取ったカードidをreturnする
    def signup_card_data(self):
        #loop = asyncio.get_event_loop()
        #await self.staff_signup(loop)
        self.staff_signup()
        return self.idm_data

#以下、nfc_reader.pyのみで動作確認をする際にコメントアウトを外す
#t = MyCardReader()
#while True:
    #asyncio.run(t.main())
#asyncio.run(t.signup_card_data())
