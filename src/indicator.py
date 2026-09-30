import pandas as pd

def calculate_sma(data, window):

    # calculate the sma of following days
    # here the column name is Close
    return data["Close"].rolling(window = window).mean()


def calculate_rsi(data, window = 14):

    close = data["Close"]

    delta = close.diff()

    # here we calcute the gain and losses seperately
    gains = delta.clip(lower = 0)
    losses = -delta.clip(upper = 0)

    # now we find the averge gain and losses

    average_gain = gains.rolling(window = window).mean()
    average_loss = losses.rolling(window = window).mean()

    rs = average_gain / average_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


if __name__ == "__main__":
    from data import get_stock_data

    data = get_stock_data("RELIANCE.NS")

    data["RSI"] = calculate_rsi(data)
    data["SMA20"] = calculate_sma(data, 20)
    data["SMA50"] = calculate_sma(data, 50)

    print(data[["Close", "SMA20", "SMA50", "RSI"]].tail(10))