import strategies

import yfinance as yf
from yfinance import EquityQuery
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

def screener(market_cap = 10000000000):
    local_stocks = []
    foreign_stocks = []

    filters = [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('gte',['intradaymarketcap', market_cap])
    ]

    query = EquityQuery('and', filters)
    offset = 0
    size = 200

    fim = 1

    while fim != 0:

        response = yf.screen(query, offset = offset, sortField = 'intradaymarketcap', sortAsc = False, size = size)

        lista = response['quotes']

        old_len = len(local_stocks)

        for stock in lista:
            if stock['symbol'].endswith("34.SA") or stock['symbol'].endswith("35.SA"):
                foreign_stocks.append(stock) 
            else:
                local_stocks.append(stock)

        fim = len(local_stocks) - old_len
        offset += size

    return local_stocks


def cleaned_stocks(local_stocks, period):

    valid_local_stocks = []
    min_expected_days = len(yf.Ticker("BBAS3.SA").history(period=period))    # Usando BB como mínimo de histórico (vai até ~2000)

    for stock in local_stocks:
        hist = yf.Ticker(stock['symbol']).history(period=period)

        if not hist.empty:
            has_nan = hist.isnull().values.any()
            has_sufficient_data = len(hist) >= min_expected_days
            if not has_nan and has_sufficient_data:
                valid_local_stocks.append(stock)
    
    return valid_local_stocks


def clean_summary(dict):

    print(f'name: {dict['symbol']}')
    
    try:
        print(f'price: {dict['regularMarketPrice']:.2f}')
    except:
        print(f'price: N/A')        

    try:
        print(f'52W range: {dict['fiftyTwoWeekRange']:.2f}')
    except:
        print(f'52W range: N/A')
        
    try:
        print(f'LTM D.Y: {100*dict['trailingAnnualDividendYield']:.2f}%')
    except:
        print(f'LTM D.Y: N/A')

    try:
        print(f'LTM P/E: {dict['forwardPE']:.2f}')
    except:
        print(f'LTM P/E: N/A')

    try:
        print(f'1Y Forward P/E: {dict['forwardPE']:.2f}')
    except:
        print(f'1Y Forward P/E: N/A')

    try:
        print(f'current P/B: {dict['priceToBook']:.2f}')
    except:
        print(f'current P/B: N/A')


def random_portfolio(number_of_stocks=5, period="3Y"):

    local_stocks = screener()
    random_list_names = []

    while len(random_list_names) != number_of_stocks:
        random_list = random.sample(local_stocks, number_of_stocks)
        stocks = cleaned_stocks(random_list, period)
        for stock in stocks:
            if stock["symbol"] not in random_list_names and len(random_list_names) != number_of_stocks:
                random_list_names.append(stock["symbol"])

    df = yf.Tickers(random_list_names).history(period = period)

    close_df = df["Close"]

    return close_df


def test_port(period = "1mo"):
    df = yf.Tickers(["BBAS3.SA", "ITUB4.SA"]).history(period = period)
    close_df = df["Close"]
    return close_df


def rebalance(df_1, weights, volume_fee = 0.001):
    
    rebalance = weights * df_1.iloc[-1].sum() - df_1.iloc[-1][weights.index]
    vol_fee = np.absolute(rebalance) * volume_fee
    rebalance = rebalance - volume_fee
    print(f'rebalance at: {df_1.index[-1]} \n')
    print(f'post fee rebalance: {rebalance[weights.index]} (total fee: {vol_fee.sum()}) \n')
    return rebalance



'''

def make_portfolio(port, rebalancement_frequency=10, volume_fee = 0, initial_investment=1000):

    for i in range(int(np.floor(len(port)/rebalancement_frequency))):

        aux1 = rebalancement_frequency*(i)
        aux2 = rebalancement_frequency*(i+1)

        weights = strategies.choose_strategy(port.iloc[aux1:aux2])
        perc = (port[weights.index].pct_change() + 1)

        if i == 0:
            capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * weights * initial_investment
            capital_aloc.iloc[0] = weights * initial_investment
            port_df = capital_aloc
        else:
            rebalancement = rebalance(capital_aloc, weights, volume_fee)
            capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
            port_df = pd.concat([port_df, capital_aloc])

    rebalancement = rebalance(capital_aloc, weights, volume_fee)
    capital_aloc = perc.iloc[aux2:][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
    port_df = pd.concat([port_df, capital_aloc])
    port_df["portfolio"] = port_df.sum(axis=1)

    return port_df    
'''

def make_portfolio(port, rebalancement_frequency=10, volume_fee = 0, initial_investment=1000):
    strategies.choose_strategy() #based on the strategy to be used, need to call different "make_portfolio" functions for each strategy 



def make_min_variance_portfolio(port, rebalancement_frequency=30, volume_fee = 0, initial_investment=1000, aggregate=False):

    weights = strategies.equal_weights(port) #initialize strategy with equal weights
    returns = port[weights.index].pct_change()

    for i in range(int(np.floor(len(port)/rebalancement_frequency))):

        aux1 = rebalancement_frequency*(i)
        aux2 = rebalancement_frequency*(i+1)

        if aggregate == True:

            if i == 0:
                capital_aloc = (returns + 1).iloc[aux1:aux2][weights.index].cumprod() * weights * initial_investment
                capital_aloc.iloc[0] = weights * initial_investment
                port_df = capital_aloc
            else:
                weights = strategies.min_variance_weights(returns.iloc[1:aux2])
                rebalancement = rebalance(capital_aloc, weights, volume_fee)
                capital_aloc = (returns + 1).iloc[aux1:aux2][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
                port_df = pd.concat([port_df, capital_aloc])

        if aggregate == False:

            if i == 0:
                capital_aloc = (returns + 1).iloc[aux1:aux2][weights.index].cumprod() * weights * initial_investment
                capital_aloc.iloc[0] = weights * initial_investment
                port_df = capital_aloc
            else:
                weights = strategies.min_variance_weights(returns.iloc[aux1:aux2])
                rebalancement = rebalance(capital_aloc, weights, volume_fee)
                capital_aloc = (returns + 1).iloc[aux1:aux2][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
                port_df = pd.concat([port_df, capital_aloc])


    rebalancement = rebalance(capital_aloc, weights, volume_fee)
    capital_aloc = (returns + 1).iloc[aux2:][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
    port_df = pd.concat([port_df, capital_aloc])
    port_df["portfolio"] = port_df.sum(axis=1)

    return port_df


def make_equal_weight_portfolio(port, rebalancement_frequency=30, volume_fee = 0, initial_investment=1000):

    weights = strategies.equal_weights(port)

    for i in range(int(np.floor(len(port)/rebalancement_frequency))):

        aux1 = rebalancement_frequency*(i)
        aux2 = rebalancement_frequency*(i+1)

        perc = (port[weights.index].pct_change() + 1)

        if i == 0:
            capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * weights * initial_investment
            capital_aloc.iloc[0] = weights * initial_investment
            port_df = capital_aloc
        else:
            rebalancement = rebalance(capital_aloc, weights, volume_fee)
            capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
            port_df = pd.concat([port_df, capital_aloc])

    rebalancement = rebalance(capital_aloc, weights, volume_fee)
    capital_aloc = perc.iloc[aux2:][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
    port_df = pd.concat([port_df, capital_aloc])
    port_df["portfolio"] = port_df.sum(axis=1)

    return port_df

def make_random_weight_portfolio(port, rebalancement_frequency=30, volume_fee = 0, initial_investment=1000):

    weights = strategies.random_weights(port)

    for i in range(int(np.floor(len(port)/rebalancement_frequency))):

        aux1 = rebalancement_frequency*(i)
        aux2 = rebalancement_frequency*(i+1)

        perc = (port[weights.index].pct_change() + 1)

        if i == 0:
            capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * weights * initial_investment
            capital_aloc.iloc[0] = weights * initial_investment
            port_df = capital_aloc
        else:
            rebalancement = rebalance(capital_aloc, weights, volume_fee)
            capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
            port_df = pd.concat([port_df, capital_aloc])

    rebalancement = rebalance(capital_aloc, weights, volume_fee)
    capital_aloc = perc.iloc[aux2:][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
    port_df = pd.concat([port_df, capital_aloc])
    port_df["portfolio"] = port_df.sum(axis=1)

    return port_df

def portfolio_stats(port):
    pass