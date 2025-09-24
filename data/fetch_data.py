import yfinance as yf
import pandas as pd

def download_stock_prices(tickers: list,
                  start_date:str,
                  end_date:str,
                  auto_adjust:bool = True,
                  price_field:str = 'Close') -> pd.DataFrame:
    """
    Download data for given tickers between start_date and end_date.

    Parameters:
        tickers (list): List of ticker symbols
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        auto_adjust (bool): Whether to adjust for splits/dividends (default: True)
        price_field (str): Price field to return (default: 'Close')
    """
    # To handle single tickers not given as list
    if isinstance(tickers, str):
        tickers = [tickers]

    data = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        auto_adjust=auto_adjust,
        progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        if price_field not in data.columns.levels[0]:
            raise ValueError(f"Price field '{price_field}' not found in data.")
        prices = data[price_field].copy()
    else:
        if price_field not in data.columns:
            raise ValueError(f"Price field '{price_field}' not found in data.")
        prices = data[price_field].copy()
        prices.columns = [tickers]

    # Handling missing tickers
    exists = [tic for tic in tickers if tic in prices.columns]
    prices = prices.reindex(columns = exists).sort_index()
    prices = prices.dropna().ffill()

    return prices

def load_stock_prices(tickers,start_date:str,end_date:str,auto_adjust:bool = True):
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=auto_adjust,
        progress=False,
    )["Close"]

    data = data.dropna(how="all").sort_index().ffill()

    return data


if __name__ == '__main__':
    tickers = ["META", "AMZN", "AAPL", "NFLX", "GOOGL"]
    #tickers = "META"
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    data = load_stock_prices(tickers, start_date, end_date)

    print(data.head())