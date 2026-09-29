import yfinance as yf


# here i first download the data for the market anlyasis
data = yf.download(
    "RELIANCE.NS",
    period = "1y"
)

print(data.shape)
print(data.head())

print(data.info())