def generate_signals(data):
    """
    Generate BUY, SELL, and HOLD signals.
    """

    data = data.copy()

    data["Signal"] = "HOLD"

    buy_condition = (
        (data["SMA20"] > data["SMA50"])
        & (data["RSI"] > 50)
        & (data["MACD"] > data["MACD_Signal"])
    )

    sell_condition = (
        (data["SMA20"] < data["SMA50"])
        | (data["RSI"] < 40)
        | (data["MACD"] < data["MACD_Signal"])
    )

    data.loc[buy_condition, "Signal"] = "BUY"
    data.loc[sell_condition, "Signal"] = "SELL"

    return data

if __name__ == "__main__":
    from data import get_stock_data
    from indicator import (
        calculate_sma,
        calculate_rsi,
        calculate_macd
    )

    data = get_stock_data("RELIANCE.NS")

    # SMA
    data["SMA20"] = calculate_sma(data, 20)
    data["SMA50"] = calculate_sma(data, 50)

    # RSI
    data["RSI"] = calculate_rsi(data)

    # MACD
    macd, signal, histogram = calculate_macd(data)

    data["MACD"] = macd
    data["MACD_Signal"] = signal
    data["MACD_Histogram"] = histogram

    # Generate signals
    data = generate_signals(data)

    print(
        data[
            [
                "Close",
                "SMA20",
                "SMA50",
                "RSI",
                "MACD",
                "MACD_Signal",
                "Signal"
            ]
        ].tail(20)
    )