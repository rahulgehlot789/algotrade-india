import pandas as pd

def calculate_sma(data, window):

    # calculate the sma of following days
    # here the column name is Close
    return data["Close"].rolling(window = window).mean()

if __name__ == "__main__":
    from data import get_stock_data

    data = get_stock_data("RELIANCE.NS")

    data["SMA20"] = calculate_sma(data, 20)
    data["SMA50"] = calculate_sma(data, 50)

    print(data[["Close", "SMA20", "SMA50"]].tail(10))