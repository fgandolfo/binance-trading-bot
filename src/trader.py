from controller import Binance_Controller
from tradingview_ta import TA_Handler, Interval, Exchange
from logger import logger_main

MACD_INTERVAL = Interval.INTERVAL_1_MINUTE

class Binance_Trader:

    def __init__(self):
        self.controller = Binance_Controller()
        self.tickers = {}

    def add_ticker(self, symbol):
        self.tickers['{0}'.format(symbol)] = {
            'lastPrice': 0.0,
            'lastBuyPrice': 0.0,
            'lastSellPrice': 0.0,
            'lastPosition': 'SELL',
            'Quantity': 0.0,
            'avl_usdt': 125
        }

    def get_macd_indicator(self, symbol):
        _handler = TA_Handler(
            symbol= "{0}".format(symbol),
            screener= "crypto",
            exchange= "binance",
            interval= MACD_INTERVAL
        )
        _analysis = _handler.get_analysis()
        
        _ema10 = _analysis.indicators['EMA10']
        _ema20 = _analysis.indicators['EMA20']
        
        if _ema10 > _ema20:
            position = 'BUY'

        else:
            position = 'SELL'

        if position != self.tickers['{0}'.format(symbol)]['lastPosition']:
            return position
        
        return None

    def add_buy_amount(self, symbol, quantity, buy_price):
        self.tickers['{0}'.format(symbol)]['lastBuyPrice'] = buy_price
        self.tickers['{0}'.format(symbol)]['lastPosition'] = 'BUY'
        self.tickers['{0}'.format(symbol)]['Quantity'] += quantity

    def add_sell_amount(self, symbol, quantity, sell_price):
        self.tickers['{0}'.format(symbol)]['lastBuyPrice'] = sell_price
        self.tickers['{0}'.format(symbol)]['lastPosition'] = 'SELL'
        self.tickers['{0}'.format(symbol)]['Quantity'] -= quantity

    def execute_call(self, call, symbol, _qty, _price):
        self.tickers["{0}".format(symbol)]['lastPosition'] = call

        if 'BUY' in call:
            self.controller.buy_ticker(symbol, _qty)
            self.update_ticker(symbol, 'Quantity', _qty)
            self.update_ticker(symbol, 'lastBuyPrice', _price)
            self.update_ticker(symbol, 'avl_usdt', 0)

            return

        _asset_balance = float(self.controller.service.client.get_asset_balance(asset=symbol[:len(symbol)-4])['free'])
        _qty = self.controller.sell_ticker(symbol, _asset_balance)
        
        prev_qty = self.tickers['{0}'.format(symbol)]['Quantity']
        
        if (prev_qty - _qty) < 0:
            self.update_ticker(symbol, 'Quantity', 0)

        else:
            self.update_ticker(symbol, 'Quantity', prev_qty - _qty)
    
        self.update_ticker(symbol, 'avl_usdt', round(float(_qty * _price), 5))
        self.update_ticker(symbol, 'lastSellPrice', _price)
        self.update_ticker(symbol, 'lastBuyPrice', 0)
        return

    
    def update_ticker(self, symbol, attr, value):
        self.tickers['{0}'.format(symbol)]['{0}'.format(attr)] = value
        
    @staticmethod
    def get_percent_change(last_price, new_price):

        if last_price != 0:
            return round(((float(new_price)-last_price)/abs(last_price))*100.00, 4)

        return 0