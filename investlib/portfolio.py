import pandas as pd 
import numpy as np
from investlib.rebalance import FixedAllocation
from investlib.data import Tiingo






class Portfolio:

    strategies = [Strategy(['SPY'])]
    #assets = ['IVV','IWR','IWM'] # Large Mid e Small cap
    # Seleziona gli asset con rendimento >0 nell'ultimo anno e ordinali per sharp crescente
    #selectors = [Rend(period=250, gt=0), Ranking(period=30, criteria='sharp', weight=[1])]  
    #allocation_class = FixedAllocation

    start = '2005-01-01'
    end = '2021-12-31'

    
    def __init__(self, strategies, start=None, end=None, initial_deposit=100000):
        pass
