from local_settings import API_KEY, API_SECRET
from binance.client import Client
from logger import logger_backend
from binance.exceptions import BinanceAPIException


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
        _qty = round(_qty, precision)

        try:
            self.client.create_test_order(symbol=symbol, side="BUY", type="MARKET", quantity=_qty)
            return _qty

        except BinanceAPIException as e:
            if "LOT_SIZE" in str(e):
                return self.make_buy_call(symbol, _qty, precision-1)
        
            else:
                error = str(e)
                logger_backend.error(error)
                raise BinanceAPIException

        except Exception as e:
            error = str(e)
            logger_backend.error(error)
            raise Exception

    def make_sell_call(self, symbol, _qty, precision):
        _qty = round(_qty, precision)

        try:
            self.client.create_test_order(symbol=symbol, side="SELL", type="MARKET", quantity=_qty)
            return _qty

        except BinanceAPIException as e:
            if "LOT_SIZE" in str(e):
                return self.make_sell_call(symbol, _qty, precision-1)
        
            else:
                error = str(e)
                logger_backend.error(error)
                raise BinanceAPIException

        except Exception as e:
            error = str(e)
            logger_backend.error(error)
            raise Exception