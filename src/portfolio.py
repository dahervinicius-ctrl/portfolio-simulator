import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from .strategy import Strategy



class Portfolio():
    def __init__(self, strategy: Strategy, name: str):

        self.strategy = strategy
        self.composition = strategy.composition
        self.strategy_type = strategy.strategy_type
        self.initial_capital = strategy.initial_capital
        self.rebalancement_frequency = strategy.rebalancement_frequency
        self.have_rebalancement = strategy.have_rebalancement
        self.volume_fee = strategy.volume_fee
        self.name = name

        self.possible_types = ['equal_weights', 'random_weights', 'min_variance_weights']

        self.portfolio_composition = None
        self.portfolio_total = None


    def create_port(self):
        if self.strategy_type == 'equal_weights':
            self.portfolio_composition = self.strategy.apply_equal_weights()

        elif self.strategy_type == 'random_weights':
            self.portfolio_composition = self.strategy.apply_random_weights()
        
        elif self.strategy_type == 'min_variance_weights':
            self.portfolio_composition = self.strategy.apply_min_variance_weights()

        else:
            print(f'Cannot simulate strategy type: {self.strategy_type}')
            return 0
                
        self.portfolio_total = self.portfolio_composition.sum(axis=1)
        return self.portfolio_composition
        

    def analyse(self, ibov: bool = True):

        analysis = self.portfolio_total
        analysis = analysis.to_frame(name = self.name)

        if ibov==True:
            ibov = yf.download("^BVSP", start=self.portfolio_composition.index[0])["Close"]
            ibov.columns = ['IBOV']
            analysis = pd.concat([analysis, ibov], axis=1)
    
        print(f'total return (index = 1):\n{analysis.iloc[-1]/analysis.iloc[0]} \n')
        print(f'standard deviation in %:\n{100 * np.std(analysis.pct_change().dropna())}%')

        analysis = analysis/analysis.iloc[0]

        plt.figure(figsize=(12, 6))

        plt.plot(analysis)

        plt.title('Performance Comparison', fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('return (indexed to 1)', fontsize=12)
        plt.legend(analysis.columns, loc='upper left')
        plt.show()






