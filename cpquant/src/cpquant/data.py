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



class ThetaDataClient:
    def __init__(self):
        headers = {
            "Accept": "application/json"
        }
        data =requests.get("http://142.93.58.224/hist/option/eod?root=AAPL&start_date=20220901&end_date=20220915&strike=140000&exp=20220930&right=C", headers=headers)
        print(data)  # displays the data. You can also do print(data).
        print(data.json())


class TradeGroup:
    def __init__(self, client, symbols, start=None, end=None, limit=10000, asof=None, feed="iex", currency="USD", page_token=None):
        self.client = client
        self.symbols = symbols
        self.start = start
        self.end = end
        self.limit = limit
        self.asof = asof
        self.feed = feed
        self.currency = currency
        self.page_token = page_token
        self.already_iterated = False

    def __iter__(self):
        self.trades = -1
        self.next_page_token = None
        return self
    
    def __next__(self):
        if self.next_page_token is None and self.trades == -1:
            self.trades, self.next_page_token = self.client.get_trades(self.symbols, self.start, self.end, self.limit, self.asof, self.feed, self.currency, self.page_token)
            return self.trades
        if self.next_page_token is not None:
            self.page_token = self.next_page_token
            self.trades, self.next_page_token = self.client.get_trades(self.symbols, self.start, self.end, self.limit, self.asof, self.feed, self.currency, self.page_token)
            self.already_iterated = True
            return self.trades
        elif self.trades is not None and not self.already_iterated:
            copy = self.trades
            self.trades = None
            return copy
        else:
            raise StopIteration
        
class OptionBarGroup:
    def __init__(self, client, symbols, timeframe="1D", start=None, end=None, limit=1000, page_token=None, sort="asc"):
        self.client = client
        self.symbols = symbols
        self.timeframe = timeframe
        self.start = start
        self.end = end
        self.limit = limit
        self.page_token = page_token
        self.sort = sort
        self.already_iterated = False

    def __iter__(self):
        self.bars = -1
        self.next_page_token = None
        return self
    
    def __next__(self):
        if self.next_page_token is None and self.bars == -1:
            self.bars, self.next_page_token = self.client.get_option_historical_bars(self.symbols, self.timeframe, self.start, self.end, self.limit, self.page_token, self.sort)
            return self.bars
        if self.next_page_token is not None:
            self.page_token = self.next_page_token
            self.bars, self.next_page_token = self.client.get_option_historical_bars(self.symbols, self.timeframe, self.start, self.end, self.limit, self.page_token, self.sort)
            self.already_iterated = True
            return self.bars
        elif self.bars is not None and not self.already_iterated:
            copy = self.bars
            self.bars = None
            return copy
        else:
            raise StopIteration

class AlpacaDataClient:
    """
    A class for retrieving data from Alpaca API.

    Attributes:
    -----------
    alpaca_data_secret : str
        Alpaca data secret key.
    alpaca_data_public : str
        Alpaca data public key.
    alpaca_data_url : str
        Alpaca data URL.
    headers : dict
        HTTP headers for Alpaca API requests.
    start_data : str
        Start date for data retrieval.
    end_data : str
        End date for data retrieval.
    """
    def __init__(self, env_file=".env"):
        load_dotenv(env_file)
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
    
    def _check_params(self, start=None, end=None, asof=None, symbols=None):
        """
        Check and update the parameters for a data query.

        Args:
            start (str or datetime.datetime, optional): The start date for the query. Defaults to the start date of the data.
            end (str or datetime.datetime, optional): The end date for the query. Defaults to the end date of the data.
            asof (str or datetime.datetime, optional): The as-of date for the query. Defaults to the current date.
            symbols (str or list of str, optional): The symbols to query. If a string, can be comma-separated.

        Returns:
            list of str: The updated symbols list.

        """
        if start is None:
            start = self.start_data
        if end is None:
            end = self.end_data
        if asof is None:
            asof = dt.datetime.now().strftime('%Y-%m-%d')
        if type(symbols) is not list:
            if "," in symbols:
                symbols = symbols.split(",")
            else:
                symbols = [symbols]
        return start, end, asof, symbols
    
    def _check_valid_response(self, result):
            """
            Checks if the response from the API is valid and returns the data if it is.
            If the response is not valid, prints an error message and returns None.

            Args:
            result (requests.Response): The response object returned by the API.

            Returns:
            dict or None: The data returned by the API if the response is valid, None otherwise.
            """
            try:
                data = result.json()
                return data
            except:
                print("Error retrieving bars: " + result.text)
                return None

    def _parse_data(self, data, symbols, renaming_dict, only_market, type):
        """
        Parses the raw data obtained from the API into a dictionary of pandas DataFrames, one for each symbol.

        Parameters:
        -----------
        data : dict
            The raw data obtained from the API.
        symbols : list of str
            The list of symbols to extract from the data.
        renaming_dict : dict
            A dictionary mapping the original column names to more specific ones.
        only_market : bool
            Whether to restrict the time range to market hours (13:30-20:00 UTC).

        Returns:
        --------
        dfs : dict of pandas DataFrames
            A dictionary mapping each symbol to its corresponding DataFrame, with columns renamed and index set to the timestamp.
        """
        dfs = {}
        try:
            if len(data[type]) == 0:
                return None, None
        except Exception as e:
            print("Error parsing data: " + str(e))
            print(data)
            raise e
        next_page_token = data.get("next_page_token")                        
        for symbol in symbols:
            dfs[symbol] = pd.DataFrame(data[type][symbol])
            dfs[symbol].set_index("t", inplace=True)
            dfs[symbol].index = dfs[symbol].index.map(lambda x: x if '.' in x else x[:-1] + '.000Z')
            dfs[symbol].index = pd.to_datetime(dfs[symbol].index, format='%Y-%m-%dT%H:%M:%S.%fZ')
            dfs[symbol].index.name = "time"
            # Make column names more specific
            dfs[symbol].rename(columns=renaming_dict, inplace=True)
            if only_market:
                # Restrict time to market hours, our data is in UTC
                dfs[symbol] = dfs[symbol].between_time('13:30', '20:00')
        return dfs, next_page_token
    
    def _format_option_chain(self, options_data, underlying_symbol):
        keys = options_data.keys()
        data = []
        for key in keys:
            key_data = {"symbol": key}
            time_stamp = options_data[key]['latestQuote']['t']
            bid_exchange = options_data[key]['latestQuote']['bx']
            bid_price = options_data[key]['latestQuote']['bp']
            bid_size = options_data[key]['latestQuote']['bs']
            ask_exchange = options_data[key]['latestQuote']['ax']
            ask_price = options_data[key]['latestQuote']['ap']
            ask_size = options_data[key]['latestQuote']['as']
            quote_condition = options_data[key]['latestQuote']['c']
            latest_trade = options_data[key].get('latestTrade')
            if latest_trade is None:
                trade_time = None
                trade_exchange = None
                trade_price = None
                trade_size = None
                trade_condition = None
            else:
                trade_time = latest_trade['t']
                trade_exchange = latest_trade['x']
                trade_price = latest_trade['p']
                trade_size = latest_trade['s']
                trade_condition = latest_trade['c']
            implied_volatility = options_data[key].get('impliedVolatility')
            greeks = options_data[key].get('greeks')
            if greeks is not None:
                delta = greeks['delta']
                gamma = greeks['gamma']
                theta = greeks['theta']
                vega = greeks['vega']
                rho = greeks['rho']
            else:
                delta = None
                gamma = None
                theta = None
                vega = None
                rho = None
            key_data["time_stamp"] = time_stamp
            key_data["bid_exchange"] = bid_exchange
            key_data["bid_price"] = bid_price
            key_data["bid_size"] = bid_size
            key_data["ask_exchange"] = ask_exchange
            key_data["ask_price"] = ask_price   
            key_data["ask_size"] = ask_size
            key_data["quote_condition"] = quote_condition
            key_data["trade_time"] = trade_time
            key_data["trade_exchange"] = trade_exchange
            key_data["trade_price"] = trade_price
            key_data["trade_size"] = trade_size
            key_data["trade_condition"] = trade_condition
            key_data["implied_volatility"] = implied_volatility
            key_data["delta"] = delta
            key_data["gamma"] = gamma
            key_data["theta"] = theta
            key_data["vega"] = vega
            key_data["rho"] = rho
            key_data["underlying_symbol"] = underlying_symbol
            key_data["expirtion_date"] = key[len(underlying_symbol):len(underlying_symbol)+6]
            # format into datetime
            key_data["expirtion_date"] = dt.datetime.strptime(key_data["expirtion_date"], '%y%m%d')
            key_data["option_type"] = key[len(underlying_symbol)+6]
            key_data["strike_price"] = key[len(underlying_symbol)+7:]
            # format into float
            # AAPL240621C00070000 corresponds to a strike price of 70.00
            key_data["strike_price"] = float(key_data["strike_price"][:-3] + '.' + key_data["strike_price"][-3:])

            data.append(key_data)
        df = pd.DataFrame(data)
        return df

    def do_get(self, url, params):
        result = requests.get(url, headers=self.headers, params=params)
        return result

    def get_bars(self, symbols, timeframe="1D", start=None, end=None, adjustment="raw", limit=1000, asof=None, feed="iex", currency="USD", page_token=None, only_market=False):
            """
            Retrieves historical bars for one or more symbols.

            Args:
                symbols (list): A list of symbols to retrieve bars for.
                timeframe (str): The timeframe for the bars. Default is "1D".
                start (str): The start date for the bars in "YYYY-MM-DD" format. Default is None.
                end (str): The end date for the bars in "YYYY-MM-DD" format. Default is None.
                adjustment (str): The adjustment method for the bars. Default is "raw", can also be "sip".
                limit (int): The maximum number of bars to retrieve. Default is 1000.
                asof (str): The date to retrieve bars as of in "YYYY-MM-DD" format. Default is None.
                feed (str): The data feed to retrieve bars from. Default is "iex".
                currency (str): The currency to retrieve bars in. Default is "USD".
                page_token (str): The page token to retrieve the next page of bars. Default is None.
                only_market (bool): Whether to only retrieve bars for market hours. Default is False.

            Returns:
                dict: A dictionary containing the bars data for the requested symbols.
            """
            start, end, asof, symbols = self._check_params(start, end, asof, symbols)
            url = self.alpaca_data_url + 'stocks/bars'
            params = {
                        'symbols': ",".join(symbols), 
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
            data = self._check_valid_response(result)
            if data is None:
                return data
            renaming_dict = {"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "n": "trades", "vw": "volume weighted"}
            return self._parse_data(data, symbols, renaming_dict, only_market, "bars")[0]

    def get_latest_bars(self, symbols, feed="iex", currency="USD"):
            """
            Retrieves the latest bars for the specified symbols from the Alpaca data API.

            Args:
                symbols (list): A list of symbols to retrieve data for.
                feed (str, optional): The data feed to use. Defaults to "iex", can also be "sip.
                currency (str, optional): The currency to use. Defaults to "USD".

            Returns:
                dict: A dictionary containing the latest bars data for the specified symbols.
            """
            url = self.alpaca_data_url + 'stocks/bars/latest'
            params = {
                        'symbols': ",".join(symbols),
                        'feed': feed,
                        'currency': currency
                    }
            result = self.do_get(url, params)
            data = self._check_valid_response(result)
            if data is None:
                return data
            renaming_dict = {"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "n": "trades", "vw": "volume weighted"}
            return self._parse_data(data, symbols, renaming_dict, False, "bars")[0]

    def get_trades_iterator(self, symbols, start=None, end=None, limit=10000, asof=None, feed="iex", currency="USD", page_token=None):
        return TradeGroup(self, symbols, start, end, limit, asof, feed, currency, page_token)

    def get_trades(self, symbols, start=None, end=None, limit=10000, asof=None, feed="iex", currency="USD", page_token=None):
            """
            Retrieves trade data for the specified symbols and time range.

            Args:
                symbols (str or list of str): The symbol to retrieve trade data for. Can only query 1 symbol at a time.
                start (str, optional): The start time for the trade data. Defaults to None.
                end (str, optional): The end time for the trade data. Defaults to None.
                limit (int, optional): The maximum number of trades to retrieve. Defaults to 1000.
                asof (str, optional): The timestamp to use for the trade data. Defaults to None.
                feed (str, optional): The data feed to use for the trade data. Defaults to "iex", can also be "sip".
                currency (str, optional): The currency to use for the trade data. Defaults to "USD".
                page_token (str, optional): The page token to use for pagination. Defaults to None.

            Returns:
                dict: A dictionary containing the trade data for the specified symbols and time range.
            """
            start, end, asof, symbols = self._check_params(start, end, asof, symbols)
            if limit == None:
                alpacaLimit = 10000
            else:
                alpacaLimit = limit
            if len(symbols) > 1:
                raise Exception("Can only retrieve trade data for 1 symbol at a time!")
            url = self.alpaca_data_url + 'stocks/trades'
            params = {
                        'symbols': symbols,
                        'start': start,
                        'end': end,
                        'limit': alpacaLimit,
                        'asof': asof,
                        'feed': feed,
                        'currency': currency,
                        'page_token': page_token
                    }
            result = self.do_get(url, params)
            data = self._check_valid_response(result)
            if data is None:
                return data
            renaming_dict = {"p": "price", "s": "size", "c": "condition", "i": "trade_id", "x": "exchange_code", "z": "exchange"}
            data, next_page_token = self._parse_data(data, symbols, renaming_dict, False, "trades")
            return data, next_page_token

    def get_exchange_codes(self):
            """
            Retrieves a list of exchange codes from the Alpaca API.

            Returns:
            - data: A list of exchange codes.
            """
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
    
    def get_option_chain(self, underlying_symbol, feed="indicative", limit=100, updated_since=None, page_token=None, type="call", strike_price_gte=None, strike_price_lte=None, expiration_date=None, expiration_date_gte=None, expiration_date_lte=None, root_symbol=None):
            """
            Retrieves an option chain for the specified symbol.

            Args:
            - underlying_symbol (str): The symbol to retrieve the option chain for.
            - feed (str): The data feed to use. Opra for paid data, indicative for free data.
            - limit (int): The maximum number of options to retrieve.
            - updated_since (str): The timestamp to use for the option chain.
            - page_token (str): The page token to use for pagination.
            - type (str): The type of option to retrieve.
            - strike_price_gte (float): The minimum strike price to retrieve.
            - strike_price_lte (float): The maximum strike price to retrieve.
            - expiration_date (str): The expiration date to retrieve options for.
            - expiration_date_gte (str): The minimum expiration date to retrieve options for.
            - expiration_date_lte (str): The maximum expiration date to retrieve options for.
            - root_symbol (str): The root symbol to retrieve options for.

            Returns:
            - data: A dictionary containing the option chain data.
            """
            url = 'https://data.alpaca.markets/v1beta1/options/snapshots/{}'.format(underlying_symbol)
            params = {
                'feed': feed,
                'limit': limit,
                'updated_since': updated_since,
                'page_token': page_token,
                'type': type,
                'strike_price_gte': strike_price_gte,
                'strike_price_lte': strike_price_lte,
                'expiration_date': expiration_date,
                'expiration_date_gte': expiration_date_gte,
                'expiration_date_lte': expiration_date_lte,
                'root_symbol': root_symbol
            }
            result = self.do_get(url, params)
            data = self._check_valid_response(result)
            next_page_token = data.get("next_page_token")
            options_data = data.get('snapshots')
            options_data = self._format_option_chain(options_data, underlying_symbol)
            return next_page_token, options_data
    
    def get_option_historical_bars(self, symbols, timeframe="1D", start=None, end=None, limit=1000, page_token=None, sort="asc"):
            """
            Retrieves historical bars for one or more option symbols.

            Args:
            - symbols (list): A list of symbols to retrieve bars for.
            - timeframe (str): The timeframe for the bars. Default is "1D".
            - start (str): The start date for the bars in "YYYY-MM-DD" format. Default is None.
            - end (str): The end date for the bars in "YYYY-MM-DD" format. Default is None.
            - limit (int): The maximum number of bars to retrieve. Default is 1000.
            - page_token (str): The page token to retrieve the next page of bars. Default is None.
            - sort (str): The sort order for the bars. Default is "asc".

            Returns:
            - data: A dictionary containing the bars data for the requested symbols.
            """
            start, end, asof, symbols = self._check_params(start, end, None, symbols)
            url = "https://data.alpaca.markets/v1beta1/options/bars"
            params = {
                'symbols': ",".join(symbols),
                'timeframe': timeframe,
                'start': start,
                'end': end,
                'limit': limit,
                'page_token': page_token,
                'sort': sort
            }
            result = self.do_get(url, params)
            data = self._check_valid_response(result)
            if data is None:
                return data
            renaming_dict = {"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "n": "trades", "vw": "volume weighted"}
            return self._parse_data(data, symbols, renaming_dict, False, "bars")[0]
    
    def get_option_historical_bars_iterator(self, symbols, timeframe="1D", start=None, end=None, limit=1000, page_token=None, sort="asc"):
        return OptionBarGroup(self, symbols, timeframe, start, end, limit, page_token, sort)

    def plot_bars(self, df, notebook=False):
        """
        Plots a candlestick chart using the provided dataframe.

        Args:
        - df (pandas.DataFrame): The dataframe containing the data to be plotted.
        - notebook (bool): If True, the plot will be displayed in the notebook. Otherwise, it will be displayed in a new window.

        Returns:
        - None
        """
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


# data_client = AlpacaDataClient()
# # Get trades
# # start_time = "2021-09-01T12:00:44.027Z"
# # end_time = "2021-09-01T12:14:01Z"
# start_time = "2023-11-20"
# end_time = "2023-11-21"
# trades = data_client.get_trades_iterator(["AAPL"], 
#                                 start = start_time, 
#                                 end = end_time)
# for trade in trades:
#     print(trade)

# tg = TradeGroup(10)
# for trade in tg:
#     print(trade)

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


# client = AlpacaDataClient()
# chain = client.get_option_chain("AAPL", strike_price_gte=200, limit=1000)
# page_token = chain[0]
# chain = chain[1]
# # sort by strike price and expiration date
# chain = chain.sort_values(by=["strike_price", "expirtion_date"])
# print(chain)

# historical_bars = client.get_option_historical_bars(["AAPL240621C00070000"], start="2024-03-01", end="2024-06-01", limit=1000)
# print(historical_bars)