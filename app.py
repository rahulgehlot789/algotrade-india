import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from src.indicator import (
    calculate_sma,
    calculate_rsi,
    calculate_macd
)

from src.stratagy import generate_signals
from src.backtest import run_backtest
from src.metrics import calculate_metrics


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AlgoTrade India",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 17px;
        color: #888888;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 26px;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    div[data-testid="metric-container"] {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }

    section[data-testid="stSidebar"] {
        padding-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🇮🇳 AlgoTrade India</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Indian Stock Market Technical Analysis & Backtesting Dashboard'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Market Settings")

ticker = st.sidebar.selectbox(
    "Select Stock",
    [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "ITC.NS",
        "TATAMOTORS.NS"
    ]
)

period = st.sidebar.selectbox(
    "Historical Period",
    [
        "6mo",
        "1y",
        "2y",
        "5y"
    ],
    index=1
)

initial_capital = st.sidebar.number_input(
    "Initial Capital (₹)",
    min_value=10000,
    max_value=10000000,
    value=100000,
    step=10000
)

st.sidebar.divider()

st.sidebar.info(
    "This dashboard is for educational and historical "
    "backtesting purposes. It does not provide financial advice."
)


# =========================================================
# LOAD MARKET DATA
# =========================================================

with st.spinner("Loading market data..."):

    try:

        data = yf.Ticker(ticker).history(
            period=period
        )

    except Exception as e:

        st.error(
            f"Unable to download market data: {e}"
        )

        st.stop()


# =========================================================
# BASIC DATA VALIDATION
# =========================================================

if data.empty:

    st.error(
        "No market data was returned. "
        "Please try another stock or period."
    )

    st.stop()


required_columns = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]

missing_columns = [
    column
    for column in required_columns
    if column not in data.columns
]

if missing_columns:

    st.error(
        f"Missing data columns: {missing_columns}"
    )

    st.stop()


# =========================================================
# CLEAN MARKET DATA
# =========================================================

data = data[
    required_columns
].copy()


# Convert columns to numeric
for column in required_columns:

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce"
    )


# Remove invalid market rows
data = data.dropna(
    subset=[
        "Open",
        "High",
        "Low",
        "Close"
    ]
).copy()


if data.empty:

    st.error(
        "No valid market price data is available."
    )

    st.stop()


# =========================================================
# CALCULATE INDICATORS
# =========================================================

data["SMA20"] = calculate_sma(
    data,
    20
)

data["SMA50"] = calculate_sma(
    data,
    50
)

data["RSI"] = calculate_rsi(
    data,
    14
)


macd, macd_signal, macd_histogram = calculate_macd(
    data
)

data["MACD"] = macd
data["MACD_Signal"] = macd_signal
data["MACD_Histogram"] = macd_histogram


# =========================================================
# REMOVE INDICATOR NaN VALUES
# =========================================================

indicator_columns = [
    "SMA20",
    "SMA50",
    "RSI",
    "MACD",
    "MACD_Signal",
    "MACD_Histogram"
]

data = data.dropna(
    subset=indicator_columns
).copy()


if data.empty:

    st.error(
        "Not enough historical data to calculate "
        "all technical indicators."
    )

    st.stop()


# =========================================================
# GENERATE TRADING SIGNALS
# =========================================================

data = generate_signals(
    data
)


# =========================================================
# RUN BACKTEST
# =========================================================

result = run_backtest(
    data,
    initial_capital=initial_capital,
    transaction_cost=0.001
)


# =========================================================
# CALCULATE PERFORMANCE METRICS
# =========================================================

metrics = calculate_metrics(
    result,
    initial_capital=initial_capital
)


# =========================================================
# CURRENT MARKET VALUES
# =========================================================

current_price = float(
    data["Close"].iloc[-1]
)

previous_price = float(
    data["Close"].iloc[-2]
)

price_change = (
    current_price
    - previous_price
)

price_change_percent = (
    price_change
    / previous_price
) * 100


current_rsi = float(
    data["RSI"].iloc[-1]
)

current_signal = data[
    "Signal"
].iloc[-1]


# =========================================================
# PERFORMANCE VALUES
# =========================================================

strategy_return = metrics[
    "Strategy Return (%)"
]

buy_hold_return = metrics[
    "Buy & Hold Return (%)"
]

final_portfolio_value = metrics[
    "Final Portfolio Value"
]

max_drawdown = metrics[
    "Maximum Drawdown (%)"
]

win_rate = metrics[
    "Win Rate (%)"
]

completed_trades = metrics[
    "Completed Trades"
]

transaction_costs = metrics[
    "Transaction Costs"
]


# =========================================================
# MARKET OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📊 Market Overview'
    '</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Current Price",
        f"₹{current_price:,.2f}",
        f"{price_change_percent:+.2f}%"
    )


with col2:

    st.metric(
        "Current RSI",
        f"{current_rsi:.2f}"
    )


with col3:

    st.metric(
        "Strategy Return",
        f"{strategy_return:+.2f}%"
    )


with col4:

    st.metric(
        "Final Portfolio",
        f"₹{final_portfolio_value:,.2f}"
    )


# =========================================================
# CURRENT SIGNAL
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🎯 Current Trading Signal'
    '</div>',
    unsafe_allow_html=True
)


if current_signal == "BUY":

    st.success(
        f"🟢 BUY signal detected for {ticker}"
    )

elif current_signal == "SELL":

    st.error(
        f"🔴 SELL signal detected for {ticker}"
    )

else:

    st.info(
        f"🟡 HOLD signal for {ticker}"
    )


# =========================================================
# PRICE + MOVING AVERAGES
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📈 Price & Moving Averages'
    '</div>',
    unsafe_allow_html=True
)


price_fig = go.Figure()


# Close price
price_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="Close",
        line=dict(width=2)
    )
)


# SMA 20
price_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["SMA20"],
        mode="lines",
        name="SMA 20",
        line=dict(width=1.5)
    )
)


# SMA 50
price_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["SMA50"],
        mode="lines",
        name="SMA 50",
        line=dict(width=1.5)
    )
)


# BUY signals
buy_data = data[
    data["Signal"] == "BUY"
]


price_fig.add_trace(
    go.Scatter(
        x=buy_data.index,
        y=buy_data["Close"],
        mode="markers",
        name="BUY",
        marker=dict(
            symbol="triangle-up",
            size=11
        )
    )
)


# SELL signals
sell_data = data[
    data["Signal"] == "SELL"
]


price_fig.add_trace(
    go.Scatter(
        x=sell_data.index,
        y=sell_data["Close"],
        mode="markers",
        name="SELL",
        marker=dict(
            symbol="triangle-down",
            size=11
        )
    )
)


price_fig.update_layout(
    height=650,
    hovermode="x unified",
    xaxis_title="Date",
    yaxis_title="Price (₹)",
    margin=dict(
        l=20,
        r=20,
        t=50,
        b=20
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)


st.plotly_chart(
    price_fig,
    use_container_width=True
)


# =========================================================
# RSI
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📊 RSI — Relative Strength Index'
    '</div>',
    unsafe_allow_html=True
)


rsi_fig = go.Figure()


rsi_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["RSI"],
        mode="lines",
        name="RSI",
        line=dict(width=2)
    )
)


rsi_fig.add_hline(
    y=70,
    line_dash="dash",
    annotation_text="Overbought — 70"
)


rsi_fig.add_hline(
    y=50,
    line_dash="dot",
    annotation_text="Neutral — 50"
)


rsi_fig.add_hline(
    y=30,
    line_dash="dash",
    annotation_text="Oversold — 30"
)


rsi_fig.update_layout(
    height=400,
    yaxis=dict(
        range=[0, 100],
        title="RSI"
    ),
    xaxis_title="Date",
    hovermode="x unified",
    margin=dict(
        l=20,
        r=20,
        t=30,
        b=20
    )
)


st.plotly_chart(
    rsi_fig,
    use_container_width=True
)


# =========================================================
# MACD
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📉 MACD — Moving Average Convergence Divergence'
    '</div>',
    unsafe_allow_html=True
)


macd_fig = go.Figure()


macd_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["MACD"],
        mode="lines",
        name="MACD",
        line=dict(width=2)
    )
)


macd_fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["MACD_Signal"],
        mode="lines",
        name="Signal",
        line=dict(width=2)
    )
)


macd_fig.add_trace(
    go.Bar(
        x=data.index,
        y=data["MACD_Histogram"],
        name="Histogram"
    )
)


macd_fig.add_hline(
    y=0,
    line_dash="dot"
)


macd_fig.update_layout(
    height=420,
    xaxis_title="Date",
    yaxis_title="MACD",
    hovermode="x unified",
    margin=dict(
        l=20,
        r=20,
        t=30,
        b=20
    )
)


st.plotly_chart(
    macd_fig,
    use_container_width=True
)


# =========================================================
# BACKTEST PERFORMANCE
# =========================================================

st.markdown(
    '<div class="section-title">'
    '💰 Backtest Performance'
    '</div>',
    unsafe_allow_html=True
)


portfolio_fig = go.Figure()


portfolio_fig.add_trace(
    go.Scatter(
        x=result.index,
        y=result["Portfolio_Value"],
        mode="lines",
        name="Portfolio Value",
        line=dict(width=3)
    )
)


portfolio_fig.add_hline(
    y=initial_capital,
    line_dash="dash",
    annotation_text="Initial Capital"
)


portfolio_fig.update_layout(
    height=500,
    xaxis_title="Date",
    yaxis_title="Portfolio Value (₹)",
    hovermode="x unified",
    margin=dict(
        l=20,
        r=20,
        t=40,
        b=20
    )
)


st.plotly_chart(
    portfolio_fig,
    use_container_width=True
)


# =========================================================
# PERFORMANCE STATISTICS
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📊 Performance Statistics'
    '</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Strategy Return",
        f"{strategy_return:+.2f}%"
    )


with col2:

    st.metric(
        "Buy & Hold",
        f"{buy_hold_return:+.2f}%"
    )


with col3:

    st.metric(
        "Win Rate",
        f"{win_rate:.2f}%"
    )


with col4:

    st.metric(
        "Max Drawdown",
        f"{max_drawdown:.2f}%"
    )


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Completed Trades",
        int(completed_trades)
    )


with col2:

    st.metric(
        "Final Portfolio",
        f"₹{final_portfolio_value:,.2f}"
    )


with col3:

    st.metric(
        "Transaction Costs",
        f"₹{transaction_costs:,.2f}"
    )


# =========================================================
# TRADE HISTORY
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📜 Trade History'
    '</div>',
    unsafe_allow_html=True
)


trade_log = result.attrs.get(
    "trades",
    []
)


if trade_log:

    trade_df = pd.DataFrame(
        trade_log
    )

    st.dataframe(
        trade_df,
        use_container_width=True
    )

else:

    st.info(
        "No trades were generated for this period."
    )


# =========================================================
# RECENT SIGNALS
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📋 Recent Trading Signals'
    '</div>',
    unsafe_allow_html=True
)


signal_table = data[
    [
        "Close",
        "SMA20",
        "SMA50",
        "RSI",
        "MACD",
        "MACD_Signal",
        "Signal"
    ]
].tail(20).copy()


st.dataframe(
    signal_table,
    use_container_width=True
)


# =========================================================
# RAW DATA
# =========================================================

with st.expander(
    "📁 View Raw Historical Data"
):

    st.dataframe(
        data.tail(50),
        use_container_width=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AlgoTrade India • Educational technical analysis "
    "and historical backtesting project • "
    "Not financial advice"
)