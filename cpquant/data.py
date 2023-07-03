import pandas as pd
import numpy as np
import requests
import os
import datetime as dt
import plotly.graph_objects as go
import plotly.offline as ofl
import asyncio
import websockets
import json
import time
import threading
from websockets.sync.client import connect
# Load .env file
from dotenv import load_dotenv
load_dotenv()



class ThetaDataClient:
    def __init__(self):
        headers = {
            "Accept": "application/json"
        }
        data =requests.get("http://142.93.58.224/hist/option/eod?root=AAPL&start_date=20220901&end_date=20220915&strike=140000&exp=20220930&right=C", headers=headers)
        print(data)  # displays the data. You can also do print(data).
        print(data.json())


class AlpacaDataClient:
    def __init__(self):
        self.alpaca_data_secret = os.environ.get('ALPACA_DATA_SECRET_KEY')
        self.alpaca_data_public = os.environ.get('ALPACA_DATA_PUBLIC_KEY')
        if self.alpaca_data_secret is None or self.alpaca_data_public is None:
            raise Exception("Alpaca keys not found in environment variables!")
        
        self.alpaca_data_url = 'https://data.alpaca.markets/v2/'
        self.headers = {"accept": "application/json", 'APCA-API-KEY-ID': self.alpaca_data_public, 'APCA-API-SECRET-KEY': self.alpaca_data_secret}
        self.start_data = dt.datetime.now() - dt.timedelta(days=365)
        self.end_data = dt.datetime.now()
        # Format as YYY-MM-DD
        self.start_data = self.start_data.strftime('%Y-%m-%d')
        self.end_data = self.end_data.strftime('%Y-%m-%d')
    
    def do_get(self, url, params):
        result = requests.get(url, headers=self.headers, params=params)
        return result

    def get_bars(self, symbols, timeframe="1D", start=None, end=None, adjustment="raw", limit=1000, asof=None, feed="sip", currency="USD", page_token=None, only_market=False):
        # API Link: https://docs.alpaca.markets/reference/stockbars
        if start is None:
            start = self.start_data
        if end is None:
            end = self.end_data
        if asof is None:
            asof = dt.datetime.now().strftime('%Y-%m-%d')
        url = self.alpaca_data_url + 'stocks/bars'
        params = {
                    'symbols': symbols, 
                    'timeframe': timeframe, 
                    'start': start, 
                    'end': end, 
                    'adjustment': adjustment, 
                    'limit': limit,
                    'asof': asof,
                    'feed': feed,
                    'currency': currency,
                    'page_token': page_token
                    }
        result = self.do_get(url, params)
        try:
            data = result.json()

        except:
            print("Error retrieving bars: " + result.text)
            return None
        if (len(symbols.split(",")) > 1):
            dfs = {}
            for symbol in symbols.split(","):
                dfs[symbol] = pd.DataFrame(data["bars"][symbol])
                dfs[symbol].set_index("t", inplace=True)
                dfs[symbol].index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S.%fZ')
                dfs[symbol].index.name = "time"
                # Make column names more specific
                dfs[symbol].rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "n": "trades", "vw": "volume weighted"}, inplace=True)
                if only_market:
                    # Restrict time to market hours, our data is in UTC
                    dfs[symbol] = dfs[symbol].between_time('13:30', '20:00')
            return dfs
        df = pd.DataFrame(data["bars"][symbols])
        df.set_index("t", inplace=True)
        df.index.name = "time"
        df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S%fZ')
        # Make column names more specific
        df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "n": "trades", "vw": "volume weighted"}, inplace=True)
        if (only_market):
            # Restrict time to market hours
            df = df.between_time('13:30', '20:00')
        return df

    def get_latest_bars(self, symbols, feed="sip", currency="USD"):
        #API Link: https://docs.alpaca.markets/reference/stocklatestbars
        url = self.alpaca_data_url + 'stocks/bars/latest'
        params = {
                    'symbols': symbols,
                    'feed': feed,
                    'currency': currency
                }
        result = self.do_get(url, params)
        try:
            data = result.json()
        except:
            print("Error retrieving latest bars: " + result.text)
            return None
        if (len(symbols.split(",")) > 1):
            dfs = {}
            for symbol in symbols.split(","):
                dfs[symbol] = pd.DataFrame(data["bars"][symbol])
                dfs[symbol].set_index("t", inplace=True)
                dfs[symbol].index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S.%fZ')
                dfs[symbol].index.name = "time"
                # Make column names more specific
                dfs[symbol].rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "n": "trades", "vw": "volume weighted"}, inplace=True)
            return dfs
        df = pd.DataFrame(data["bars"][symbols])
        df.set_index("t", inplace=True)
        df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S.%fZ')
        df.index.name = "time"
        # Make column names more specific
        df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "n": "trades", "vw": "volume weighted"}, inplace=True)
        return df

    def get_exchange_codes(self):
        #API Link: https://docs.alpaca.markets/reference/stockmetaexchanges
        url = self.alpaca_data_url + 'meta/exchanges'
        params = {}
        result = self.do_get(url, params)
        try:
            data = result.json()
        except:
            print("Error retrieving exchange codes: " + result.text)
            return None
        return data

    def get_trades(self, symbols, start=None, end=None, limit=1000, asof=None, feed="sip", currency="USD", page_token=None):
        #API Link: https://docs.alpaca.markets/reference/stocktrades
        if start is None:
            start = self.start_data
        if end is None:
            end = self.end_data
        if asof is None:
            asof = dt.datetime.now().strftime('%Y-%m-%d')
        url = self.alpaca_data_url + 'stocks/trades'
        params = {
                    'symbols': symbols,
                    'start': start,
                    'end': end,
                    'limit': limit,
                    'asof': asof,
                    'feed': feed,
                    'currency': currency,
                    'page_token': page_token
                }
        result = self.do_get(url, params)
        try:
            data = result.json()
        except:
            print("Error retrieving trades: " + result.text)
            return None
        if len(symbols.split(",")) > 1:
            dfs = {}
            for symbol in symbols.split(","):
                dfs[symbol] = pd.DataFrame(data["trades"][symbol])
                dfs[symbol].set_index("t", inplace=True)
                dfs[symbol].index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S.%fZ')
                #Make column names more specific
                dfs[symbol].rename(columns={"p": "price", "s": "size", "c": "condition", "i": "trade_id", "x": "exchange_code", "z": "exchange"}, inplace=True)
            return dfs
        df = pd.DataFrame(data["trades"][symbols])
        df.set_index("t", inplace=True)
        df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S.%fZ')
        #Make column names more specific
        df.rename(columns={"p": "price", "s": "size", "c": "condition", "i": "trade_id", "x": "exchange_code", "z": "exchange"}, inplace=True)
        return df



    def plot_bars(self, df, notebook=False):
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])
        if not notebook:
            fig.show()
        else:
            ofl.iplot(fig)

class AlpacaRealtimeClient:
    def __init__(self) -> None:
        self.alpaca_data_secret = os.environ.get('ALPACA_DATA_SECRET_KEY')
        self.alpaca_data_public = os.environ.get('ALPACA_DATA_PUBLIC_KEY')
        if self.alpaca_data_secret is None or self.alpaca_data_public is None:
            raise Exception("Alpaca keys not found in environment variables!")
        self.stream_url = "wss://stream.data.alpaca.markets/v2/sip"
        self.socket = websockets.sync.client.connect(self.stream_url)
        auth = {"action": "auth", "key": self.alpaca_data_public, "secret": self.alpaca_data_secret}
        self.socket.send(json.dumps(auth))
        self.curr_quotes = []
        self.curr_trades = []
        self.curr_bars = []


    def subscribe_quotes(self, symbols):
        self.curr_quotes.extend(symbols)
        msg = {"action": "subscribe", "quotes": symbols}
        self.socket.send(json.dumps(msg))

    def subscribe_trades(self, symbols):
        self.curr_trades.extend(symbols)
        msg = {"action": "subscribe", "trades": symbols}
        self.socket.send(json.dumps(msg))

    def subscribe_bars(self, symbols, timeframe):
        self.curr_bars.extend(symbols)
        msg = {"action": "subscribe", "bars": symbols, "timeframe": timeframe}
        self.socket.send(json.dumps(msg))
    
    def unsubscribe_quotes(self, symbols):
        self.curr_quotes = [x for x in self.curr_quotes if x not in symbols]
        msg = {"action": "unsubscribe", "quotes": symbols}
        self.socket.send(json.dumps(msg))

    def unsubscribe_trades(self, symbols):
        self.curr_trades = [x for x in self.curr_trades if x not in symbols]
        msg = {"action": "unsubscribe", "trades": symbols}
        self.socket.send(json.dumps(msg))

    def unsubscribe_bars(self, symbols, timeframe):
        self.curr_bars = [x for x in self.curr_bars if x not in symbols]
        msg = {"action": "unsubscribe", "bars": symbols, "timeframe": timeframe}
        self.socket.send(json.dumps(msg))

    def close(self):
        self.socket.close()

    def listen(self, handler=None):
        while True:
            try:
                msg = self.socket.recv()
                if handler is not None:
                    handler(msg)
                else:
                    print(msg)
            except:
                print("Error receiving message from websocket!")
                break

    async def async_listen(self, handler):
        while True:
            try:
                msg = self.socket.recv()
                if handler is not None:
                    handler(msg)
                else:
                    print(msg)
                await asyncio.sleep(0) 
            except Exception as e:
                print(e)
                print("Error receiving message from websocket!")
                break


# def handler(msg):
#     print(msg, "Custom handle")

# def between_callback(client, handler):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)

#     loop.run_until_complete(client.async_listen(handler))
#     loop.close()

# rtClient = AlpacaRealtimeClient()
# rtClient.subscribe_quotes(["AAPL"])
# rtClient.subscribe_trades(["AAPL"])
# _thread = threading.Thread(target=between_callback, args=(rtClient, handler))
# _thread.start()
# count = 0
# while True:
#     time.sleep(1)
#     count += 1
#     if count == 10:
#         rtClient.unsubscribe_quotes(["AAPL"])
#         rtClient.unsubscribe_trades(["AAPL"])
#     if count == 20:
#         rtClient.subscribe_quotes(["TSLA"])
#     print("Waiting...")
# rtClient.close()


