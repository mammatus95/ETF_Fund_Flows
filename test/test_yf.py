#!/usr/bin/python3
import unittest
from datetime import datetime
import pandas as pd

# project modul
from src.yahoofinance import download_symbol_from_yf


class TestDownloadYF(unittest.TestCase):
    def test_download_successful(self):
        # Call the function with mock data
        result = download_symbol_from_yf('AAPL', datetime(2022, 1, 2), datetime(2022, 1, 10))

        # Check if the function returns a DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        # Check if the returned DataFrame has the expected columns
        self.assertTrue(all(col in result.columns for col in ['Volume', 'AdjClose']))


if __name__ == '__main__':
    unittest.main()
