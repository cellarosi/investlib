import pandas as pd
import os
import unittest
from investlib.rebalance import MonthlyTimer, FirstFriday, FixedAllocation

class MonthlyTimerTest(unittest.TestCase):
    
    def test_single_day(self):
        timer = MonthlyTimer(months=2, day=FirstFriday())

        self.assertTrue(timer.is_rebalance_day(pd.Timestamp('2022-01-07')))
        self.assertFalse(timer.is_rebalance_day(pd.Timestamp('2022-01-08')))

        self.assertTrue(timer.is_rebalance_day(pd.Timestamp('2022-01-07')))
        self.assertFalse(timer.is_rebalance_day(pd.Timestamp('2022-01-08')))

    def test_first_day_last_friday(self):
        timer = MonthlyTimer(months=1, day=FirstFriday())

        self.assertTrue(timer.is_rebalance_day(pd.Timestamp('1993-02-05')))
        
    

class FixedAllocationTest(unittest.TestCase):

    def test_default(self):
        equities = pd.DataFrame(columns=['st1','st2'])
        fixed = FixedAllocation()
        allocation = fixed.rebalance(equities) 
        ret_alloc = pd.Series(index=['st1','st2'], data=[0.5,0.5])
        self.assertEqual(allocation.tolist(), ret_alloc.tolist())  

    def test_with_params(self):
        equities = pd.DataFrame(columns=['st1','st2'])
        fixed = FixedAllocation(allocation={'st1': 0.7,'st2': 0.3})
        allocation = fixed.rebalance(equities) 
        ret_alloc = pd.Series(index=['st1','st2'], data=[0.7,0.3])
        self.assertEqual(allocation.tolist(), ret_alloc.tolist())   
    
    def test_empty_assets(self):
        equities = pd.DataFrame(columns=['st1','st2'])
        fixed = FixedAllocation()
        allocation = fixed.rebalance(equities, assets=[]) 
        ret_alloc = pd.Series(index=['st1','st2'], data=[0,0])
        self.assertEqual(allocation.tolist(), ret_alloc.tolist())

    def test_total_error(self):        
        self.assertRaises(Exception, FixedAllocation, [0.8, 0.3])

    def test_count_error_miss_params_equities(self):    
        fixed = FixedAllocation(allocation={'st1': 0.3,'st2': 0.3,'st3': 0.4})
        self.assertRaises(Exception, fixed.rebalance)
