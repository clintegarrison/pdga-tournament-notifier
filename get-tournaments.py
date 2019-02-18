import requests
from bs4 import BeautifulSoup as bs
import psycopg2
import os
import json

DATABASE_URL = os.environ['DATABASE_URL']
SLACK_HOOK = os.environ['SLACK_HOOK']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

print("Job starting")

class Tournament:
    def __init__(self, id, description, location, date):
        self.id = id
        self.description = description
        self.location = location
        self.date = date
    def __eq__(self, other): 
        return self.id== other.id

response = requests.get("https://www.pdga.com/tour/search?OfficialName=&TDPDGANum=&date_filter%5Bmin%5D%5Bdate%5D=2019-02-14&date_filter%5Bmax%5D%5Bdate%5D=2019-12-31&State%5B%5D=NC")

soup = bs(str(response.content), 'html.parser')

webTournaments = []
tournamentRows = soup.find('div', class_='view-pdga-tournament-list').find('tbody').find_all('tr')
for t in tournamentRows:
    col = t.find('td').find('a')
    description = col.contents[0]
    location = t.find('td', class_='views-field-Location').contents[0].replace('\\n','')
    date = t.find('td', class_="views-field-StartDate").contents[0].replace('\\n','')
    id = int(col['href'].split('/event/')[1])
    tournament = Tournament(id, description, location, date)
    webTournaments.append(tournament)

cur = conn.cursor()
cur.execute("select * from tournaments")
rows = cur.fetchall()
dbTournaments = []
for row in rows:
    print(row)
    tournament = Tournament(row[0], row[1], row[2], row[3])
    dbTournaments.append(tournament)
cur.close()

for webTournament in webTournaments:
    if webTournament not in dbTournaments:
        # slack alert new tourny
        url = "https://www.pdga.com/tour/event/%s" % webTournament.id
        msg = "New tourament added! \n *%s* \n %s \n %s \n %s" % (webTournament.description, webTournament.location, webTournament.date, url)
        slack_data = {'text': msg}
        response = requests.post(
            SLACK_HOOK, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        # then insert into db
        cur = conn.cursor()
        cur.execute("insert into tournaments values (%s,%s,%s,%s);", (webTournament.id, webTournament.description, webTournament.location, webTournament.date,))
        conn.commit()
        cur.close()

print("Job ending")