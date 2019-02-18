import requests
from bs4 import BeautifulSoup as bs
import web

class Tournament:
    def __init__(self, id, description, location, date):
        self.id = id
        self.description = description
        self.location = location
        self.date = date

response = requests.get("https://www.pdga.com/tour/search?OfficialName=&TDPDGANum=&date_filter%5Bmin%5D%5Bdate%5D=2019-02-14&date_filter%5Bmax%5D%5Bdate%5D=2019-12-31&State%5B%5D=NC")

soup = bs(str(response.content), 'html.parser')

tournaments = []
tournamentRows = soup.find('div', class_='view-pdga-tournament-list').find('tbody').find_all('tr')
for t in tournamentRows:
    col = t.find('td').find('a')
    description = col.contents[0]
    location = t.find('td', class_='views-field-Location').contents[0].replace('\\n','')
    date = t.find('td', class_="views-field-StartDate").contents[0].replace('\\n','')
    id = col['href'].split('/event/')[1]
    tournament = Tournament(id, description, location, date)
    tournaments.append(tournament)

print(tournamentRows)