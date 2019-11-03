# 365scores parser
# Array example

import requests
import json

url = "https://webws.365scores.com/web/games/results/?langId=31&timezoneName=America/Sao_Paulo&userCountryId=-1&appTypeId=5&competitions=113"
r = requests.get(url)
data = r.json()

for item in data['games']:
    print(item['homeCompetitor']['name'],"x",item['awayCompetitor']['name'])
