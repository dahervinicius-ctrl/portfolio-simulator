import yfinance as yf
import pandas as pd
import random

class Stocks():

    def __init__(self, stocks_names: list[str]):

        self.stocks_names = stocks_names
        self.cleaned_stocks_list = []
        self.random_stocks_list = []
        self.stocks_returns = None
        self.period = None

    def cleaned_stocks(self, stocks_to_analyse: list[str], period: str):

        min_expected_days = len(yf.Ticker("BBAS3.SA").history(period=period))   # Usando BB como mínimo de histórico (vai até ~2000)

        for stock in stocks_to_analyse:
            hist = yf.Ticker(stock).history(period=period)

            if not hist.empty:
                has_nan = hist.isnull().values.any()
                has_sufficient_data = len(hist) >= min_expected_days
                if not has_nan and has_sufficient_data:
                    self.cleaned_stocks_list.append(stock)
        

    def random_selection(self, number_of_stocks: int =5, period: str="3Y") -> list[str]:

        self.random_stocks_list = [] # make sure to always re-do the portfolio for every call
        self.cleaned_stocks_list = []

        self.period = period

        while len(self.random_stocks_list) < number_of_stocks:
            aux = random.sample(self.stocks_names, number_of_stocks)
            self.cleaned_stocks(aux, period)

            for stock in self.cleaned_stocks_list:
                if stock not in self.random_stocks_list and len(self.random_stocks_list) != number_of_stocks:
                    self.random_stocks_list.append(stock) 

        return self.random_stocks_list


    def calculate_returns(self, selected_stocks: list[str], period: str) -> pd.DataFrame:
        self.stocks_returns = yf.Tickers(selected_stocks).history(period=period)['Close'].pct_change()
        return self.stocks_returns
        
