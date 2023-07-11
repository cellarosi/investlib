import calendar
import pandas as pd
from investlib.utils import get_interval_by_month

class FirstFriday:
    def is_valid(self, date):
        return date.day_of_week == 4 and date.day <= 7

class FirstMonday:
    def is_valid(self, date):
        return date.day_of_week == 0 and date.day <= 7

class EveryDay:
    def is_valid(self, date):
        return True

class FirstDay:
    def is_valid(self, date):
        return date.day==1

class FridayTimer:
    def is_rebalance_day(self, date):
        return date.weekday() == 4     

class MonthlyTimer:

    def __init__(self, months, day=None):
        self.months = months
        self.day_obj = day
   
    def is_rebalance_day(self, date):
        return self.day_obj.is_valid(date)
            

class FixedAllocation:
    """
        Define the allocation statically using a dictionary that must correspond to the tickers passed to the Strategy class.
        If you don't specify the allocation, it will be equally distributed based on the number of tickers.
        If you exclude certain tickers with filters, it will match the previous allocation if provided; 
        otherwise, it will distribute all capital equally.
    """
    def __init__(self, allocation=None):

        if allocation and sum(allocation.values())>1:
            raise Exception('Total allocation can\'t exceede 100%')

        allocation_dict = allocation or {}
        self.allocation = pd.Series(allocation_dict.values(), index=allocation_dict.keys())

    def rebalance(self, equities, assets=None, *args, **kwargs): 
        cols = assets if assets != None else list(equities.columns) 

        if not self.allocation.empty:
            exclude_cols = list(set(self.allocation.index) - set(cols))
            filter_allocation = self.allocation
            if exclude_cols:
                filter_allocation[exclude_cols] = 0
            return filter_allocation

        perc = round(1/len(cols), 3) if len(cols)>0 else 0
        equal_allocation = pd.Series(index=equities.columns.tolist()).fillna(0)
        equal_allocation[cols] = perc
        return equal_allocation

class BaseRankingAllocation:
    """
        Sort assets based on a condition and adjust them to deciles. 
        After that you can select percentage of allocation for every decile or equally distribution
    """

    def __init__(self, allocation, days=None, months=None, decile=False):
        if len(allocation) > 10:
            raise Exception('BaseRankingAllocation needs to be allocated into deciles. Therefore, the allocation parameters must have a max length of 10')
        if sum(allocation) > 1 or sum(allocation) <= 0:
            raise Exception('The sum of allocation parameter must be between 0 and 1')

        if days==None and months==None:
            raise Exception('Choose one and only one period: days, months') 

        self.allocation = allocation + [0] * (10 - len(allocation)) if decile else allocation
        self.decile = decile
        self.days=days
        self.months=months

class PctChangeRank(BaseRankingAllocation):
    """
        Sort assets based on a percentage variance
    """
    def rebalance(self, equities, date, assets=None, *args, **kwargs): 
        cols = assets if assets != None else list(equities.columns) 
        if self.months != None:
            first_day, last_day = get_interval_by_month(date, self.months)
            eq_cond = (equities.loc[last_day]/equities.loc[first_day]-1).dropna()
        else:
            eq_cond = equities.pct_change(periods=self.days).loc[date].dropna()
        
        if eq_cond.shape[0]<len(cols):
            cols = eq_cond.index.tolist()
        data = self.allocation+[0]*(len(cols)-len(self.allocation))
        allocation = pd.Series(index=eq_cond[cols].sort_values(ascending=False).index, data=data)
        return allocation.reindex(list(equities.columns) ).fillna(0)

