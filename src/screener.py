import yfinance as yf
from yfinance import EquityQuery

class Screener():

    def __init__(self, market_cap: float, region: str):
        self.market_cap = market_cap
        self.region = region

    def screen(self) -> list[dict]:

        local_stocks = []
        local_stocks_names = []
        other_stocks = []

        filters = [
            EquityQuery('eq', ['region', self.region]),
            EquityQuery('gte',['intradaymarketcap', self.market_cap])
        ]

        query = EquityQuery('and', filters)
        offset = 0
        size = 200

        fim = 1

        if self.region == 'br':

            while fim != 0:

                response = yf.screen(query, offset = offset, sortField = 'intradaymarketcap', sortAsc = False, size = size)

                lista = response['quotes']

                old_len = len(local_stocks)

                for stock in lista:
                    if stock['symbol'].endswith("34.SA") or stock['symbol'].endswith("35.SA") or stock['symbol'].endswith("11.SA"):
                        other_stocks.append(stock) 
                    else:
                        local_stocks.append(stock)
                        local_stocks_names.append(stock['symbol'])

                fim = len(local_stocks) - old_len
                offset += size
            
        else:
            print(f'no screener implemented for region: {self.region}')
            return 0

        self.local_stocks = local_stocks
        self.local_stocks_names = local_stocks_names

        return self.local_stocks_names

