import streamlit as st
import yfinance as yf


# Page configuration
st.set_page_config(
    page_title="AlgoTrade India",
    page_icon="🇮🇳",
    layout="wide"
)


# Title
st.title("🇮🇳 AlgoTrade India")

st.write(
    "Indian Stock Market Technical Analysis & Backtesting Dashboard"
)


# Sidebar
st.sidebar.header("⚙️ Stock Settings")

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
        "5d",
        "1mo",
        "6mo",
        "1y",
        "2y",
        "5y"
    ]
)


# Download data
with st.spinner("Downloading market data..."):

    data = yf.Ticker(ticker).history(
        period=period
    )


# Check whether data was downloaded
if data.empty:

    st.error(
        "❌ No market data was received. Please try again."
    )

    st.stop()


# Dashboard
st.subheader(f"📊 {ticker}")


# Current price
current_price = data["Close"].iloc[-1]


# Metrics
col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Current Price",
        f"₹{current_price:.2f}"
    )

with col2:

    st.metric(
        "Highest Price",
        f"₹{data['High'].max():.2f}"
    )

with col3:

    st.metric(
        "Lowest Price",
        f"₹{data['Low'].min():.2f}"
    )


# Historical data
st.subheader("📋 Historical Data")

st.dataframe(
    data.tail(20),
    use_container_width=True
)

# import streamlit as st

# st.set_page_config(
#     page_title="AlgoTrade India",
#     page_icon="🇮🇳"
# )

# st.title("🇮🇳 AlgoTrade India")

# st.success("Streamlit is working!")

# st.write("If you can see this, the Streamlit app is running correctly.")