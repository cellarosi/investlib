import pandas as pd

def get_interval_by_month(date, months):
    start_month = date - pd.DateOffset(months=months)
    first_day = start_month
    if not first_day.is_month_start:
        first_day = start_month - pd.offsets.MonthBegin()
    
    last_day = date - pd.DateOffset(months=1)
    if not last_day.is_month_end:
        last_day += pd.offsets.MonthEnd(0)
    
    return (first_day, last_day)