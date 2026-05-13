import pandas as pd
import numpy as np
from scipy.optimize import minimize


def choose_strategy(df, choose=False):
    if choose == True:
        strategy = int(input(f'''choose your strategy: \n
                            
                            1: equal weights \n
                            2: random weights\n
                            
                            '''))
        
        trials = 0
        max = 3

        if strategy == 1:
            return equal_weights(df)
        if strategy == 2:
            return random_weights(df)
        if trials > max:
            return 0
        else:
            print("strategy non existent, try another one")
            trials +=1
            print(f'trials left: {max - trials}')
    else:
        return equal_weights(df)


def equal_weights(df):
    weights = pd.Series([1/len(df.columns)]*len(df.columns), index=df.columns)
    return weights


def random_weights(df):
    n = len(df.columns)
    random_list = np.random.uniform(0, 100, n)
    normalized_weights = random_list/random_list.sum()
    return pd.Series(normalized_weights, index=df.columns)


def min_variance_weights(df):
    cov_matrix = df.cov().values * 252
    num_assets = len(df.columns) 

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
    weights_min_var = pd.Series(weights, index=df.columns, name="Weights")
    return weights_min_var