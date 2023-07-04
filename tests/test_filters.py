import pandas as pd
import os
import unittest
from investlib.filters import PctChange, SharpRatio, BaseFilter


class BaseFilterTest(unittest.TestCase):

    def test_month_or_day_mandatory(self):
        self.assertRaises(Exception, BaseFilter, **dict(gt=0))


class PctChangeTest(unittest.TestCase):
    
    def test_init_no_parameters(self):
        self.assertRaises(Exception, PctChange)
        self.assertRaises(Exception, PctChange, **dict(gt=0))

    def test_init_gt(self):
        f = PctChange(days=30, gt=0)
        self.assertEqual(f.days, 30)
        self.assertEqual(f.gt, 0)
        self.assertEqual(f.gte, None)
        self.assertEqual(f.lt, None)
        self.assertEqual(f.lte, None)

    def test_filtered_one(self):
        datadf = pd.DataFrame(columns=['tk1','tk2'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        datadf['tk1'] = [12,11,12,13,16]
        datadf['tk2'] = [12,11,13,13,16]
        
        f = PctChange(days=2, gt=0)
        assets = f.get_filtered(datadf, date='2023-01-06')
        self.assertEqual(assets, ['tk2'])

    def test_filtered_two(self):
        datadf = pd.DataFrame(columns=['tk1','tk2'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        datadf['tk1'] = [11,12,12,13,16]
        datadf['tk2'] = [11,12,15,13,16]
        
        f = PctChange(days=2, gt=0)
        assets = f.get_filtered(datadf, date='2023-01-06')
        self.assertEqual(assets, ['tk1', 'tk2'])
    
    def test_filtered_gt_02(self):
        datadf = pd.DataFrame(columns=['tk1','tk2'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        datadf['tk1'] = [9,12,11,13,16]
        datadf['tk2'] = [12,11,11,13,16]
        
        f = PctChange(days=2, gt=0.2)
        assets = f.get_filtered(datadf, date='2023-01-06')
        self.assertEqual(assets, ['tk1'])

        f = PctChange(days=2, lt=0.2)
        assets = f.get_filtered(datadf, date='2023-01-06')
        self.assertEqual(assets, ['tk2'])

    def test_filtered_best(self):
        datadf = pd.DataFrame(columns=['tk1','tk2', 'tk3'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        datadf['tk1'] = [12,11,12,13,16]
        datadf['tk2'] = [12,11,15,13,16]
        datadf['tk3'] = [12,11,18,13,16]
        
        f = PctChange(days=2, best=1)
        assets = f.get_filtered(datadf, date='2023-01-06')
        self.assertEqual(assets, ['tk3'])

        f = PctChange(days=2, best=2)
        assets = f.get_filtered(datadf, date='2023-01-06')
        self.assertEqual(assets, ['tk3','tk2'])


class SharpRatioTest(unittest.TestCase):
    
    def test_init_no_parameters(self):
        self.assertRaises(Exception, SharpRatio)
        self.assertRaises(Exception, SharpRatio, **dict(gt=0))

    def test_init_gt(self):
        f = SharpRatio(days=30, gt=0)
        self.assertEqual(f.days, 30)
        self.assertEqual(f.gt, 0)
        self.assertEqual(f.gte, None)
        self.assertEqual(f.lt, None)
        self.assertEqual(f.lte, None)

    def test_filtered_one(self):
        datadf = pd.DataFrame(columns=['tk1','tk2'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        datadf['tk1'] = [12,11,12,9,9]
        datadf['tk2'] = [12,11,13,13,16]
        
        f = SharpRatio(days=2, gt=0)
        assets = f.get_filtered(datadf, date='2023-01-10')
        self.assertEqual(assets, ['tk2'])