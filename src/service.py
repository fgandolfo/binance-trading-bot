from binance.exceptions import BinanceAPIException
from local_settings import API_KEY, API_SECRET
from binance.client import Client
from logger import logger_backend
import math

class Binance_Service:

    def __init__(self):
        self.client = Client(API_KEY, API_SECRET)
        logger_backend.info("Binance Client connected successfuly")

    def get_ticker_price(self, symbol):
        try:
            return self.client.get_orderbook_ticker(symbol="{0}".format(symbol))

        except Exception as e:
            error = str(e)
            logger_backend.error(error)
            raise Exception

    def make_buy_call(self, symbol, _qty, precision):
        
        _qty = self.round_down(_qty, precision)

        try:
            self.client.create_order(symbol=symbol, side=self.client.SIDE_BUY, type=self.client.ORDER_TYPE_MARKET, quantity=_qty)
            logger_backend.info("Buy call executed for {0} {1}".format(_qty, symbol))
            return _qty

        except BinanceAPIException as e:
            if "LOT_SIZE" in str(e) or "Account has insufficient balance for requested action" in str(e):
                return self.make_buy_call(symbol, _qty, precision-1)
        
            else:
                error = str(e)
                logger_backend.error(error)
                raise BinanceAPIException

        except Exception as e:
            error = str(e)
            logger_backend.error(error)
            raise Exception

    def make_sell_call(self, symbol, _asset_balance, precision):

        _qty = self.round_down(_asset_balance, precision)

        if _qty > _asset_balance:
            _qty = float(self.client.get_asset_balance(asset=symbol[:len(symbol)-4])['free'])
            precision = 9

        try:
            self.client.create_order(symbol=symbol, side=self.client.SIDE_SELL, type=self.client.ORDER_TYPE_MARKET, quantity=_qty)
            logger_backend.info("Sell call executed for {0} {1}".format(_qty, symbol))
            self.client.transfer_dust(asset=symbol[:len(symbol)-4]['free'])
            
            return _qty

        except BinanceAPIException as e:
            if "LOT_SIZE" in str(e) or "Account has insufficient balance for requested action" in str(e):
                return self.make_sell_call(symbol, _qty, precision-1)
        
            else:
                error = str(e)
                logger_backend.error(error)
                raise BinanceAPIException

        except Exception as e:
            error = str(e)
            logger_backend.error(error)
            raise Exception
    
    @staticmethod
    def round_down(n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n * multiplier) / multiplier
