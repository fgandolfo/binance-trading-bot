
class BuyException(Exception):
    """ exception raised when trying to make a buy order """
    pass

class SellException(Exception):
    """ exception raised when trying to make a sell order """
    pass

class TickerException(Exception):
    """ exception raised when trying to make a ticker call """
    pass