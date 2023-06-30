import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
pd.options.plotting.backend = "plotly"
import math

class Portfolio:

    def __init__(self, instruments, allocations, initial_balance=100000):
        self.tickers = np.unique(instruments.columns.get_level_values(0).tolist())
        self.initial_balance = initial_balance
        self.instruments = instruments
        self.allocations = allocations

    def get_total_years(self, start, end):
        start_year = start.year
        start_month = start.month
        start_day = start.day
        end_year = end.year
        end_month = end.month
        end_day = end.day
        return round(end_year-start_year+(end_month-start_month)/12+(end_day-start_day)/365,1)
    
    def get_cagr(self, start_money, end_money, years):
        cagr = (end_money / start_money) ** (1 / years) - 1
        return round(cagr*100,1)

    def get_net_profit(self, start_money, end_money):
        return round(((end_money/start_money-1)*100),1)

    def get_stats(self):
        years = self.get_total_years(self.eq.index[1], self.eq.index[-1])

        return dict(
            cagr=self.get_cagr(self.eq.iloc[0],self.eq.iloc[-1], years),
            net_profit_money=self.eq.iloc[-1],
            net_profit_perc=self.get_net_profit(self.eq.iloc[0],self.eq.iloc[-1]),
            max_dd_perc=self.dd.min().round(1),
            max_dd_money=self.dd_money.min().round(1)
        )

    def run(self):
        instruments = self.instruments
        
        cash = pd.Series(index=instruments.index, dtype='float64').fillna(0)
        div = pd.Series(index=instruments.index, dtype='float64').fillna(0)
        eq = pd.Series(index=instruments.index, dtype='float64').fillna(0)

        multi_idx = pd.MultiIndex.from_product([self.tickers,['close', 'shares', 'total_shares',  'endmonth']], names=['ticker', ''])
        pf = pd.DataFrame(columns=multi_idx,index=instruments.index, dtype='float64').fillna(0)
        
        i_lev1 = instruments.columns.get_level_values(1)
        pf_lev1 = pf.columns.get_level_values(1)

        pf.loc[:,(slice(None), 'close')] = instruments.loc[:,(slice(None),'close')]
        cash.iloc[0] = self.initial_balance
        eq.iloc[0] = self.initial_balance


        for month in pf.index[1:]:
            prev = pf.shift(1)
            tot_capital =eq.shift(1)[month]
            to_allocate= tot_capital*self.allocations.loc[month]
            
            current_using =  prev.loc[month, pf_lev1=='endmonth'].droplevel(1)
            used = (to_allocate-current_using)
            price = instruments.shift(1).loc[month,i_lev1=='close'].droplevel(level=1)
            ll = (used/price).apply(lambda x: math.floor(x) if x < 0 else int(x))
            pf.loc[month,pf_lev1=='shares'] = ll.tolist() # Boh. Senza tolist non va
            pf.loc[month,pf_lev1=='total_shares'] = (prev.loc[month,pf_lev1=='total_shares'].droplevel(1)+pf.loc[month,pf_lev1=='shares'].droplevel(1)).tolist()
            new_position = pf.loc[month,pf_lev1=='shares'].droplevel(level=1)*instruments.shift(1).loc[month,i_lev1=='close'].droplevel(1)
            pf.loc[month,pf_lev1=='endmonth'] = (pf.loc[month,pf_lev1=='total_shares'].droplevel(level=1)*instruments.loc[month,i_lev1=='close'].droplevel(level=1)).tolist()
            div.loc[month]=(instruments.loc[month,i_lev1=='divCash'].droplevel(1)*pf.loc[month,pf_lev1=='total_shares'].droplevel(1)).sum()
            cash.loc[month] = cash.shift(1).loc[month]-new_position.sum()+div.loc[month]
            
            eq.loc[month] = pf.loc[month,pf_lev1=='endmonth'].sum()+cash[month]
        eq = eq.round(2)
        returns = eq.copy()
        grid = returns.copy()
        
        grid.index = pd.MultiIndex.from_arrays([returns.index.year,returns.index.month])
        grid_idx = pd.MultiIndex.from_product([returns.index.year.unique(),range(1,13)])
        grid = grid.reindex(grid_idx, fill_value=0)
        grid = (grid.pct_change().unstack(level=1)*100).fillna(0).round(1)

        years = (returns[returns.index.month==12].pct_change()*100).round(1)
        years.index = years.index.year
        
        if len(returns.index.year.unique()) > 1:
            years.iloc[0] = ((returns[returns.index.month==12].iloc[0]/self.initial_balance-1)*100).round(1)
        else:
            years.loc[returns.index.year.unique()[0]] = self.get_net_profit(returns.iloc[0],returns.iloc[-1])

        grid['Tot'] = years
        grid.iloc[0,0] = ((returns.iloc[0]/eq.iloc[0]-1)*100).round(1)

        grid.drop(index=grid.index.tolist()[0], inplace=True)
        grid.index.rename('years', inplace=True)
        def ddfunc(val):
            return ((val/val.cummax()-1)*100).min().round(1)
        
        grid['dd'] = returns.groupby(by=returns.index.year).apply(ddfunc)

        dd_eq_money = returns-returns.cummax()
        dd_eq = ((returns/returns.cummax()-1)*100).round(2)
        pf=pf.round(2)        

        self.periods = grid
        self.eq=eq
        self.cash=cash
        self.pf=pf
        self.dd=dd_eq
        self.dd_money=dd_eq_money
        self.div=div




