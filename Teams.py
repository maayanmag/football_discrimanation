# import pandas as pd
# import numpy as np
import logging
import json
import io
import re
import scrapy
from urllib.parse import urljoin


class Teams(scrapy.Spider):
    name = 'football discrimination'
    allowed_domains = ['football.org.il']
    leumit_20_arab_teams_games = ['https://www.football.org.il/team-details/team-games/?team_id=1844&season_id=20',
                                  'https://www.football.org.il/team-details/team-games/?team_id=2530&season_id=20',
                                  'https://www.football.org.il/team-details/team-games/?team_id=2566&season_id=20']
    leumit_19_arab_teams_games = ['https://www.football.org.il/team-details/team-games/?team_id=1844&season_id=19',
                                  'https://www.football.org.il/team-details/team-games/?team_id=2530&season_id=19']
    leumit_18_arab_teams_games = ['https://www.football.org.il/team-details/team-games/?team_id=1844&season_id=18',
                                  'https://www.football.org.il/team-details/team-games/?team_id=2530&season_id=18']
    leumit_17_arab_teams_games = ['https://www.football.org.il/team-details/team-games/?team_id=1844&season_id=17',
                                  'https://www.football.org.il/team-details/team-games/?team_id=2530&season_id=17']
    leumit_16_arab_teams_games = ['https://www.football.org.il/team-details/team-games/?team_id=1844&season_id=16',
                                  'https://www.football.org.il/team-details/team-games/?team_id=2530&season_id=16']
    leumit_15_arab_teams_games = ['https://www.football.org.il/team-details/team-games/?team_id=1844&season_id=15',
                                  'https://www.football.org.il/team-details/team-games/?team_id=2530&season_id=15',
                                  'https://www.football.org.il/team-details/team-games/?team_id=1153&season_id=15']

    start_urls = leumit_15_arab_teams_games
    custom_settings = {
        'LOG_FILE': 'leumit_15_arab.log',
    }
    logging.getLogger().addHandler(logging.StreamHandler())

    games = {}

    def parse(self, response):
        for game in response.css('.games_table .table_row_group a'):
            url = urljoin(response.url, game.xpath('@href').extract_first())
            game_id = re.search('game_id=\d+', url).group(0)[8:]
            if game_id not in self.games:
                yield scrapy.Request(url, callback=self.parse_game, dont_filter=True)

    def parse_game(self, response):
        referees_names = response.css('.judge a .name ::text').extract()
        referees_positions = response.css('.judge a .position ::text').extract()
        referees = []
        for i in range(len(referees_names)):
            referees.append({
                'name': referees_names[i],
                'position': referees_positions[i]
            })

        score = response.css('.game-time .total ::text').extract()
        home_score = int(''.join(filter(str.isdigit, score[1])))
        guest_score = int(score[3])

        game = {
            'date': response.css('.game-time .date ::text').extract_first(),
            'home_score': home_score,
            'guest_score': guest_score,
            'home_team': response.css('.team-home a span ::text').extract_first(),
            'guest_team': response.css('.team-guest a span ::text').extract_first(),
            'referees': referees,
            'home_yellows': response.css(".home .yellow").xpath("../..//span[@class='name']/text()").extract(),
            'guest_yellows': response.css(".guest .yellow").xpath("../..//span[@class='name']/text()").extract(),
            'home_yellows2': response.css(".home .yellow2").xpath("../..//span[@class='name']/text()").extract(),
            'guest_yellows2': response.css(".guest .yellow2").xpath("../..//span[@class='name']/text()").extract(),
            'home_reds': response.css(".home .red").xpath("../..//span[@class='name']/text()").extract(),
            'guest_reds': response.css(".guest .red").xpath("../..//span[@class='name']/text()").extract(),
            'home_coach': response.css('#GAME_COACH_HOME').xpath("..//a/div/span[@class='name']/text()").extract_first(),
            'guest_coach': response.css('#GAME_COACH_GUEST').xpath("..//a/div/span[@class='name']/text()").extract_first(),
        }

        game_id = re.search('game_id=\d+', response.url).group(0)[8:]

        self.games[game_id] = game

    def closed(self, reason):
        with io.open('leumit_15_arab.json', 'w', encoding='utf8') as f:
            data = json.dumps(self.games, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
            f.write(data)


    # rules = {
    #     Rule(LinkExtractor(restrict_css=['.league-table a']), callback='parse_item')
    # }
