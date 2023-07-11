import pandas as pd
import unittest
from investlib.utils import get_interval_by_month



class IntervalTest(unittest.TestCase):
    def test_get_interval_middle_month_day(self):
        first, last = get_interval_by_month(pd.to_datetime('2022-05-03'),3)
        self.assertEqual(first.date().__str__(), '2022-02-01')
        self.assertEqual(last.date().__str__(), '2022-04-30')

    def test_get_interval_last_month_day(self):
        first, last = get_interval_by_month(pd.to_datetime('2022-05-31'),3)
        self.assertEqual(first.date().__str__(), '2022-02-01')
        self.assertEqual(last.date().__str__(), '2022-04-30')

    def test_get_interval_first_month_day(self):
        first, last = get_interval_by_month(pd.to_datetime('2022-05-01'),3)
        self.assertEqual(first.date().__str__(), '2022-02-01')
        self.assertEqual(last.date().__str__(), '2022-04-30')
