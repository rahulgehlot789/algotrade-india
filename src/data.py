import yfinance as yf

def get_stock_data(ticker , period = "1y"):

    data = yf.download(
        ticker,
        period = period,
        auto_adjust= False
    )

    return data

# get_stock_data("RELIANCE")

if __name__ == "__main__":

    data = get_stock_data("TCS.NS")
    print(data.head())
    print(f"Shape of data : {data.shape}")

