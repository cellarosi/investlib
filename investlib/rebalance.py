import calendar
import pandas as pd

class FirstFriday:
    def is_valid(self, date):
        return date.day_of_week == 4 and date.day <= 7

class EveryDay:
    def is_valid(self, date):
        return True

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

