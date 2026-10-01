import pandas as pd
import numpy as np

from src.indicator import (
    calculate_sma,
    calculate_rsi,
    calculate_macd
)


def sample_data():
    dates = pd.date_range(
        start="2025-01-01",
        periods=100,
        freq="D"
    )

    close = np.linspace(
        100,
        200,
        100
    )

    return pd.DataFrame(
        {
            "Close": close
        },
        index=dates
    )


def test_sma():

    data = sample_data()

    sma = calculate_sma(
        data,
        20
    )

    assert len(sma) == len(data)
    assert sma.iloc[-1] > 0


def test_rsi():

    data = sample_data()

    rsi = calculate_rsi(
        data,
        14
    )

    valid_rsi = rsi.dropna()

    assert len(valid_rsi) > 0
    assert (valid_rsi >= 0).all()
    assert (valid_rsi <= 100).all()


def test_macd():

    data = sample_data()

    macd, signal, histogram = calculate_macd(
        data
    )

    assert len(macd) == len(data)
    assert len(signal) == len(data)
    assert len(histogram) == len(data)