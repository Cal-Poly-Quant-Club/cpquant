import pandas as pd
import numpy as np
import os

class AlpacaTradeClient:
    def __init__(self):
        self.alpaca_trade_secret = os.environ.get('ALPACA_TRADE_SECRET_KEY')
        self.alpaca_trade_public = os.environ.get('ALPACA_TRADE_PUBLIC_KEY')
        if self.alpaca_trade_secret is None or self.alpaca_trade_public is None:
            raise Exception("Alpaca keys not found in environment variables!")
        
        self.alpaca_trade_url = 'https://paper-api.alpaca.markets'
