from scrapy import Selector
import requests

html = requests.get('https://www.sportsline.com/college-football/odds/money-line/').content
html = requests.get('https://www.sportsline.com/college-basketball/odds/money-line/').content

sel = Selector(text = html)

table = sel.xpath('//div[@class="table-container"]')


books = ['Caesars', 'DraftKings', 'Fanduel', 'Bet365'] # The order of the books on sportsline
investment = 200 # Minimum amount in one of the sportsbook accounts (needed for calculating arb bet amount)

# Investment will eventually become automated so that it looks at the two accounts it's considering when an arbitrage
# opportunity is found (either scrapes it or those values are stored and updated frequently in an offline file)

def toDecimalOdds(americanOddsList):
    '''
    toDecimalOdds: string list -> float list
    Converts each element of americanOddsList from american odds to decimal odds
    '''
    decimalOdds = []
    for el in americanOddsList:
        el_int = int(el)
        if el_int > 0:
            decimalOdds.append(el_int/100 + 1)
        else:
            decimalOdds.append(100/el_int + 1)
    return decimalOdds

def findArbitrage(urls : list[str]):
    """
    findArbitrage : string list --> Unit
    findArbitrage scrapes all of the odds for all of the games listed at each url in urls and determines
    whether an arbitrage opportunity exists.
    """
    for url in urls:
        html = requests.get(url).content
        sel = Selector(text = html)
        table = sel.xpath('//div[@class="table-container"]')
        for matchup in table.xpath("//tbody"):
            home_team = matchup.xpath('.//tr[contains(@class,"home-team")]//div[@data-testid = "Team-name"]/text()').get()
            away_team = matchup.xpath('.//tr[contains(@class,"away-team")]//div[@data-testid = "Team-name"]/text()').get()

            # Zero-th is consensus odds which isn't useful because it's not from a sportsbook
            # Odds are American odds format (+355, -125, etc.)
            home_odds = matchup.xpath('.//tr[contains(@class,"home-team")]//span[@class="primary"]/text()').extract()[1:]
            away_odds = matchup.xpath('.//tr[contains(@class,"away-team")]//span[@class="primary"]/text()').extract()[1:]
            try:
                homeDecimal = toDecimalOdds(home_odds)
                awayDecimal = toDecimalOdds(away_odds)
            except:
                print(home_team)
                print(home_odds)
                print(away_team)
                print(away_odds)
                next

            #Now I want to do all of the pairwise comparisons to see if any of them present an arbitrage opporunity. An awesome
            #explanation of arbs in general as well as the calculation for finding them can be found at:
            #https://www.gamblingsites.org/sports-betting/arbitrage-betting/

            for i,home_odd in enumerate(homeDecimal):
                home_book = books[i]
                for j,away_odd in enumerate(awayDecimal):
                    away_book = books[j]
                    #iap --> Individual Arbitrage Percentage
                    iap_home = (1/home_odd)*100
                    iap_away = (1/away_odd)*100
                    if iap_home + iap_away < 100: #article say you probably want to make this 98 so you get actual profits
                        tap = iap_home + iap_away #tap = Total Arbitrage Percentage (arb exists if TAP < 100)
                        home_stake = investment * iap_home / tap
                        away_stake = investment * iap_away / tap
                        print("Game: {} vs. {}".format(home_team, away_team))
                        print("Team: {}\t Stake: {:.2f}\t Sportsbook: {}".format(home_team, home_stake, home_book))
                        print("Team: {}\t Stake: {:.2f}\t Sportsbook: {}".format(away_team, away_stake, away_book))
                        print("EXPECTED PROFIT: {:.2f}".format(investment/tap*100 - investment))
            # Here I want to do the Market Leveraging with HomeDecimal and Away Decimal
            # This part is based on the paper:
            # "Beating​ ​the​ ​bookies​ ​with​ ​their​ ​own​ ​numbers​ ​-​ ​and​ ​how​ ​the online​ ​sports​ ​betting​ ​market​ ​is​ ​rigged"
            p_home = len(homeDecimal)/sum(homeDecimal)
            p_away = len(awayDecimal)/sum(awayDecimal)

            hmax = max(homeDecimal)
            amax = max(awayDecimal)

            if hmax > (1/(p_home - .08)):
                print("Team: {}\t Sportsbook: {}".format(home_team, books[homeDecimal.index(hmax)]))

            if amax > (1/(p_away - .08)):
                print("Team: {}\t Sportsbook: {}".format(away_team, books[awayDecimal.index(amax)]))


#findArbitrage([
#    'https://www.sportsline.com/nba/odds/money-line/',
#    'https://www.sportsline.com/college-basketball/odds/money-line/',
#    'https://www.sportsline.com/college-football/odds/money-line/'])




