

from tiingo import TiingoClient
import pandas as pd

tickers = [
    'SPY'
]

config = {}

# To reuse the same HTTP Session across API calls (and have better performance), include a session key.
config['session'] = True

# If you don't have your API key as an environment variable,
# pass it in via a configuration dictionary.
config['api_key'] = "dd3b82b63e3dd1a4caa7c7658a2942977cef280a"

# Initialize
for ticker in tickers:
    client = TiingoClient(config)
    data = client.get_ticker_price(ticker,
                                fmt='json',
                                startDate='1900-01-01',
                                frequency='daily')

    t = pd.DataFrame(data)
    t.index = pd.DatetimeIndex(data=pd.to_datetime(t.date).dt.date)
    t.drop(columns='date', inplace=True)
    t.to_csv('./data/Tiingo/{}.csv'.format(ticker))
