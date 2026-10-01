import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from src.indicator import calculate_sma



st.set_page_config(
    page_title="AlgoTrade India",
    page_icon="🇮🇳",
    layout="wide"
)




st.title("🇮🇳 AlgoTrade India")

st.caption(
    "Indian Stock Market Technical Analysis & Backtesting Dashboard"
)



# SIDEBAR


st.sidebar.header("⚙️ Market Settings")

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
    "Select Period",
    [
        "6mo",
        "1y",
        "2y",
        "5y"
    ]
)




with st.spinner("Loading market data..."):

    data = yf.Ticker(ticker).history(
        period=period
    )



if data.empty:

    st.error("Unable to load market data.")

    st.stop()

# Calculate moving averages
data["SMA20"] = calculate_sma(data, 20)
data["SMA50"] = calculate_sma(data, 50)



current_price = data["Close"].iloc[-1]

previous_price = data["Close"].iloc[-2]

change = current_price - previous_price

change_percent = (
    change / previous_price
) * 100




col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Current Price",
        f"₹{current_price:.2f}",
        f"{change_percent:.2f}%"
    )

with col2:

    st.metric(
        "Day High",
        f"₹{data['High'].iloc[-1]:.2f}"
    )

with col3:

    st.metric(
        "Day Low",
        f"₹{data['Low'].iloc[-1]:.2f}"
    )

with col4:

    st.metric(
        "Volume",
        f"{int(data['Volume'].iloc[-1]):,}"
    )



st.subheader("📈 Price Chart")


fig = go.Figure()


fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="Close Price"
    )
)

fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["SMA20"],
        mode="lines",
        name="SMA 20"
    )
)

fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["SMA50"],
        mode="lines",
        name="SMA 50"
    )
)


fig.update_layout(
    title=f"{ticker} Price Movement",
    xaxis_title="Date",
    yaxis_title="Price (₹)",
    height=500,
    hovermode="x unified"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# DATA TABLE
# -----------------------------

with st.expander("📋 View Historical Data"):

    st.dataframe(
        data.tail(20),
        use_container_width=True
    )