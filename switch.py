import requests

headers = {
    'Authorization': '42b8a2cbc94cd3a845eafffce207a3db789ff1bc1fa92d428a6c2e921bf3fa69428fb37b200195e58c4fbaa9dbf454fa',
    'Content-Type': 'application/json; charset=utf8',
    }
"""
headers = {
    'Authorization': 'b4ea0b7201acabdf4fbfb781d5425426475cc9f074d0765a40fb308b3f23fd9c734ba84186c3528eb78b37e0901af291',
    'Content-Type': 'application/json; charset=utf8',
    }
"""
json_data = {
    'command': 'press',
    'parameter': 'default',
    'commandType': 'command',
    }

response = requests.post('https://api.switch-bot.com/v1.0/devices/FA9364B2BC98/commands',headers=headers,json=json_data)
#response = requests.post('https://api.switch-bot.com/v1.0/devices/F5B5D6CF0F0E/commands',headers=headers,json=json_data)

print('完了')
