import json

import requests

group_id = '1915970043695337511'  # Type your group id
api_key = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJHYW1lciBIdXkiLCJVc2VyTmFtZSI6IkdhbWVyIEh1eSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTE1OTcwMDQzNjk5NTMxODE1IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTkxNTk3MDA0MzY5NTMzNzUxMSIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6Imh1eWdhbWVyc2hvcEBnbWFpbC5jb20iLCJDcmVhdGVUaW1lIjoiMjAyNS0wNi0yMSAxOToxNDo1NyIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.Mqxd62uCVtrF5156LW6EM7aDiicQBOHJJ20uOzquSO6J0GzLkswo9zMfDFjkchzCfzx3Z6LzErCNayQNQWcHxJQGUEt47zOthzT-gGDo3snnwYLWYIANQ-wJ2gIfK2h8jjYH9-CpIGBGYYeB7l6RzdU2PlR3MJWrUg8Jy3MZDDi4Wo9KoDC2X4TmU7fv1YCNWBpvM1nXM-0flU1kHpGNTs7gcbp-dBfiNIXtJ3fTtvt4UjTDMDzmkEwcBxhlCjNP4ZOWgHszru31wzZri3rmqwc-7qkz_Mwal5u_5I_W3hDGmv68BwvI3hbtZq-xmACTakN7PhjaAvz9S9hesCk1yg'  # Type your api key

url = f'https://api.minimax.io/v1/files/upload?GroupId={group_id}'
headers1 = {
    'authority': 'api.minimax.io',
    'Authorization': f'Bearer {api_key}'
}

data = {
    'purpose': 'voice_clone'
}

files = {
    'file': open('sepHuy.mp3', 'rb')
}
response = requests.post(url, headers=headers1, data=data, files=files)
file_id = response.json().get("file").get("file_id")
print(file_id)

#Voice cloning
url = f'https://api.minimax.io/v1/voice_clone?GroupId={group_id}'
payload2 = json.dumps({
  "file_id": file_id,
  "voice_id": "sephuygamer"
})
headers2 = {
  'authorization': f'Bearer {api_key}',
  'content-type': 'application/json'
}
response = requests.request("POST", url, headers=headers2, data=payload2)
print(response.text)