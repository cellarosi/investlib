import csv, os, json
import requests
from datetime import datetime
import pandas as pd


class Tiingo:
    base_url = "https://api.tiingo.com/tiingo/daily/{}/prices?token={}&startDate={}"
    usecols=['date','open','close','divCash','splitFactor', 'adjClose']
    
    def __init__(self, api_key,backup_path=None):
        self.api_key = api_key
        self.backup_path = backup_path if backup_path else '/tmp/Tiingo'
        config = dict(
            session=True,
            api_key=api_key
        )
        
    def fix_end(self, date):
        if not date or pd.to_datetime(date).date() >= pd.to_datetime(datetime.now()).date():
            date = (pd.to_datetime(datetime.now()) - pd.DateOffset(days=5)).strftime("%Y-%m-%d")
        return date
    
    def download(self, ticker):
        headers = {
            'Content-Type': 'application/json'
        }
        res = requests.get(self.base_url.format(ticker, self.api_key, '1900-01-01'), headers=headers)
        if res.status_code==200:
            data = res.json()
        else:
            raise Exception('Error downloading ticker {} from api'.format(ticker))
        tk_df = pd.DataFrame(data)
        tk_df.set_index('date', inplace=True)
        tk_df.to_csv('{}/{}'.format(self.backup_path, ticker))

    def get_url(self, ticker):
        return '{}/{}'.format(self.backup_path, ticker)

    def download_needed(self, ticker_or_buffer, end):
        buffer = ticker_or_buffer
        if isinstance(buffer, str):
            path = self.get_url(buffer)
            
            if not os.path.exists(path):
                return True
            else:
                buffer = open(path, 'r') 
        df = pd.read_csv(buffer, parse_dates=True, index_col=['date'],usecols=self.usecols)
        buffer.close()
        df.index = df.index.date
        end = pd.to_datetime(end).date()
        if end>df.index[-1]:
            return True
        return False

    def read(self, ticker_or_buffer, start=None, end=None):
        buffer = ticker_or_buffer
        if isinstance(buffer, str):
            path = self.get_url(buffer)
            if not os.path.exists(path):
                raise Exception('No file for ticker {}'.format(buffer))
            else:
                buffer = open('{}/{}'.format(self.backup_path,buffer), 'r') 
        
        df = pd.read_csv(buffer, parse_dates=True, index_col=['date'],usecols=self.usecols)
        
        #df = df.resample('D').asfreq()
        #df[['open','close', 'adjClose','splitFactor']] = df[['open','close', 'adjClose','splitFactor']].ffill()
        #df = df.fillna(0)

        df.index = pd.DatetimeIndex(df.index.date)
        
        if start:
            df=df.loc[start:]
        if end:
            df=df.loc[:end]
        
        buffer.close()
        return df

    def load(self, tickers, start=None, end=None):
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)

        end = self.fix_end(end)

        if(start and start>end):
            raise Exception('Start date must be greater than end date')  
        series = [] 
        
        for ticker in tickers:
            if self.download_needed(ticker, end):
                self.download(ticker)
            series.append(self.read(ticker, start, end))
            

        return pd.concat(series, keys=tickers, axis=1, join='outer')  
