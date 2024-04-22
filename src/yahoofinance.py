import yfinance as yf
import pandas as pd


def download_symbol_from_yf(symbol, start_date, end_date, interval="1d"):
    """
    Parameters:
    -----------
    symbol     : Symbol of Stock, Currency, ETF or Index on YahooFinance
                 (Search on website to ensure you have the right symbol)
    start_date : start date
    end_date   : end date
    interval   : interval default "1d"
    full_flag  : max period yes : True

    Returns:
    ---------
    pandas.dataframe
    if failed it returns -1

    ValueError: the provided symbol is invalid or if the date range specified is not valid.
    IOError: if there is a problem with the input/output operation,
             such as issues with network connectivity or file system errors.
    KeyError: if the data returned from Yahoo Finance does not contain the expected keys.
    TimeoutError: when the request to Yahoo Finance times out due to slow network connectivity
    ConnectionError: when there is a problem establishing a connection to the Yahoo Finance server,
                     such as when the server is down or when there are network connectivity issues.
    PermissionError: when there are permission issues with the file system
    """
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        assert df.shape[0] != 0
    except ValueError as e:
        print(f"ValueError for {symbol}. \nError-Message: {e}")
        print("This usally happens the provided symbol is invalid or if the date range specified is not valid. ")
        return -1
    except IOError as e:
        print(f"IOError for {symbol}. \nError-Message: {e}")
        print("This usally happens there is a problem with the input/output operation. ")
        return -1
    except KeyError as e:
        print(f"KeyError for {symbol}. \nError-Message: {e}")
        print("This usally happens when returned data does not contain the expected keys. ")
        return -1
    except ConnectionError as e:
        print(f"IndexError for {symbol}. \nError-Message: {e}")
        print("This usally happens when there is a problem establishing a connection to the Yahoo Finance server. ")
        return -1
    except TimeoutError as e:
        print(f"TimeoutError for {symbol}. \nError-Message: {e}")
        print("This usally happens when the request to Yahoo Finance times out due to slow network connectivity. ")
        return -1
    except IndexError as e:
        print(f"IndexError for {symbol}. \nError-Message: {e}")
        return -1
    except TypeError as e:
        print(f"TypeError for {symbol}. \nError-Message: {e}")
        return -1
    except Exception as e:
        print(f"Error for {symbol}. \nError-Message: {e}")
        return -1
    finally:
        print(f"{symbol} was downloaded. Dim: {df.shape}")

    # Adj Close: price adjusted for splits and dividend and/or capital gain distributions
    df['AdjClose'] = df['Adj Close']
    df = df.drop(columns=['Adj Close', 'Close', 'Open', 'Low', 'High'])
    df.index = pd.to_datetime(df.index)
    return df
