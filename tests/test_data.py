import os
import shutil
import json
import requests
import unittest
import tempfile
import pandas as pd
from datetime import datetime
from investlib.data import Tiingo
from unittest.mock import MagicMock



class TiingoTest(unittest.TestCase):

    def setUp(self):
        self.tiingo = Tiingo(api_key='token_test', backup_path='/tmp/testTiingo')
        os.mkdir('/tmp/testTiingo')
    def tearDown(self):
        shutil.rmtree('/tmp/testTiingo')

    def test_fix_end_date_past(self):
        self.assertEqual(self.tiingo.fix_end('2003-01-01'), '2003-01-01')

    def test_fix_end_date_future(self):
        # Today
        end_date = pd.to_datetime(datetime.now())
        end_date = end_date.strftime("%Y-%m-%d")
        return_end_date = (pd.to_datetime(datetime.now()) - pd.DateOffset(days=5))
        return_end_date= return_end_date.strftime("%Y-%m-%d")
        self.assertEqual(self.tiingo.fix_end(end_date), return_end_date)

        # Tomorrow
        end_date = pd.to_datetime(datetime.now()) + pd.DateOffset(days=1)
        end_date = end_date.strftime("%Y-%m-%d")
        return_end_date = (pd.to_datetime(datetime.now()) - pd.DateOffset(days=5))
        return_end_date= return_end_date.strftime("%Y-%m-%d")
        self.assertEqual(self.tiingo.fix_end(end_date), return_end_date)

    def test_get_url_default(self):
        tiingo = Tiingo(api_key='token_test')
        self.assertEqual(tiingo.get_url('AAPL'), '/tmp/Tiingo/AAPL')
        
    def test_get_url_backup_path(self):
        self.assertEqual(self.tiingo.get_url('AAPL'), '/tmp/testTiingo/AAPL')

    def test_check_download_needed_no_file(self):
        self.assertTrue(self.tiingo.download_needed('AAPL', '2023-01-01'))

    def test_check_download_needed(self):
        data = {
            'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
            'open': [150.50, 152.30, 153.40, 155.10, 154.90],
            'close': [149.50, 151.70, 152.80, 153.90, 155.50],
            'divCash': [0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1],
            'adjClose': [1, 1, 1, 1, 1],
        }
        aapl = pd.DataFrame(data).set_index('date')
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        aapl.to_csv(temp_file)
        temp_file.seek(0)
        self.assertTrue(self.tiingo.download_needed(temp_file, '2023-01-06'))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        self.assertFalse(self.tiingo.download_needed(temp_file, '2023-01-05'))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        self.assertFalse(self.tiingo.download_needed(temp_file, '2023-01-04'))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        self.assertFalse(self.tiingo.download_needed(temp_file, '2023-01-01'))

        temp_file.close()

    def test_read_date_ok(self):
        data = {
            'date': ['2023-01-01T00:00:00.000Z', '2023-01-02T00:00:00.000Z', '2023-01-03T00:00:00.000Z', '2023-01-04T00:00:00.000Z', '2023-01-05T00:00:00.000Z'],
            'open': [150.50, 152.30, 153.40, 155.10, 154.90],
            'close': [149.50, 151.70, 152.80, 153.90, 155.50],
            'divCash': [0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1],
            'adjClose': [1, 1, 1, 1, 1],
        }
        aapl = pd.DataFrame(data).set_index('date')
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        aapl.to_csv(temp_file)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, '2023-01-02','2023-01-05')
        self.assertEqual(data.shape,(4,5))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, '2022-01-02','2023-01-05')
        self.assertEqual(data.shape,(5,5))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, '2022-01-02','2024-01-05')
        self.assertEqual(data.shape,(5,5))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, '2023-01-05','2024-01-05')
        self.assertEqual(data.shape,(1,5))
        temp_file.close()
        os.remove(temp_file.name)

    def test_read_check_date_format(self):
        data = {
            'date': ['2023-01-01T00:00:00.000Z', '2023-01-02T00:00:00.000Z', '2023-01-03T00:00:00.000Z', '2023-01-04T00:00:00.000Z', '2023-01-05T00:00:00.000Z'],
            'open': [150.50, 152.30, 153.40, 155.10, 154.90],
            'close': [149.50, 151.70, 152.80, 153.90, 155.50],
            'divCash': [0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1],
            'adjClose': [1, 1, 1, 1, 1],
        }
        aapl = pd.DataFrame(data).set_index('date')
        temp_file = tempfile.TemporaryFile()
        aapl.to_csv(temp_file)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, '2023-01-02','2023-01-05')
        self.assertEqual(data.index[0].date(), pd.to_datetime('2023-01-02').date())
        temp_file.close()
        

    def test_read_date_empty(self):
        data = {
            'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
            'open': [150.50, 152.30, 153.40, 155.10, 154.90],
            'close': [149.50, 151.70, 152.80, 153.90, 155.50],
            'divCash': [0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1],
            'adjClose': [1, 1, 1, 1, 1],
        }
        aapl = pd.DataFrame(data).set_index('date')
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        
        aapl.to_csv(temp_file)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file)
        self.assertEqual(data.shape,(5,5))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, None,'2023-01-10')
        self.assertEqual(data.shape,(5,5))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, '2023-01-01',None)
        self.assertEqual(data.shape,(5,5))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, '2022-01-01',None)
        self.assertEqual(data.shape,(5,5))

        temp_file = open(temp_file.name)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, '2022-01-01','2022-02-01')
        self.assertEqual(data.shape,(0,5))
        temp_file = open(temp_file.name)
        temp_file.seek(0)
        data = self.tiingo.read(temp_file, '2023-12-01','2023-12-12')
        self.assertEqual(data.shape,(0,5))
    
        temp_file.close()
        os.remove(temp_file.name)
  
    def test_download(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.tiingo.backup_path  = temp_dir.name

        json_data = '[{"date":"1997-01-07T00:00:00.000Z","close":75.343697,"high":75.468697,"low":74.125,"open":74.4375,"volume":939000,"adjClose":47.2742585611,"adjHigh":47.352689572,"adjLow":46.5095894596,"adjOpen":46.7056669869,"adjVolume":939000,"divCash":0.0,"splitFactor":1.0},{"date":"1997-01-08T00:00:00.000Z","close":74.6875,"high":75.781197,"low":74.6875,"open":75.75,"volume":1802200,"adjClose":46.8625290087,"adjHigh":47.5487670992,"adjLow":46.8625290087,"adjOpen":47.5291926013,"adjVolume":1802200,"divCash":0.0,"splitFactor":1.0},{"date":"1997-01-09T00:00:00.000Z","close":75.3125,"high":75.875,"low":74.9375,"open":75.0625,"volume":1415700,"adjClose":47.2546840631,"adjHigh":47.6076236121,"adjLow":47.0193910304,"adjOpen":47.0978220413,"adjVolume":1415700,"divCash":0.0,"splitFactor":1.0},{"date":"1997-01-10T00:00:00.000Z","close":76.125,"high":76.25,"low":74.25,"open":74.25,"volume":2369500,"adjClose":47.7644856339,"adjHigh":47.8429166448,"adjLow":46.5880204705,"adjOpen":46.5880204705,"adjVolume":2369500,"divCash":0.0,"splitFactor":1.0},{"date":"1997-01-13T00:00:00.000Z","close":76.015602,"high":76.5,"low":75.640602,"open":76.5,"volume":1364600,"adjClose":47.6958440681,"adjHigh":47.9997786666,"adjLow":47.4605510354,"adjOpen":47.9997786666,"adjVolume":1364600,"divCash":0.0,"splitFactor":1.0}]'
        
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = json.loads(json_data)

        # Simula la chiamata alla richiesta HTTP
        requests.get = MagicMock(return_value=response_mock)

        self.tiingo.download('AAPL')
        df  = pd.read_csv('{}/{}'.format(temp_dir.name, 'AAPL'))
        self.assertEqual(df.shape, (5,13))
        temp_dir.cleanup()

    def test_load(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.tiingo.backup_path  = temp_dir.name

        json_data = '[{"date":"1997-01-07T00:00:00.000Z","close":75.343697,"high":75.468697,"low":74.125,"open":74.4375,"volume":939000,"adjClose":47.2742585611,"adjHigh":47.352689572,"adjLow":46.5095894596,"adjOpen":46.7056669869,"adjVolume":939000,"divCash":0.0,"splitFactor":1.0},{"date":"1997-01-08T00:00:00.000Z","close":74.6875,"high":75.781197,"low":74.6875,"open":75.75,"volume":1802200,"adjClose":46.8625290087,"adjHigh":47.5487670992,"adjLow":46.8625290087,"adjOpen":47.5291926013,"adjVolume":1802200,"divCash":0.0,"splitFactor":1.0},{"date":"1997-01-09T00:00:00.000Z","close":75.3125,"high":75.875,"low":74.9375,"open":75.0625,"volume":1415700,"adjClose":47.2546840631,"adjHigh":47.6076236121,"adjLow":47.0193910304,"adjOpen":47.0978220413,"adjVolume":1415700,"divCash":0.0,"splitFactor":1.0},{"date":"1997-01-10T00:00:00.000Z","close":76.125,"high":76.25,"low":74.25,"open":74.25,"volume":2369500,"adjClose":47.7644856339,"adjHigh":47.8429166448,"adjLow":46.5880204705,"adjOpen":46.5880204705,"adjVolume":2369500,"divCash":0.0,"splitFactor":1.0},{"date":"1997-01-13T00:00:00.000Z","close":76.015602,"high":76.5,"low":75.640602,"open":76.5,"volume":1364600,"adjClose":47.6958440681,"adjHigh":47.9997786666,"adjLow":47.4605510354,"adjOpen":47.9997786666,"adjVolume":1364600,"divCash":0.0,"splitFactor":1.0}]'
        
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = json.loads(json_data)

        # Simula la chiamata alla richiesta HTTP
        requests.get = MagicMock(return_value=response_mock)

        aapl = self.tiingo.load(['AAPL1', 'AAPL2'])
        cols = aapl.columns.tolist()

        self.assertTrue(('AAPL1','open') in cols)
        self.assertTrue(('AAPL2','open') in cols)
        self.assertTrue(('AAPL1','close') in cols)
        self.assertTrue(('AAPL2','close') in cols)
        self.assertTrue(('AAPL1','divCash') in cols)
        self.assertTrue(('AAPL2','divCash') in cols)
        self.assertTrue(('AAPL1','splitFactor') in cols)
        self.assertTrue(('AAPL2','splitFactor') in cols)
        self.assertEqual(aapl.shape, (5,10))
        temp_dir.cleanup()


    def test_load_diff_periods(self):

        data1 = {
            'date': ['2023-01-10','2023-01-11', '2023-01-12', '2023-01-13', '2023-01-16', '2023-01-17'],
            'open': [10,11,12,13,16,17],
            'close': [10,11,12,13,16,17],
            'divCash': [0, 0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1, 1],
            'adjClose': [1, 1, 1, 1, 1, 1],
        }
        data2 = {
            'date': ['2023-01-11', '2023-01-12', '2023-01-13', '2023-01-16', '2023-01-17'],
            'open': [11,12,13,16,17],
            'close': [11,12,13,16,17],
            'divCash': [0, 0, 0, 0, 0],
            'splitFactor': [1, 1, 1, 1, 1],
            'adjClose': [1, 1, 1, 1, 1],
        }
        data1df = pd.DataFrame(data1).set_index('date')
        data2df = pd.DataFrame(data2).set_index('date')
        filedata1 = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo',delete=False)
        filedata2 = tempfile.NamedTemporaryFile(dir='/tmp/testTiingo', delete=False)
        data1df.to_csv(filedata1)
        data2df.to_csv(filedata2)
        filedata1.seek(0)
        filedata2.seek(0)

        tk1=os.path.basename(filedata1.name)
        tk2=os.path.basename(filedata2.name)
        tickers = [tk1,tk2]
        data = self.tiingo.load(tickers, end='2023-01-17')
        self.assertTrue(data.loc['2023-01-10',(tk1,'close')]>0)
        self.assertFalse(data.loc['2023-01-10',(tk2,'close')]>0)
        self.assertTrue(pd.isna(data.loc['2023-01-10',(tk2,'close')]))
        filedata1.close()
        filedata2.close()
        os.remove(filedata1.name)
        os.remove(filedata2.name)

    def test_resample_read_no_div_and_split(self):
        data = {
            'date': ['2023-05-05T00:00:00.000Z', '2023-05-08T00:00:00.000Z'],
            'open': [150.50, 152.30],
            'close': [149.50, 151.70],
            'divCash': [1, 1],
            'splitFactor': [1, 1],
            'adjClose': [1, 1]
        }
        aapl = pd.DataFrame(data).set_index('date')
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        aapl.to_csv(temp_file)
        temp_file.seek(0)
        tk = os.path.basename(temp_file.name)
        data = self.tiingo.read(temp_file)
        self.assertEqual(data.shape,(2,5))
      
        self.assertEqual(data.loc['2023-05-05', 'divCash'],1)
        self.assertEqual(data.loc['2023-05-05', 'splitFactor'],1)
        self.assertEqual(data.loc['2023-05-08', 'divCash'],1)
        self.assertEqual(data.loc['2023-05-08', 'splitFactor'],1)
        
