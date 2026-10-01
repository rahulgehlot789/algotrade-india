def calculate_metrics(
    result,
    initial_capital=100000
):
    """
    Calculate backtest performance metrics.
    """

    final_value = float(
        result["Portfolio_Value"].iloc[-1]
    )

    strategy_return = (
        (final_value - initial_capital)
        / initial_capital
    ) * 100

    

    first_price = float(
        result["Close"].iloc[0]
    )

    last_price = float(
        result["Close"].iloc[-1]
    )

    buy_hold_return = (
        (last_price - first_price)
        / first_price
    ) * 100

    

    running_max = (
        result["Portfolio_Value"]
        .cummax()
    )

    drawdown = (
        result["Portfolio_Value"]
        / running_max
        - 1
    ) * 100

    max_drawdown = float(
        drawdown.min()
    )

   

    trades = result.attrs.get(
        "trades",
        []
    )

    buy_trades = [
        trade
        for trade in trades
        if trade["Type"] == "BUY"
    ]

    sell_trades = [
        trade
        for trade in trades
        if trade["Type"] == "SELL"
    ]

    completed_trades = min(
        len(buy_trades),
        len(sell_trades)
    )


    winning_trades = 0
    losing_trades = 0

    for buy, sell in zip(
        buy_trades,
        sell_trades
    ):

        buy_cost = (
            buy["Value"]
            + buy["Cost"]
        )

        sell_revenue = (
            sell["Value"]
            - sell["Cost"]
        )

        pnl = (
            sell_revenue
            - buy_cost
        )

        if pnl > 0:
            winning_trades += 1

        elif pnl < 0:
            losing_trades += 1

    if completed_trades > 0:

        win_rate = (
            winning_trades
            / completed_trades
        ) * 100

    else:

        win_rate = 0

  

    total_transaction_cost = sum(
        trade["Cost"]
        for trade in trades
    )

    return {
        "Initial Capital": initial_capital,
        "Final Portfolio Value": final_value,
        "Strategy Return (%)": strategy_return,
        "Buy & Hold Return (%)": buy_hold_return,
        "Completed Trades": completed_trades,
        "Winning Trades": winning_trades,
        "Losing Trades": losing_trades,
        "Win Rate (%)": win_rate,
        "Maximum Drawdown (%)": max_drawdown,
        "Transaction Costs": total_transaction_cost
    }