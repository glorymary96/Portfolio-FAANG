import yfinance as yf
import pandas as pd


def fetch_free_float(tickers):

    data_list = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)

        try:
            info = stock.info

            float_shares = info.get("floatShares", None)
            current_price = info.get("currentPrice", None)
            market_cap = info.get("marketCap", None)

            # Available share based on the market cap
            implied_shares = (market_cap/current_price) if (market_cap and current_price) else 0
            implied_shares_B = round(implied_shares/1e9, 4) if implied_shares else 0
            free_float_B = round(float_shares/1e9, 4) if float_shares else 0

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

    return pd.DataFrame(data_list)

def add_free_float_weight(df):

    df = df.copy()
    total = df["Free Float Shares (B)"].sum()
    if total and total>0:
        df["Free Float Weight"] = df["Free Float Shares (B)"]/total
    else:
        df["Free Float Weight"] = 0

    return df

if __name__ == "__main__":

    data = fetch_free_float(["GOOG", "AMZN"])
    data = add_free_float_weight(data)
    print(data)



