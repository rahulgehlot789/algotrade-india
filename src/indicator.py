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

def calculate_macd(data):

    close = data["Close"]

    ema12 = close.ewm(
        span = 12 , 
        adjust = False
    ).mean()

    ema26 = close.ewm(
        span = 26, 
        adjust = False
    ).mean()

    macd = ema12 - ema26

    signal = macd.ewm(
        span = 9 , 
        adjust = False
    ).mean()

    histogram = macd - signal

    return macd ,signal, histogram

if __name__ == "__main__":
    from data import get_stock_data

    data = get_stock_data("RELIANCE.NS")

    data["RSI"] = calculate_rsi(data)
    data["SMA20"] = calculate_sma(data, 20)
    data["SMA50"] = calculate_sma(data, 50)

    macd, signal, histogram = calculate_macd(data)

    data["MACD"] = macd
    data["Signal"] = signal
    data["Histogram"] = histogram



    print(data[["Close", "SMA20", "SMA50", "RSI", "MACD", "Signal","Histogram"]].tail(10))