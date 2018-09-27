import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
from NFL_teams_list import NFL_teams_list

r = requests.get("https://sports.sportingbet.com/en/sports/11/betting/american-football#sportId=11")
soup = BeautifulSoup(r.text, "html.parser")
assert r.status_code == 200, 'Failed request'

all_attrs = soup.findAll('div', attrs = {'class' : "marketboard-event-with-header"})
games = []

for m in all_attrs:
    attributes = list(m.stripped_strings)[-4:]
    fields = ["away_team", "away_odds", "home_team", "home_odds"]
    # attributes are ordered, list of tuples
    record = [(fields[ix], f) for ix, f in enumerate(attributes)]
    record = dict(record)
    # transform values from string to float, careful if you get empties
    record['away_odds'] = float(record.get('away_odds'))
    record['home_odds'] = float(record.get('home_odds'))
    # appending dictionary to games list
    games.append(record)

output = pd.DataFrame(games, columns=["away_team", "home_team", "away_odds", "home_odds"])

# verifies if odds are in european format, converts otherwise
if((output["away_odds"]<0).sum()>0 or (output["home_odds"]<0).sum()>0):
    output["away_odds"] = output["away_odds"].apply(lambda x: round(x/100+1,2) if x > 0 else round(100/(-x)+1,2))
    output["home_odds"] = output["home_odds"].apply(lambda x: round(x/100+1,2) if x > 0 else round(100/(-x)+1,2))

assert output.empty == False, 'No output given'

# add timestamp
output["timestamp"] = "{:%Y-%m-%d %H:%M}".format(datetime.datetime.now())
# add game-key
output["game_key"] = output["away_team"]+" - "+output["home_team"]

# removes college games using game-key
output = output[output["away_team"].isin(NFL_teams_list)]
output.reset_index(drop=True, inplace=True)

with open("/home/carlos/scrapers/results/sportingbet_results.txt", "a") as f:
    output.to_csv(f, header=False)