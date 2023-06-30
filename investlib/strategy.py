import os, math 
import pandas as pd 
import numpy as np
from investlib.rebalance import FixedAllocation
from investlib.rebalance import MonthlyTimer
from investlib.rebalance import FirstFriday
from investlib.data import Tiingo

class Strategy:

    def __init__(self, assets, start=None, end=None, allocation_class=None, filters=None, timer=None, initial_deposit=100000):
        self.timer = timer or MonthlyTimer(months=1, day=FirstFriday())
        self.allocation_class = allocation_class or FixedAllocation()
        self.initial_deposit = initial_deposit
        self.assets = assets
        self.start = pd.to_datetime(start) if start else None
        self.end = pd.to_datetime(end) if end else None
        self.filters = filters or []
    
    def load_data(self):
        tiingo = Tiingo(api_key=os.environ.get("tiingo_api_key"), backup_path=os.environ.get("tiingo_backup_path"))
        return tiingo.load(self.assets)
    
    def init_run(self, history):
        if self.start:
            self.start = max(history.index[0],self.start)
        else:
            self.start = history.index[0]
        
        if self.end:
            self.end = min(history.index[-1],self.end)
        else:
            self.end = history.index[-1]

        
        invest_range = history.loc[self.start:self.end].index

        self.cash = pd.DataFrame(index=invest_range, columns=['add', 'pre_close', 'post_close']).fillna(0)
        self.quantity = pd.DataFrame(index=invest_range, columns=self.assets).fillna(0)
        self.dividends = pd.DataFrame(index=invest_range, columns=self.assets).fillna(0)
        self.allocation = pd.DataFrame(index=invest_range, columns=self.assets).fillna(0)

        cols = pd.MultiIndex.from_product([self.assets, ['current', 'value']])
        self.invested = pd.DataFrame(index=invest_range, columns=cols).fillna(0)
        self.cash.loc[self.start, ['add','pre_close','post_close']] = self.initial_deposit
    
    def get_assets_to_allocate(self, equities, date):
        assets = equities.columns.tolist() 
        for f in self.filters:
            assets = f.get_filtered(equities[assets], date)
        return assets

    def run(self):
        history = self.load_data()
        self.init_run(history)
        timer = MonthlyTimer(months=1, day=FirstFriday())
        #timer.set_rebalancing_days(pd.to_datetime(self.start), pd.to_datetime(self.end))
        invest_range = history.copy()
        invest_range = invest_range.loc[self.start:self.end]
        self.history=history
        for i, date in invest_range.iterrows():
            self.quantity.loc[i,:] = self.quantity.shift(1).fillna(0).loc[i,:]*history.loc[i].xs('splitFactor',  level=1)
            # CASO DI NON RIBILANCIAMENTO
            # Copio tutte le righe aggiornando solo il valore investito, la equity ed eventuali dividendi che vanno in cash
            # Calculate final invesment returns for every asset at the end of current date <i>
            self.invested.loc[i, (slice(None), 'current')] = 0
            self.invested.loc[i, (slice(None), 'value')] = self.quantity.loc[i, :].mul(history.loc[i].xs('close',  level=1)).tolist()
            

            # get dividends
            self.dividends.loc[i,:] = self.quantity.loc[i,:].mul(history.loc[i].xs('divCash',  level=1))
            # Add dividend to cash and update total cash
            self.cash.loc[i, 'add'] += self.dividends.loc[i,:].sum()
           
            # TODO: SERVE???
            if i>self.start:
                self.cash.loc[i, 'pre_close'] = self.cash.shift(1).loc[i,'post_close']+self.cash.loc[i,'add']
                self.allocation.loc[i] = self.allocation.shift(1).loc[i]

            if self.timer.is_rebalance_day(pd.to_datetime(i)) or i == self.start:
                
                equities = history.loc[:, (slice(None), 'close')].droplevel(1, axis=1)
                assets = self.get_assets_to_allocate(equities,i)
                self.allocation.loc[i] = self.allocation_class.rebalance(history.loc[:, (slice(None), 'close')].droplevel(1, axis=1), date=i, assets=assets)
                total_capital = self.invested.loc[i, (slice(None), 'value')].sum() + self.cash.loc[i, 'pre_close']
                capital_used = self.invested.loc[i, (slice(None), 'value')].droplevel(level=1)
                capital_to_use = (total_capital*self.allocation.loc[i]-capital_used)


                # In case we neet to remove money from asset, we round up to modify weight under the required percentage
                # Otherwise, if we need to buy, we have to use rund under to buy che max intege quantity
                #neg_asset = capital_to_use[capital_to_use<0].index
                #pos_asset = capital_to_use[capital_to_use>=0].index
                current_close = history.loc[i].xs('close',  level=1)
                quantity = (capital_to_use/current_close).fillna(0).round(2).apply(math.floor)
                self.quantity.loc[i, :] += quantity
                #self.quantity.loc[i, pos_asset] += (capital_to_use/current_close).apply(math.floor)
                self.invested.loc[i, (slice(None), 'current')] = history.loc[i].xs('close',  level=1).mul(quantity).tolist()
                self.invested.loc[i, (slice(None), 'value')] = self.quantity.loc[i,:].mul(history.loc[i].xs('close',  level=1)).tolist()

            self.cash.loc[i, 'post_close'] = self.cash.loc[i, 'pre_close']-self.invested.loc[i, (slice(None), 'current')].sum()
