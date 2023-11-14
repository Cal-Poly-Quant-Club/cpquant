from cpquant.data import AlpacaDataClient
import pandas as pd

def test_get_bars():
    client = AlpacaDataClient()
    bars = client.get_bars(["AAPL"])
    assert isinstance(bars, dict)
    assert len(bars) == 1
    assert "AAPL" in bars.keys()
    assert isinstance(bars["AAPL"], pd.DataFrame)