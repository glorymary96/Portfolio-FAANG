import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

import warnings

from data.fetch_data import download_stock_prices

def fetch_compute_weight_free_float(tickers):
    """
    Fetch free float data for a list of tickers from Yahoo Finance and compute free-float weights.

    Parameters
    ----------
    tickers : list[str]
        List of stock tickers.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - Ticker
        - Implied Shares (B)
        - Free Float Shares (B)
        - Free Float (%)
        - Valid
        - Free Float Weight
    """

    data_list = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)

        try:
            info = stock.info

            float_shares = info.get("floatShares", None)
            current_price = info.get("currentPrice", None)
            market_cap = info.get("marketCap", None)

            # Available share based on the market cap
            implied_shares = (market_cap/current_price) if (market_cap and current_price) else None
            implied_shares_B = round(implied_shares/1e9, 4) if implied_shares else None
            free_float_B = round(float_shares/1e9, 4) if float_shares else None

            if implied_shares and float_shares:
                free_float_pct = round((float_shares/implied_shares)*100,3)
                valid = (float_shares <= implied_shares)
            else:
                free_float_pct = 0
                valid = False

            data_list.append({
                "Ticker": ticker,
                "Implied Shares (B)": implied_shares_B,
                "Free Float Shares (B)": free_float_B,
                "Free Float (%)": free_float_pct,
                "Valid": valid,
            })
        except Exception as e:
            print(f"Could not get data for {ticker}: {e}")

    df = pd.DataFrame(data_list)
    total = df["Free Float Shares (B)"].sum(skipna=True)
    if total and total > 0:
        df["Free Float Weight"] = (df["Free Float Shares (B)"] / total).round(5)
    else:
        df["Free Float Weight"] = None

    return df


def calculate_porfolio_from_stock_weights(weights, prices, initial_capital=1000):
    """
    Simulate the value of a weighted portfolio over time.

    Parameters
    ----------
    prices : pd.DataFrame
        Price history with tickers as columns and dates as index.
    weights : dict
        Mapping of {ticker -> portfolio weight}. Missing tickers are treated as 0.
    initial_investment : float, default=1000.0
        Starting portfolio value.

    Process
    -------
    1. Compute daily percentage returns for each ticker.
    2. Apply portfolio weights to calculate daily portfolio returns:
           r_portfolio,t = Σ_i w_i * r_{i,t}
    3. Compound returns to obtain cumulative portfolio value:
           V_t = V_{t-1} * (1 + r_portfolio,t)

    Returns
    -------
    pd.DataFrame
        Daily percentage returns for each ticker plus a "Portfolio Value" column.
    """
    w = pd.Series(weights, dtype=float).fillna(0.0)
    prices_pct_change = prices.pct_change().fillna(0.0)

    daily_returns = prices_pct_change.mul(w, axis=1).sum(axis=1)

    portfolio_values = initial_capital*(1+daily_returns).cumprod()

    port_returns = prices_pct_change.copy()
    port_returns["daily_returns"] = daily_returns
    port_returns["Portfolio Value"] = portfolio_values

    return port_returns

def build_portfolio_free_float(tickers, start_date, end_date, auto_adjust=True, price_field = "Close", initial_capital=1000):

    df_weights = fetch_compute_weight_free_float(tickers)

    valid = df_weights["Valid"] & df_weights["Free Float Weight"].notnull()

    if not valid.any():
        warnings.warn("No free float weights available, and thus portfolio cannot be built.")
        prices = download_stock_prices(tickers = tickers,
                                       start_date=start_date,
                                       end_date = end_date,
                                       auto_adjust=auto_adjust,
                                       price_field=price_field
                                       )
        port_returns = prices.pct_change().fillna(0.0)
        port_returns["daily_returns"] = 0.0
        port_returns["Portfolio Value"] = initial_capital
        return port_returns, df_weights

    weights = df_weights.loc[valid].set_index("Ticker")["Free Float Weight"].to_dict()

    prices = download_stock_prices(
            tickers = list(weights.keys()),
            start_date = start_date,
            end_date = end_date,
            auto_adjust=auto_adjust,
            price_field=price_field
            )

    port_returns = calculate_porfolio_from_stock_weights(weights, prices)

    return port_returns, df_weights

def build_portfolio_equal_weight(tickers, start_date, end_date, auto_adjust=True, price_field = "Close", initial_capital=1000):
    weights = {}

    for ticker in tickers:
        weights[ticker] = round(1/len(tickers),3)

    df_weights = pd.DataFrame([weights])

    prices = download_stock_prices(
        tickers=list(weights.keys()),
        start_date=start_date,
        end_date=end_date,
        auto_adjust=auto_adjust,
        price_field=price_field
    )

    port_returns = calculate_porfolio_from_stock_weights(weights, prices)

    return port_returns, df_weights

if __name__ == "__main__":

    tickers = ["META", "AMZN", "AAPL", "NFLX", "GOOGL"]
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    port_returns, df_weights = build_portfolio_equal_weight(
                    tickers = tickers,
                    start_date = start_date,
                    end_date = end_date,
                    initial_capital = 1000)

    ax = port_returns["Portfolio Value"].plot(figsize=(10, 6))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %Y"))
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value (USD)")
    ax.legend()
    ax.tick_params(axis="x", labelrotation=45)

    free_port_returns, free_df_weights = build_portfolio_free_float(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        initial_capital=1000)

    ax = free_port_returns["Portfolio Value"].plot(figsize=(10, 6))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %Y"))
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value (USD)")
    ax.legend()
    ax.tick_params(axis="x", labelrotation=45)



    plt.show()









