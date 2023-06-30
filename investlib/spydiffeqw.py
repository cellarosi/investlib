import base64
import pandas as pd
from data import Tiingo
import plotly.graph_objects as go


tiingo = Tiingo('dd3b82b63e3dd1a4caa7c7658a2942977cef280a', backup_path='/tmp/studies/Tiingo')

data = tiingo.load(['SPY', 'RSP', 'GLD','TLT','GSC'], start='2005-10-01')

spy = data['SPY']
rsp = data['RSP']
gld = data['GLD']
tlt = data['TLT']
gsc = data['GSC']
rsp.loc[:,'close'] = rsp['close']*rsp['splitFactor'].cummax()
diff = ((spy['close'].pct_change()-rsp['close'].pct_change())*100).round(2).rolling(window=250).mean()

pct_spy = spy['close'].pct_change().rolling(window=60).mean()*100
pct_gsc = gsc['close'].pct_change().rolling(window=60).mean()*100
diff = (pct_spy-pct_gsc).round(2)


idx = []
r=False
for i in diff.index:
    d=diff.loc[i]
    if d>0.2:
        r=True
    
    if d<-0.2:
        r=False

    if r==True:
        idx.append(i)

riskoff = pd.Series(index=spy.index)
riskoff.loc[idx] = spy.loc[idx,'close']



fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=spy['close'], name='SPY', yaxis='y1'))
#fig.add_trace(go.Scatter(x=gld.index, y=gld['close'], name='GLD',yaxis='y1'))
fig.add_trace(go.Scatter(x=gsc.index, y=gsc['close'], name='gsc',yaxis='y1'))
fig.add_trace(go.Scatter(x=data.index, y=riskoff, name='ROFF',yaxis='y1'))
fig.add_trace(go.Scatter(x=data.index, y=diff, name='DIFF',yaxis='y2'))
fig.update_layout(
    yaxis2=dict(
        title='Dati 2',
        overlaying='y',
        side='right'
    )
)

fig.show()


corr = pd.DataFrame(index=idx)
corr['spy'] = (spy.loc[idx, 'close'].pct_change()*100).round(2)
corr['gld'] = (gld.loc[idx, 'close'].pct_change()*100).round(2)
corr['tlt'] = (tlt.loc[idx, 'close'].pct_change()*100).round(2)

print(corr.corr())

