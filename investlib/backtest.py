import base64
import pandas as pd
from data import Tiingo
import plotly.graph_objects as go


tiingo = Tiingo('dd3b82b63e3dd1a4caa7c7658a2942977cef280a', backup_path='/tmp/studies/Tiingo')
tickers = [
    'XLK',  # Technology
    'XLF',  # Financials
    'XLV',  # Health Care
    'XLY',  # Consumer Discretionary
    'XLP',  # Consumer Staples
    'XLE',  # Energy
    'XLI',  # Industrials
    'XLB',  # Materials
    'XLRE',  # Real Estate
    'XLU',  # Utilities
    'XLC',  # Communication Services
]

data = tiingo.load(tickers, start='2005-01-01', end='2022-12-31')
spy = tiingo.load(['SPY'], start='2005-01-01', end='2022-12-31')
spy = spy['SPY']['close']

data.loc[:,('XLK','close')] = data.loc[:,('XLK','close')]*data.loc[:,('XLK','splitFactor')].cummax()
data.loc[:,('XLF','close')] = data.loc[:,('XLF','close')]*data.loc[:,('XLF','splitFactor')].cummax()
data.loc[:,('XLV','close')] = data.loc[:,('XLV','close')]*data.loc[:,('XLV','splitFactor')].cummax()
data.loc[:,('XLY','close')] = data.loc[:,('XLY','close')]*data.loc[:,('XLY','splitFactor')].cummax()
data.loc[:,('XLP','close')] = data.loc[:,('XLP','close')]*data.loc[:,('XLP','splitFactor')].cummax()
data.loc[:,('XLE','close')] = data.loc[:,('XLE','close')]*data.loc[:,('XLE','splitFactor')].cummax()
data.loc[:,('XLI','close')] = data.loc[:,('XLI','close')]*data.loc[:,('XLI','splitFactor')].cummax()
data.loc[:,('XLB','close')] = data.loc[:,('XLB','close')]*data.loc[:,('XLB','splitFactor')].cummax()
data.loc[:,('XLRE','close')] = data.loc[:,('XLRE','close')]*data.loc[:,('XLRE','splitFactor')].cummax()
data.loc[:,('XLU','close')] = data.loc[:,('XLU','close')]*data.loc[:,('XLU','splitFactor')].cummax()
data.loc[:,('XLC','close')] = data.loc[:,('XLC','close')]*data.loc[:,('XLC','splitFactor')].cummax()

rend = data.loc[:, (slice(None),'close')].pct_change().droplevel(1, axis=1).fillna(0)

rend3m = data.loc[:, (slice(None),'close')].pct_change(periods=90).droplevel(1, axis=1).fillna(0)
strategy = pd.Series(index=rend.index).fillna(0)

etf_exposition = rend3m.apply(lambda row: row.dropna().nsmallest(3).index.tolist(), axis=1).shift(1)
print(etf_exposition)
#expositions = pd.DataFrame(index=rend.index, columns=['IVV','IWR','IWM']).fillna(0)
for idx, col in etf_exposition[1:].iteritems():
    strategy[idx] = rend.loc[idx, col].mean()
    
    #expositions.loc[idx] = [0,0,0] 
    #expositions.loc[idx, col] = 1 

#bench_eq = pd.Series([1] + rend['SPY']).cumprod()*10000
strategy = pd.Series([1] + strategy).cumprod()*10000



spy = pd.Series([1] + spy.pct_change()).cumprod()*10000 

fig = go.Figure()
fig.add_trace(go.Scatter(x=strategy.index, y=strategy, name='strategy', yaxis='y1'))
fig.add_trace(go.Scatter(x=strategy.index, y=(strategy/strategy.cummax()-1)*100, name='DD', yaxis='y2'))
fig.add_trace(go.Scatter(x=spy.index, y=spy, name='SPY', yaxis='y1'))
#fig.add_trace(go.Scatter(x=expositions.index, y=expositions['IVV'], name='IVVexpositions', yaxis='y1'))
#fig.add_trace(go.Scatter(x=expositions.index, y=expositions['IWR'], name='IWRexpositions', yaxis='y1'))
#fig.add_trace(go.Scatter(x=expositions.index, y=expositions['IWM'], name='IWMexpositions', yaxis='y1'))
#fig.add_trace(go.Scatter(x=data.index, y=real_close['IWM'], name='IWM', yaxis='y2'))
#fig.add_trace(go.Scatter(x=data.index, y=bench_eq, name='SPY', yaxis='y2'))
#fig.add_trace(go.Scatter(x=data.index, y=close['IVV'], name='Large cap', yaxis='y1'))
#fig.add_trace(go.Scatter(x=data.index, y=close['IWR'], name='Mid Cap', yaxis='y1'))
#fig.add_trace(go.Scatter(x=data.index, y=close['IWM'], name='Small cap', yaxis='y1'))
#fig.add_trace(go.Scatter(x=data.index, y=ro, name='ro', yaxis='y2'))
fig.update_layout(
    yaxis2=dict(
        title='Dati 2',
        overlaying='y',
        side='right'
    )
)
fig.show()



