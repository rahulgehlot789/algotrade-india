import pandas as pd

def run_backtest(
    data,
    initial_capital=100000,
    transaction_cost=0.001
):
    """
    Run a long-only historical backtest.

    Trades are executed at the next trading day's Open
    to avoid same-day look-ahead bias.

    transaction_cost:
        0.001 = 0.10% transaction cost per trade.
    """

    data = data.copy()

    cash = float(initial_capital)
    shares = 0

    portfolio_values = []

    trades = []

    pending_signal = None

    for i in range(len(data)):

        current_close = float(data["Close"].iloc[i])

        

        if i > 0:

            execution_price = float(
                data["Open"].iloc[i]
            )

            signal = data["Signal"].iloc[i - 1]

            # BUY
            if signal == "BUY" and shares == 0:

                shares_to_buy = int(
                    cash // (
                        execution_price
                        * (1 + transaction_cost)
                    )
                )

                if shares_to_buy > 0:

                    trade_value = (
                        shares_to_buy
                        * execution_price
                    )

                    cost = (
                        trade_value
                        * transaction_cost
                    )

                    cash -= (
                        trade_value
                        + cost
                    )

                    shares = shares_to_buy

                    trades.append({
                        "Date": data.index[i],
                        "Type": "BUY",
                        "Price": execution_price,
                        "Shares": shares_to_buy,
                        "Value": trade_value,
                        "Cost": cost
                    })

            # SELL
            elif signal == "SELL" and shares > 0:

                trade_value = (
                    shares
                    * execution_price
                )

                cost = (
                    trade_value
                    * transaction_cost
                )

                cash += (
                    trade_value
                    - cost
                )

                trades.append({
                    "Date": data.index[i],
                    "Type": "SELL",
                    "Price": execution_price,
                    "Shares": shares,
                    "Value": trade_value,
                    "Cost": cost
                })

                shares = 0

      

        portfolio_value = (
            cash
            + shares * current_close
        )

        portfolio_values.append(
            portfolio_value
        )

    # Add portfolio value
    data["Portfolio_Value"] = portfolio_values

    # Store trade information
    data.attrs["trades"] = trades

    return data


def get_trade_log(result):
    """
    Return completed trade information.
    """

    trades = result.attrs.get(
        "trades",
        []
    )

    return trades

def calculate_metrics(result, initial_capital=100000):

    final_value = result["Portfolio_Value"].iloc[-1]

    # Total strategy return
    total_return = (
        (final_value - initial_capital)
        / initial_capital
    ) * 100

    # Buy and hold return
    first_price = result["Close"].iloc[0]
    last_price = result["Close"].iloc[-1]

    buy_hold_return = (
        (last_price - first_price)
        / first_price
    ) * 100

    # Number of BUY signals
    total_trades = (
        result["Signal"] == "BUY"
    ).sum()

    # Maximum drawdown
    running_max = result["Portfolio_Value"].cummax()

    drawdown = (
        result["Portfolio_Value"] / running_max - 1
    ) * 100

    max_drawdown = drawdown.min()

    return {
        "Initial Capital": initial_capital,
        "Final Portfolio Value": final_value,
        "Strategy Return (%)": total_return,
        "Buy & Hold Return (%)": buy_hold_return,
        "Number of BUY Signals": total_trades,
        "Maximum Drawdown (%)": max_drawdown
    }


if __name__ == "__main__":
    from data import get_stock_data
    from indicator import (
        calculate_sma,
        calculate_rsi,
        calculate_macd
    )
    from stratagy import generate_signals

    # Get data
    data = get_stock_data("RELIANCE.NS")

    # Indicators
    data["SMA20"] = calculate_sma(data, 20)
    data["SMA50"] = calculate_sma(data, 50)
    data["RSI"] = calculate_rsi(data)

    macd, signal, histogram = calculate_macd(data)

    data["MACD"] = macd
    data["MACD_Signal"] = signal
    data["MACD_Histogram"] = histogram

    # Trading signals
    data = generate_signals(data)

    # Backtest
    result = run_backtest(
        data,
        initial_capital=100000
    )

    metrics = calculate_metrics(result)
    
    for key, value in metrics.items():
        print(f"{key}: {value:.2f}%")


    print(result[
        [
            "Close",
            "Signal",
            "Portfolio_Value"
        ]
    ].tail(20))

    print("\nInitial Capital: ₹100,000")
    print(
        "Final Portfolio Value:",
        round(result["Portfolio_Value"].iloc[-1], 2)
    )