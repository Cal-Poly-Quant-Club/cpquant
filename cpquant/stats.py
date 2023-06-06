from data import AlpacaDataClient
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def correlation_matrix():
    dataClient = AlpacaDataClient()
    msft = dataClient.get_bars("MSFT", "1Min", start="2020-01-01", end="2020-01-02", only_market=True)
    aapl = dataClient.get_bars("AAPL", "1Min", start="2020-01-01", end="2020-01-02", only_market=True)
    goog = dataClient.get_bars("GOOG", "1Min", start="2020-01-01", end="2020-01-02", only_market=True)


    msf = msft.add_prefix('msft_')
    aap = aapl.add_prefix('aapl_')
    goo = goog.add_prefix('goog_')
    df = pd.concat([msf, aap, goo], axis=1)
    correlation_matrix = df.corr()

    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')

    plt.title('Correlation matrix heatmap')
    plt.show()

def pairs_trading_demo():
    dataClient = AlpacaDataClient()


    msft = dataClient.get_bars("MSFT", "1Min", start="2020-01-01", end="2020-01-02", only_market=True)
    aapl = dataClient.get_bars("AAPL", "1Min", start="2020-01-01", end="2020-01-02", only_market=True)
    goog = dataClient.get_bars("GOOG", "1Min", start="2020-01-01", end="2020-01-02", only_market=True)
    aapl = aapl["close"]
    msft = msft["close"]

    print(aapl)

    spread = aapl - msft
    # nomralize spread
    spread = (spread - spread.mean()) / spread.std()
    # plot spread
    plt.plot(spread)
    # normalize aapl
    aapl = (aapl - aapl.mean()) / aapl.std()
    # plot aapl
    plt.plot(aapl)
    # normalize msft
    msft = (msft - msft.mean()) / msft.std()
    # plot msft
    plt.plot(msft)
    plt.show()

    # Define two boundaries for buy/sell signals
    z_buy = -1.0  # Z-score value to buy spread
    z_sell = 1.0  # Z-score value to sell spread

    # Generate signals
    signals = pd.Series(index=spread.index, dtype=np.int32)
    signals[spread < z_buy] = 1.0  # Buy signal
    signals[spread > z_sell] = -1.0  # Sell signal
    # set nan to 0
    signals = signals.fillna(0.0)
    # Forward fill signals
    signals = signals.ffill()

    # Plot
    plt.figure(figsize=(15, 7))
    plt.plot(spread.index, spread.values, label='Rolling 20 day Z score')
    plt.fill_between(spread.index, z_buy, z_sell, color='gray', alpha=0.2)
    plt.title('Z-score evolution with trading signals')
    plt.show()

correlation_matrix()