import pandas as pd
import numpy as np


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