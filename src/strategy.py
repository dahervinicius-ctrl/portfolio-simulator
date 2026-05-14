import pandas as pd
import numpy as np
from scipy.optimize import minimize

from .stocks import Stocks

# think about how to implement a more robust linkage to the stocks class to get the analysed period without problems

class Strategy():

    def __init__(self,
                 stocks: list[str], 
                 period: str = '3Y',
                 strategy_type: str = 'equal_weights', 
                 aggregate: bool = True,
                 initial_capital: float = 1000, 
                 have_rebalancement: bool = True,
                 rebalancement_frequency: int = 30,
                 volume_fee: float = 0.01
                 ):
        
        self.period = period
        self.strategy_type = strategy_type
        self.composition = stocks
        self.returns = Stocks(stocks).calculate_returns(stocks, period)
        self.rebalancement_frequency = rebalancement_frequency
        self.initial_capital = initial_capital
        self.have_rebalancement = have_rebalancement
        self.volume_fee = volume_fee
        self.aggregate = aggregate

    
    def rebalance(self, df_1, weights):
    
        rebalance = weights * df_1.iloc[-1].sum() - df_1.iloc[-1][weights.index]
        vol_fee = np.absolute(rebalance) * self.volume_fee
        rebalance = rebalance - vol_fee
        #print(f'rebalance at: {df_1.index[-1]} \n')
        #print(f'post fee rebalance: {rebalance[weights.index]} (total fee: {vol_fee.sum()}) \n')
        return rebalance
    

    def apply_equal_weights(self):

        weights = self.create_equal_weights()
        perc = (self.returns[weights.index] + 1)

        if self.have_rebalancement == True:

            for i in range(int(np.floor(len(self.returns)/self.rebalancement_frequency))):

                aux1 = self.rebalancement_frequency*(i)
                aux2 = self.rebalancement_frequency*(i+1)

                if i == 0:
                    capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * weights * self.initial_capital
                    capital_aloc.iloc[0] = weights * self.initial_capital
                    portfolio_composition = capital_aloc
                else:
                    rebalancement = self.rebalance(capital_aloc, weights)
                    capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
                    portfolio_composition = pd.concat([portfolio_composition, capital_aloc])

            rebalancement = self.rebalance(capital_aloc, weights)
            capital_aloc = perc.iloc[aux2:][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
            portfolio_composition = pd.concat([portfolio_composition, capital_aloc])

        elif self.have_rebalancement == False:
            capital_aloc = perc[weights.index].cumprod() * weights * self.initial_capital
            capital_aloc.iloc[0] = weights * self.initial_capital
            portfolio_composition = capital_aloc

        return portfolio_composition

    def apply_random_weights(self):

        weights = self.create_random_weights()
        perc = (self.returns[weights.index] + 1)

        if self.have_rebalancement == True:

            for i in range(int(np.floor(len(self.returns)/self.rebalancement_frequency))):

                weights = self.create_random_weights()

                aux1 = self.rebalancement_frequency*(i)
                aux2 = self.rebalancement_frequency*(i+1)

                if i == 0:
                    capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * weights * self.initial_capital
                    capital_aloc.iloc[0] = weights * self.initial_capital
                    portfolio_composition = capital_aloc
                else:
                    rebalancement = self.rebalance(capital_aloc, weights, self.volume_fee)
                    capital_aloc = perc.iloc[aux1:aux2][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
                    portfolio_composition = pd.concat([portfolio_composition, capital_aloc])

            rebalancement = self.rebalance(capital_aloc, weights, self.volume_fee)
            capital_aloc = perc.iloc[aux2:][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
            portfolio_composition = pd.concat([portfolio_composition, capital_aloc])

        elif self.have_rebalancement == False:
            capital_aloc = perc[weights.index].cumprod() * weights * self.initial_capital
            capital_aloc.iloc[0] = weights * self.initial_capital
            portfolio_composition = capital_aloc

        return portfolio_composition


    def apply_min_variance_weights(self):

        weights = self.create_equal_weights() #initialize strategy with equal weights

        for i in range(int(np.floor(len(self.returns)/self.rebalancement_frequency))):

            aux1 = self.rebalancement_frequency*(i)
            aux2 = self.rebalancement_frequency*(i+1)

            if self.aggregate == True:

                if i == 0:
                    capital_aloc = (self.returns + 1).iloc[aux1:aux2][weights.index].cumprod() * weights * self.initial_capital
                    capital_aloc.iloc[0] = weights * self.initial_capital
                    portfolio_composition = capital_aloc
                else:
                    weights = self.create_min_variance_weights(self.returns.iloc[1:aux2])
                    rebalancement = self.rebalance(capital_aloc, weights)
                    capital_aloc = (self.returns + 1).iloc[aux1:aux2][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
                    portfolio_composition = pd.concat([portfolio_composition, capital_aloc])

            if self.aggregate == False:

                if i == 0:
                    capital_aloc = (self.returns + 1).iloc[aux1:aux2][weights.index].cumprod() * weights * self.initial_capital
                    capital_aloc.iloc[0] = weights * self.initial_capital
                    portfolio_composition = capital_aloc
                else:
                    weights = self.create_min_variance_weights(self.returns.iloc[aux1:aux2])
                    rebalancement = self.rebalance(capital_aloc, weights)
                    capital_aloc = (self.returns + 1).iloc[aux1:aux2][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
                    portfolio_composition = pd.concat([portfolio_composition, capital_aloc])


        rebalancement = self.rebalance(capital_aloc, weights)
        capital_aloc = (self.returns + 1).iloc[aux2:][weights.index].cumprod() * (capital_aloc.iloc[-1] + rebalancement)
        portfolio_composition = pd.concat([portfolio_composition, capital_aloc])

        return portfolio_composition



    def create_equal_weights(self):
        self.weights = pd.Series([1/len(self.returns.columns)]*len(self.returns.columns), index=self.returns.columns)
        return self.weights
    

    def create_random_weights(self):
        random_list = np.random.uniform(0, 100, len(self.composition))
        normalized_weights = random_list/random_list.sum()
        self.weights = pd.Series(normalized_weights, index=self.returns.columns)
        return self.weights
        

    def create_min_variance_weights(self, df_1):
        cov_matrix = df_1.cov().values * 252
        num_assets = len(self.composition)

        def portfolio_variance(weights):
            return weights.T @ cov_matrix @ weights

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        init_guess = num_assets * [1. / num_assets]
        
        optimized_results = minimize(portfolio_variance, 
                                init_guess, 
                                method='SLSQP', 
                                bounds=bounds, 
                                constraints=constraints)
        
        weights = optimized_results.x
        self.weights = pd.Series(weights, index=df_1.columns, name="Weights")
        return self.weights

    