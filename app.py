import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

from src.indicator import (
    calculate_sma,
    calculate_rsi,
    calculate_macd
)

from src.stratagy import generate_signals

from src.backtest import run_backtest


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AlgoTrade India",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */
    .main {
        padding-top: 1rem;
    }

    /* Main title */
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

    /* Section headings */
    .section-title {
        font-size: 26px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        padding-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

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


# ============================================================
# SIDEBAR
# ============================================================

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


# ============================================================
# LOAD DATA
# ============================================================

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


# ============================================================
# DATA VALIDATION
# ============================================================

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


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

data["SMA20"] = calculate_sma(
    data,
    20
)

data["SMA50"] = calculate_sma(
    data,
    50
)

data["RSI"] = calculate_rsi(
    data
)

macd, macd_signal, macd_histogram = calculate_macd(
    data
)

data["MACD"] = macd

data["MACD_Signal"] = macd_signal

data["MACD_Histogram"] = macd_histogram


# ============================================================
# TRADING SIGNALS
# ============================================================

data = generate_signals(data)


# ============================================================
# BACKTEST
# ============================================================

result = run_backtest(
    data,
    initial_capital=initial_capital
)


# ============================================================
# BASIC MARKET DATA
# ============================================================

current_price = float(
    data["Close"].iloc[-1]
)

previous_price = float(
    data["Close"].iloc[-2]
)

price_change = (
    current_price - previous_price
)

price_change_percent = (
    price_change / previous_price
) * 100


current_rsi = float(
    data["RSI"].iloc[-1]
)

current_signal = data["Signal"].iloc[-1]

final_portfolio_value = float(
    result["Portfolio_Value"].iloc[-1]
)

strategy_return = (
    (final_portfolio_value - initial_capital)
    / initial_capital
) * 100


# ============================================================
# TOP KPI SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📊 Market Overview</div>',
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
        f"₹{final_portfolio_value:,.0f}"
    )


# ============================================================
# CURRENT SIGNAL
# ============================================================

st.markdown(
    '<div class="section-title">🎯 Current Trading Signal</div>',
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


# ============================================================
# PRICE CHART
# ============================================================

st.markdown(
    '<div class="section-title">📈 Price & Moving Averages</div>',
    unsafe_allow_html=True
)


price_fig = go.Figure()


# Closing price
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


# BUY markers
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


# SELL markers
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


# ============================================================
# RSI
# ============================================================

st.markdown(
    '<div class="section-title">📊 RSI — Relative Strength Index</div>',
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


# 70 level
rsi_fig.add_hline(
    y=70,
    line_dash="dash",
    annotation_text="Overbought — 70"
)


# 50 level
rsi_fig.add_hline(
    y=50,
    line_dash="dot",
    annotation_text="Neutral — 50"
)


# 30 level
rsi_fig.add_hline(
    y=30,
    line_dash="dash",
    annotation_text="Oversold — 30"
)


rsi_fig.update_layout(
    height=380,
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


# ============================================================
# MACD
# ============================================================

st.markdown(
    '<div class="section-title">📉 MACD</div>',
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


# ============================================================
# BACKTEST PERFORMANCE
# ============================================================

st.markdown(
    '<div class="section-title">💰 Backtest Performance</div>',
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


# ============================================================
# PERFORMANCE STATISTICS
# ============================================================

st.markdown(
    '<div class="section-title">📊 Performance Statistics</div>',
    unsafe_allow_html=True
)


first_price = float(
    data["Close"].iloc[0]
)

last_price = float(
    data["Close"].iloc[-1]
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


buy_signals = (
    data["Signal"] == "BUY"
).sum()


sell_signals = (
    data["Signal"] == "SELL"
).sum()


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Strategy Return",
        f"{strategy_return:+.2f}%"
    )


with col2:

    st.metric(
        "Buy & Hold Return",
        f"{buy_hold_return:+.2f}%"
    )


with col3:

    st.metric(
        "BUY Signals",
        str(buy_signals)
    )


with col4:

    st.metric(
        "Max Drawdown",
        f"{max_drawdown:.2f}%"
    )


# ============================================================
# SIGNAL TABLE
# ============================================================

st.markdown(
    '<div class="section-title">📋 Recent Trading Signals</div>',
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


# ============================================================
# RAW DATA
# ============================================================

with st.expander("📁 View Raw Historical Data"):

    st.dataframe(
        data.tail(50),
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AlgoTrade India • Educational technical analysis "
    "and historical backtesting project • "
    "Not financial advice"
)