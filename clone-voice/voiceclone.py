import requests
import json

group_id = '1915970043695337511'  # Type your group id
api_key = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJHYW1lciBIdXkiLCJVc2VyTmFtZSI6IkdhbWVyIEh1eSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTE1OTcwMDQzNjk5NTMxODE1IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTkxNTk3MDA0MzY5NTMzNzUxMSIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6Imh1eWdhbWVyc2hvcEBnbWFpbC5jb20iLCJDcmVhdGVUaW1lIjoiMjAyNS0wNi0yMSAxOToxNDo1NyIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.Mqxd62uCVtrF5156LW6EM7aDiicQBOHJJ20uOzquSO6J0GzLkswo9zMfDFjkchzCfzx3Z6LzErCNayQNQWcHxJQGUEt47zOthzT-gGDo3snnwYLWYIANQ-wJ2gIfK2h8jjYH9-CpIGBGYYeB7l6RzdU2PlR3MJWrUg8Jy3MZDDi4Wo9KoDC2X4TmU7fv1YCNWBpvM1nXM-0flU1kHpGNTs7gcbp-dBfiNIXtJ3fTtvt4UjTDMDzmkEwcBxhlCjNP4ZOWgHszru31wzZri3rmqwc-7qkz_Mwal5u_5I_W3hDGmv68BwvI3hbtZq-xmACTakN7PhjaAvz9S9hesCk1yg'  # Type your api key
file_id =  285185397563538 # Type file id

url = f'https://api.minimax.io/v1/voice_clone?GroupId={group_id}'

payload = json.dumps({
  "file_id":file_id,
  "voice_id": 'huygamershop'
})
headers = {
  'authorization': f'Bearer {api_key}',
  'content-type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)