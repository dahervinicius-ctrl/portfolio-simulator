import pandas as pd
import yfinance as yf
import numpy as np


def overview(port, ibov=True):

    if ibov==True:
        ibov = yf.download("^BVSP", start=port.index[0])["Close"]
        analysis = pd.concat([port, ibov], axis=1)
    
    print(f'total return (index = 1): {analysis.iloc[-1]/analysis.iloc[0]} \n')
    print(f'standard deviation in %: {100* (np.std(analysis)/np.mean(analysis))}')

    analysis = analysis/analysis.iloc[0]

    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))

    plt.plot(analysis)

    plt.title('Stock Performance History', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('return (indexed to 1)', fontsize=12)
    plt.legend(analysis.columns, loc='upper left')
    plt.show()
    