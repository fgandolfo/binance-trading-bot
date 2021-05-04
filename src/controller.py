from service import Binance_Service
from exceptions import BuyException, SellException, TickerException
from logger import logger_backend


class Binance_Controller:

    def __init__(self):
        self.service = Binance_Service()

    def get_ticker(self, symbol):
        try:
            return round(float(self.service.get_ticker_price(symbol)['bidPrice']), 8)

        except Exception as e:
            logger_backend.error(str(e))
            raise TickerException

    def buy_ticker(self, symbol, _qty):
        try:
            return self.service.make_buy_call(symbol, _qty, 8)

        except Exception as e:
            logger_backend.error(str(e))
            raise BuyException

    def sell_ticker(self, symbol, _qty):
        try:
            return self.service.make_sell_call(symbol, _qty, 8)

        except Exception as e:
            logger_backend.error(str(e))
            raise SellException