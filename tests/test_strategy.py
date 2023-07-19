import os
import shutil
import unittest
from unittest import mock
import tempfile
from freezegun import freeze_time
import pandas as pd
from investlib.strategy import Strategy
from investlib.rebalance import FixedAllocation
from investlib.rebalance import FridayTimer
from investlib.filters import PctChange, SharpRatio


class StrategyFiltersTest(unittest.TestCase):
    
    
    def test_get_assets_to_allocate_multi_filter(self):
        data_df = pd.DataFrame(columns=['tk1','tk2','tk3'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        data_df['tk1'] = [11,12,9,13,16]
        data_df['tk2'] = [11,12,16,13,16]
        data_df['tk3'] = [11,12,15,13,16]
        
        s = Strategy(
            assets = ['tk1','tk2','tk3'],
            filters=[PctChange(days=2,gt=0), PctChange(days=1,best=1)]
        )

        assets = s.get_assets_to_allocate(data_df, date='2023-01-06')
        self.assertEqual(assets, ['tk2'])

    def test_get_assets_to_allocate_no_assets(self):
        data_df = pd.DataFrame(columns=['tk1','tk2','tk3'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'])
        data_df['tk1'] = [11,12,9,13,16]
        data_df['tk2'] = [11,12,9,13,16]
        data_df['tk3'] = [11,12,9,13,16]
        
        s = Strategy(
            assets = ['tk1','tk2','tk3'],
            filters=[PctChange(days=2,gt=0)]
        )

        assets = s.get_assets_to_allocate(data_df, date='2023-01-06')
        self.assertEqual(assets, [])

    def test_get_assets_to_allocate_no_assets_mix_filter(self):
        data_df = pd.DataFrame(columns=['tk1','tk2','tk3'], index=['2023-01-04','2023-01-05','2023-01-06', '2023-01-07', '2023-01-08'])
        data_df['tk1'] = [11,12,9,9,9]
        data_df['tk2'] = [11,12,9,9,9]
        data_df['tk3'] = [11,12,9,9,9]
        
        s = Strategy(
            assets = ['tk1','tk2','tk3'],
            filters=[PctChange(days=2,gt=0), SharpRatio(days=2,gt=0)]
        )

        assets = s.get_assets_to_allocate(data_df, date='2023-01-06')
        self.assertEqual(assets, [])
        assets = s.get_assets_to_allocate(data_df, date='2023-01-07')
        self.assertEqual(assets, [])
        assets = s.get_assets_to_allocate(data_df, date='2023-01-08')
        self.assertEqual(assets, [])

   


class StrategyTest(unittest.TestCase):
    def setUp(self):
        os.mkdir('/tmp/testTiingo')
    def tearDown(self):
        shutil.rmtree('/tmp/testTiingo')
    
    def test_init(self):
        tickers = ['SPY']
        
        s = Strategy(
            assets = tickers
        )

        self.assertEqual(s.assets, tickers)
        self.assertEqual(s.start, None)
        self.assertEqual(s.end, None)
        self.assertEqual(s.filters, [])
        self.assertEqual(s.initial_deposit, 100000)
        self.assertEqual(s.allocation_class.__class__.__name__, 'FixedAllocation')

    @mock.patch.dict(os.environ, {"tiingo_backup_path": "/tmp/testTiingo"})
    @freeze_time("2023-01-22")
    def test_load(self):
        data = {
            'date': ['2023-01-10','2023-01-11', '2023-01-12', '2023-01-13', '2023-01-16', '2023-01-17'],
            'open': [10,11,12,13,16,17],
            'close': [10,11,12,13,16,17],
            'divCash': [0, 0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk=os.path.basename(filedata.name)
        
        tickers = [tk]
        s = Strategy(
            assets = tickers
        )
        history = s.load_data()        
        self.assertEqual(history.shape, (6,5))
        filedata.close()

    
    def test_init_run(self):
        data = {
            'date': ['2023-01-10','2023-01-11', '2023-01-12', '2023-01-13', '2023-01-16', '2023-01-17'],
            'open': [10,11,12,13,16,17],
            'close': [10,11,12,13,16,17],
            'divCash': [0, 0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        datadf=pd.concat([datadf], keys=['SPY'], axis=1, join='outer')
        
        s = Strategy(
            assets = ['SPY']
        )
        s.init_run(datadf)
        self.assertEqual(s.start, '2023-01-10')
        self.assertEqual(s.end, '2023-01-17')

        s.start = '2023-01-11'
        s.end = '2023-01-16'
        s.init_run(datadf)
        self.assertEqual(s.start, '2023-01-11')
        self.assertEqual(s.end, '2023-01-16')


    @mock.patch.dict(os.environ, {"tiingo_backup_path": "/tmp/testTiingo"})
    @freeze_time("2023-01-17")
    def test_init_run_one_ticker_no_date(self):
        data = {
            'date': ['2023-01-05','2023-01-06', '2023-01-09', '2023-01-10', '2023-01-11', '2023-01-12'],
            'open': [10,11,12,13,16,17],
            'close': [10,11,12,13,16,17],
            'divCash': [0, 0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk=os.path.basename(filedata.name)
        
        tickers = [tk]
        s = Strategy(
            assets = tickers
        )
        s.run()        
        filedata.close()

        self.assertEqual(len(s.cash.index), 6)

        s = Strategy(
            assets = tickers,
            start='2023-01-06'
        )
        s.run()   
        self.assertEqual(len(s.cash.index), 5)
        s = Strategy(
            assets = tickers,
            start='2023-01-05',
            end='2023-01-12'
        )
        s.run()   
        self.assertEqual(len(s.cash.index), 6)
        self.assertEqual(s.cash.columns.tolist(), ['add','pre_close','post_close'])
        self.assertEqual(s.quantity.columns.tolist(), [tk])
        self.assertEqual(s.invested.columns.tolist(), [(tk,'current'),(tk,'value'),])
    
    @mock.patch.dict(os.environ, {"tiingo_backup_path": "/tmp/testTiingo"})
    @freeze_time("2023-01-16")
    def test_run_one_ticker_no_date_100(self):
        data = {
            'date': ['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10', '2023-01-11'],
            'open': [12,11,12,13,16,17],
            'close': [12,11,12,13,16,17],
            'divCash': [0, 0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk=os.path.basename(filedata.name)
        filedata.close()
        
        tickers = [tk]
        s = Strategy(
            assets = tickers
        )
        s.run()        

        

        self.assertEqual(s.invested.loc['2023-01-11', (tk,'value')], 141661)
        self.assertEqual(s.cash['post_close'].tolist(), [4, 4,4,4,4,4])

  
    @mock.patch.dict(os.environ, {"tiingo_backup_path": "/tmp/testTiingo"})
    @freeze_time("2023-01-16")
    def test_run_one_ticker_no_date_70(self):
        data = {
            'date': ['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10', '2023-01-11'],
            'open': [12,11,12,13,16,17],
            'close': [12,11,12,13,16,17],
            'divCash': [0, 0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk=os.path.basename(filedata.name)
        filedata.close()
        
        tickers = [tk]
        s = Strategy(
            assets = tickers,
            allocation_class=FixedAllocation(allocation={tk:0.7})
        )
        s.run()        

        

        self.assertEqual(s.invested.loc['2023-01-11', (tk,'value')], 99161)
        self.assertEqual(s.cash['post_close'].tolist(), [30004, 30004,30004,30004,30004,30004])



    @mock.patch.dict(os.environ, {"tiingo_backup_path": "/tmp/testTiingo"})
    @freeze_time("2023-01-16")
    def test_run_one_ticker_date_start_missing(self):
        data = {
            'date': ['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10', '2023-01-11'],
            'open': [12,11,12,13,16,17],
            'close': [12,11,12,13,16,17],
            'divCash': [0, 0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk=os.path.basename(filedata.name)
        filedata.close()
        
        tickers = [tk]
        s = Strategy(
            assets = tickers,
            start='2023-01-03'
        )
        s.run()   

        self.assertEqual(s.invested.loc['2023-01-11', (tk,'value')], 141661)
        self.assertEqual(s.cash['post_close'].tolist(), [4,4,4,4,4,4]) 

    @mock.patch.dict(os.environ, {"tiingo_backup_path": "/tmp/testTiingo"})
    @freeze_time("2023-03-15")
    def test_run_one_ticker_second_rebalance_with_dividends(self):
        data = {
            'date': ['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10', '2023-02-03', '2023-02-10',  '2023-02-11', '2023-03-03', '2023-03-10'],
            'open': [12,11,12,13,16,16,16,16,16,17],
            'close': [12,11,12,13,16,16,16,16,16,17],
            'divCash': [0, 0, 0, 1, 0, 0,1, 0, 0,0],
            'splitFactor': [1, 1, 1, 1, 1, 1, 1, 1, 1,1],
            'adjClose':  [0,0,0,0,0,0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk=os.path.basename(filedata.name)
        filedata.close()
        
        tickers = [tk]
        s = Strategy(
            assets = tickers,
            start='2023-01-03'
        )
        s.run()   
        self.assertEqual(s.dividends.loc['2023-01-09', tk], 8333)
        self.assertEqual(s.quantity.loc['2023-02-03', tk], 8854)
        
        self.assertEqual(s.invested.loc['2023-02-03', (tk,'value')], 141664)
        self.assertEqual(s.cash.loc['2023-02-03', 'post_close'], 1)
       
        self.assertEqual(s.cash.loc['2023-02-10', 'post_close'], 8855)
        self.assertEqual(s.cash.loc['2023-03-03', 'post_close'], 7)
        self.assertEqual(s.quantity.loc['2023-03-03', tk], 9407)
        self.assertEqual(s.invested.loc['2023-03-10', (tk,'value')], 159919)

    @mock.patch.dict(os.environ, {"tiingo_backup_path": "/tmp/testTiingo"})
    @freeze_time("2023-01-15")
    def test_run_tow_ticker_no_rebalance(self):
        data = {
            'date': ['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'],
            'open': [12,11,12,13,16],
            'close': [12,11,12,13,16],
            'divCash': [0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk1=os.path.basename(filedata.name)
        filedata.close()

        data = {
            'date': ['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'],
            'open': [12,11,12,13,16],
            'close': [12,11,12,13,16],
            'divCash': [0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk2=os.path.basename(filedata.name)
        filedata.close()
        
        tickers = [tk1,tk2]
        s = Strategy(
            assets = tickers,
            allocation_class=FixedAllocation({tk1:0.6,tk2:0.4})
        )
        s.run()   
        
        self.assertEqual(s.cash.iloc[0]['post_close'], 4)
        self.assertEqual(s.cash.iloc[-1]['post_close'], 4)
        self.assertEqual(s.quantity.iloc[0].sum(), 8333)
        self.assertEqual(s.quantity.iloc[-1].sum(), 8333)
        self.assertEqual(s.invested.loc['2023-01-10', (tk1,'value')], 80000)
        self.assertEqual(s.invested.loc['2023-01-10', (tk2,'value')], 53328)


    @mock.patch.dict(os.environ, {"tiingo_backup_path": "/tmp/testTiingo"})
    @freeze_time("2023-01-15")
    def test_run_tow_ticker_one_more_rebalance(self):
        data = {
            'date': ['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'],
            'open': [12,11,12,13,16],
            'close': [12,11,12,13,16],
            'divCash': [0, 1, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk1=os.path.basename(filedata.name)
        filedata.close()

        data = {
            'date': ['2023-01-04','2023-01-05','2023-01-06', '2023-01-09', '2023-01-10'],
            'open': [12,11,12,13,16],
            'close': [10,11,12,13,16],
            'divCash': [0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1],
            'adjClose':  [0,0,0,0,0]
        }
       
        datadf = pd.DataFrame(data).set_index('date')
        filedata = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        datadf.to_csv(filedata)
        tk2=os.path.basename(filedata.name)
        filedata.close()
        
        tickers = [tk1,tk2]
        s = Strategy(
            assets = tickers,
            allocation_class=FixedAllocation({tk1:0.5,tk2:0.5})
        )
        s.run()   
        
        self.assertEqual(s.quantity.iloc[0][tk1], 4166)
        self.assertEqual(s.quantity.iloc[0][tk2], 5000)
        self.assertEqual(s.invested.loc['2023-01-04', (tk1,'value')], 49992)
        self.assertEqual(s.invested.loc['2023-01-04', (tk2,'value')], 50000)
        self.assertEqual(s.cash.loc['2023-01-04', 'post_close'], 8)

        self.assertEqual(s.cash.loc['2023-01-05', 'post_close'], 4174)
        self.assertEqual(s.quantity.loc['2023-01-05'][tk1], 4166)
        self.assertEqual(s.quantity.loc['2023-01-05'][tk2], 5000)
        self.assertEqual(s.invested.loc['2023-01-05', (tk1,'value')], 45826)
        self.assertEqual(s.invested.loc['2023-01-05', (tk2,'value')], 55000)

        #total = 49992 + 60000 = 109992 / + 4174 (cash) = 114166/2 = 57083
        self.assertEqual(s.quantity.loc['2023-01-06', tk1], 4756)
        self.assertEqual(s.quantity.loc['2023-01-06', tk2], 4756)
        self.assertEqual(s.cash.loc['2023-01-06', 'post_close'], 22)
        self.assertEqual(s.invested.loc['2023-01-06', (tk1,'value')], 57072)
        self.assertEqual(s.invested.loc['2023-01-06', (tk2,'value')], 57072)
   