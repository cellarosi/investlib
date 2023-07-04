import pandas as pd
import numpy as np
import os
import unittest
from investlib.rebalance import MonthlyTimer, FirstFriday
from investlib.rebalance import FixedAllocation, BaseRankingAllocation, PctChangeRank

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


class BaseRankingAllocationTest(unittest.TestCase):

    def test_no_allocation_error(self):
        self.assertRaises(Exception, BaseRankingAllocation)

    def test_sum_error(self):
        self.assertRaises(Exception, BaseRankingAllocation, **dict(allocation=[1,0.1]))
        self.assertRaises(Exception, BaseRankingAllocation, **dict(allocation=[-1,0.1]))

        with self.assertRaises(Exception) as cm:
            BaseRankingAllocation(allocation=[0])

        self.assertEqual(str(cm.exception), 'The sum of allocation parameter must be between 0 and 1')
    
    def test_len_error(self):
        with self.assertRaises(Exception) as cm:
            BaseRankingAllocation(allocation=[0,0,0,0,0,0,0,0,0,0,1])

        self.assertEqual(str(cm.exception), 'BaseRankingAllocation needs to be allocated into deciles. Therefore, the allocation parameters must have a max length of 10')

    def test_fill_missed_allocation(self):
        ranking = BaseRankingAllocation(allocation=[0.6,0.4], months=3, decile=True)
        self.assertEqual(ranking.allocation, [0.6,0.4,0,0,0,0,0,0,0,0])

        ranking = BaseRankingAllocation(allocation=[0.6,0.4], months=3, decile=False)
        self.assertEqual(ranking.allocation, [0.6,0.4])


class PctChangeRankTest(unittest.TestCase):

    def test_no_assets(self):
        datadf = pd.DataFrame(columns=['tk1','tk2','tk3'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        datadf['tk1'] = [12,11,12,13,16]
        datadf['tk2'] = [12,11,13,13,16]
        datadf['tk3'] = [12,11,15,13,16]
        
        rank = PctChangeRank(allocation=[0.6,0.4], days=2)
        rankdf = rank.rebalance(datadf, date='2023-01-06')
        self.assertEqual(rankdf.values.tolist(), [0.0, 0.4,0.6])
        
        datadf['tk1'] = [12,11,12,13,16]
        datadf['tk2'] = [12,11,10,13,16]
        datadf['tk3'] = [12,11,15,13,16]
        
        rank = PctChangeRank(allocation=[0.6,0.4], days=2)
        rankdf = rank.rebalance(datadf, date='2023-01-06')
        self.assertEqual(rankdf.tolist(), [0.4, 0,0.6])

    def test_assets_notequal_cols(self):
        datadf = pd.DataFrame(columns=['tk1','tk2','tk3','tk4'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        datadf['tk1'] = [12,11,12,13,16]
        datadf['tk2'] = [12,11,13,13,16]
        datadf['tk3'] = [12,11,15,13,16]
        datadf['tk4'] = [12,11,9,13,16]
    
        rank = PctChangeRank(allocation=[0.6,0.4], days=2)
        rankdf = rank.rebalance(datadf, date='2023-01-06', assets=['tk1','tk2','tk4'])
        self.assertEqual(rankdf.values.tolist(), [0.4, 0.6,0.0,0.0])

    def test_nan_values(self):
        datadf = pd.DataFrame(columns=['tk1','tk2','tk3','tk4'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        datadf['tk1'] = [12,11,12,14,16]
        datadf['tk2'] = [12,11,13,13,16]
        datadf['tk3'] = [np.nan,11,15,13,16]
        datadf['tk4'] = [12,11,9,13,16]
    
        rank = PctChangeRank(allocation=[0.6,0.4], days=2)
        rankdf = rank.rebalance(datadf, date='2023-01-06')
        self.assertEqual(rankdf.values.tolist(), [0.4, 0.6,0.0,0.0])
        rankdf = rank.rebalance(datadf, date='2023-01-10')
        self.assertEqual(rankdf.values.tolist(), [0.4, 0.0,0.0,0.6])
       