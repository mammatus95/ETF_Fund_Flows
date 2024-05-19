#!/usr/bin/python3
import unittest
from datetime import datetime
import pandas as pd
import requests

# project modul
from src.fund_flows import fetch_fund_flow_data


class TestDownloadETF(unittest.TestCase):
    def test_download(self):
        date_from = datetime.strptime("2024-05-01", "%Y-%m-%d")
        date_to = datetime.strptime("2024-05-01", "%Y-%m-%d")
        df = fetch_fund_flow_data("SPY", date_from, date_to)

        # Check the DataFrame is None
        self.assertIsNone(df)

if __name__ == '__main__':
    unittest.main()
