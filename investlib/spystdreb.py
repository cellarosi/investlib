import base64
import pandas as pd
from data import Tiingo
import plotly.graph_objects as go


tiingo = Tiingo('dd3b82b63e3dd1a4caa7c7658a2942977cef280a', backup_path='/tmp/studies/Tiingo')

data = tiingo.load(['SPY','IVV','IWR','IWM'], start='1999-09-01')

data.loc[:,('SPY','close')] = data.loc[:,('SPY','close')]*data.loc[:,('SPY','splitFactor')].cummax()
data.loc[:,('IVV','close')] = data.loc[:,('IVV','close')]*data.loc[:,('IVV','splitFactor')].cummax()
data.loc[:,('IWR','close')] = data.loc[:,('IWR','close')]*data.loc[:,('IWR','splitFactor')].cummax()
data.loc[:,('IWM','close')] = data.loc[:,('IWM','close')]*data.loc[:,('IWM','splitFactor')].cummax()

rend = data.loc[:, (slice(None),'close')].pct_change().droplevel(1, axis=1).fillna(0)
rend3m = data.loc[:, (slice(None),'close')].pct_change(periods=250).droplevel(1, axis=1).fillna(0)

prices = data.loc[:,(slice(None),'close')].droplevel(1, axis=1)

idx = rend3m[rend3m['IWR']<rend3m['SPY']].index
strategy = rend['IWR']
strategy.loc[idx] = rend.loc[idx,'SPY']
#idx2 = rend3m[rend3m['IWR']<0].index
#strategy.loc[idx2] = 0

strategy = strategy.shift(1)

eq=pd.Series([1] + strategy).cumprod()*10000

fig = go.Figure()
#fig.add_trace(go.Scatter(x=data.index, y=data['SPY']['close'], name='SPY', yaxis='y1'))
fig.add_trace(go.Scatter(x=data.index, y=pd.Series([1] + prices['SPY'].pct_change()).cumprod()*10000 , name='SPY', yaxis='y1'))
fig.add_trace(go.Scatter(x=data.index, y=pd.Series([1] + prices['IVV'].pct_change()).cumprod()*10000, name='IVV Large', yaxis='y1'))
fig.add_trace(go.Scatter(x=data.index, y=pd.Series([1] + prices['IWR'].pct_change()).cumprod()*10000, name='IWR Mid', yaxis='y1'))
fig.add_trace(go.Scatter(x=data.index, y=pd.Series([1] + prices['IWM'].pct_change()).cumprod()*10000, name='IWM Small', yaxis='y1'))
fig.add_trace(go.Scatter(x=data.index, y=eq, name='strategy', yaxis='y1'))
fig.add_trace(go.Scatter(x=data.index, y=(eq/eq.cummax()-1)*100, name='eq cap', yaxis='y2'))
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



