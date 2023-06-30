import calendar
import pandas as pd

class BaseFilter:
    def __init__(self, days=None, months=None, gt=None, gte=None, lt=None, lte=None, best=None):
        params = [gt, gte, lt, lte, best]
        check = sum(param != None for param in params)
        if check != 1:
            raise Exception('Choose one and only one conditions: gt,gte,lt,lte')
        
        if days==None and month==None:
            raise Exception('Choose one and only one period: days, months') 
    
        self.days=days
        self.months=months
        self.gt=gt
        self.gte=gte
        self.lt=lt
        self.lte=lte
        self.best=best

    def get_interval(self, date):
        start_month = date - pd.DateOffset(months=self.months)
        first_day = start_month
        if not first_day.is_month_start:
            first_day = start_month - pd.offsets.MonthBegin()
        
        last_day = date - pd.DateOffset(months=1)
        if not last_day.is_month_end:
            last_day += pd.offsets.MonthEnd(0)
        
        return (first_day, last_day)

class PctChange(BaseFilter):
    
    def get_filtered(self, equities, date):
        if self.months != None:
            first_day, last_day = self.get_interval(date)
            filtered = (equities.loc[last_day]/equities.loc[first_day]-1).dropna()
        else:
            filtered = equities.pct_change(periods=self.days).loc[date].dropna()

        if self.gt is not None:
            filtered = filtered[filtered>self.gt]
        if self.gte is not None:
            filtered = filtered[filtered>=self.gte]
        if self.lt is not None:
            filtered = filtered[filtered<self.lt]
        if self.lte is not None:
            filtered = filtered[filtered<=self.lte]
        if self.best is not None:
            filtered = filtered.sort_values(ascending=False).iloc[:self.best]
        return filtered.index.tolist()

class SharpRatio(BaseFilter):
    
    def get_filtered(self, equities, date):
        from_date = pd.to_datetime(date) - pd.tseries.offsets.DateOffset(days=self.days)
        from_date = from_date.date().__str__()
        returns = equities.pct_change(periods=self.days).loc[from_date:date]
        filtered = returns.mean()/returns.std()
        filtered = filtered.dropna()

        if self.gt is not None:
            filtered = filtered[filtered>self.gt]
        if self.gte is not None:
            filtered = filtered[filtered>=self.gte]
        if self.lt is not None:
            filtered = filtered[filtered<self.lt]
        if self.lte is not None:
            filtered = filtered[filtered<=self.lte]
        if self.best is not None:
            filtered = filtered.sort_values(ascending=False).iloc[:self.best]

        return filtered.index.tolist()