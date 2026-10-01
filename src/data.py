# import yfinance as yf

# def get_stock_data(ticker , period = "1y"):

#     data = yf.download(
#         ticker,
#         period = period,
#         auto_adjust= False
#     )

#     return data

# # get_stock_data("RELIANCE")

# if __name__ == "__main__":

#     data = get_stock_data("TCS.NS")
#     print(data.head())
#     print(f"Shape of data : {data.shape}")

import yfinance as yf


def get_stock_data(ticker, period="1y"):

    data = yf.download(
        ticker,
        period=period,
        auto_adjust=False
    )

    # Fix yfinance MultiIndex columns
    if hasattr(data.columns, "levels"):
        data.columns = data.columns.get_level_values(0)

    return data


if __name__ == "__main__":

    data = get_stock_data("RELIANCE.NS")

    print(data.head())
    print(data.columns)
    print("\nShape:", data.shape)