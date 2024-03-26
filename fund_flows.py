from datetime import date, datetime
from typing import Dict, List
import time

import pandas as pd
import requests
import json
import yaml

# project moduls
import yahoofinance as yf_modul
import plots as plot_modul
# ----------------------------------------------------------------------------------------------------------------------------

headers = {
    "authority": "api-prod.etf.com",
    "method": "GET",
    "path": f"/private/apps/fundflows/SPY/charts?startDate=2022-01-01&endDate=2023-01-01",
    "scheme": "https",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Content-Type": "application/json",
    "Dnt": "1",
    "If-None-Match": "W/\"8b09-E20zV8i3lylx2EqkjQDu72dYFSE\"",
    "Sec-Ch-Ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# ----------------------------------------------------------------------------------------------------------------------------

def fetch_fund_flow_data(ticker, date_from: date, date_to: date, raw_path: str = None):
    """"
    Parameters:
    -----------
    ticker :  as string

    Returns:
    ---------
    pandas pandas.dataframe or None
    
    """
    
    date_from_str = date_from.strftime("%Y%m%d")
    date_to_str = date_to.strftime("%Y%m%d")

    headers.update({"path" : f"/private/apps/fundflows/{ticker}/charts?startDate={date_from_str}&endDate={date_to_str}"})

    url = (f"https://api-prod.etf.com/private/apps/fundflows/"
           f"{ticker}/charts?startDate={date_from_str}&endDate={date_to_str}"
          )

    # print(url)
    res = requests.get(url, headers=headers)
    
    if res.ok:
        json_data = res.json()
        
        try:
            df = pd.DataFrame(json_data["data"]["results"]["data"])
            # print(df)
            df.index = pd.to_datetime(df["asOf"])
            df.index.name = "Date"
            df.drop(columns=["asOf"], inplace=True)
            return df
        except (KeyError, TypeError) as e:
            print(f"Error processing json data: {e}")
            return None
    else:
        print(f"Status Code: {res.status_code} - Fetch Fund Flows Data Failed")
        return None

# ----------------------------------------------------------------------------------------------------------------------------

def create_fund_flow_df(flow_df, pice_df):
    
    merged_df = pd.merge(flow_df, pice_df, how='inner', on="Date", left_index=False, right_index=False)
    merged_df["negative"] = merged_df["value"]
    merged_df["positive"] = merged_df["value"]
    merged_df.loc[merged_df["negative"]>0, "negative"] = 0
    merged_df.loc[merged_df["positive"]<0, "positive"] = 0
    return merged_df

# ----------------------------------------------------------------------------------------------------------------------------

def load_yaml(yaml_file, yaml_path='./'):
    """
    Parameters:
    -----------
    yaml_file : name of yaml file
    """
    with open(f"{yaml_path}/{yaml_file}", 'r') as yhand:
        config_data = yaml.safe_load(yhand)
    return config_data

# ----------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    # load config
    config = load_yaml('config.yml')

    date_from= datetime.strptime(config['date_from'], "%Y-%m-%d")
    date_to  = datetime.today()
    raw_path = config['raw_path']
    back_idx = config['back_idx']
    tickers  = {**config['etf_bonds'], 
                **config['etf_stocks'],  
                # **config['etf_'],
                }
    
    # start time profiling
    t1 = time.time()
    

    for ticker in tickers:
        print(f"Ticker: {ticker} Time: {round(time.time() - t1,2)} seconds")
        flow_df = fetch_fund_flow_data(ticker, date_from=date_from, date_to=date_to, raw_path=raw_path)
        pice_df = yf_modul.download_symbol_from_yf(ticker, date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d'))
        fund_flow_df = create_fund_flow_df(flow_df, pice_df)

        # print(fund_flow_df.head(10))

        # create plots

        #plot_modul.basic_plot(ticker, fund_flow_df)
        plot_modul.flow_plot(ticker, fund_flow_df)
        plot_modul.plot_stock_info(ticker, fund_flow_df, back_idx, flowflag=True)
        plot_modul.fund_flow_plotter(ticker, fund_flow_df, date_subset_range=[datetime(2020, 1, 1), datetime.today()], 
                                     tick_freq=25, plot_volume=True, plot_price=True)



    t2 = time.time()
    print(f"\nTime profiling: {round(t2 - t1,2)} seconds")