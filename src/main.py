from controller import Binance_Controller
from trader import Binance_Trader
from logger import logger_main
from constants import *
from time import sleep
import curses

_slope = CALL_SLOPE_FIRST

controller = Binance_Controller()
trader = Binance_Trader()

def main(stdscr):

    MAX_X, MAX_Y, DIVIDER_BOTTOM = init_screen(stdscr)

    trader.add_ticker("XRPUSDT")
    trader.add_ticker("ADAUSDT")
    trader.add_ticker("ETHUSDT")
    trader.add_ticker("BTCUSDT")
    
    init_ui(stdscr, MAX_X, MAX_Y, DIVIDER_BOTTOM)
    update_usdt(stdscr, MAX_Y, MAX_X)

    while True:
        
        key = stdscr.getch()
        if key == ord('f') or key == ord('F'):
            sell_all_exit()
            update_usdt(stdscr, MAX_Y, MAX_X)
            sleep(5)
            break

        update_prices(stdscr, MAX_X, DIVIDER_BOTTOM)
        update_usdt(stdscr, MAX_Y, MAX_X)
        # sleep(10)

def update_prices(stdscr, MAX_X, DIVIDER_BOTTOM):
    _delta = 0

    for ticker in trader.tickers:
        _symbol = {
            'lastPrice': trader.tickers["{0}".format(ticker)]['lastPrice'],
            'lastBuyPrice': trader.tickers["{0}".format(ticker)]['lastBuyPrice'],
            'lastSellPrice': trader.tickers["{0}".format(ticker)]['lastSellPrice'],
            'lastPosition': trader.tickers["{0}".format(ticker)]['lastPosition'],
            'Quantity': trader.tickers["{0}".format(ticker)]['Quantity'],
            'avl_usdt': trader.tickers["{0}".format(ticker)]['avl_usdt']
        }

        _handler = {
            'new_price': controller.get_ticker,
            'macd_call': trader.get_macd_indicator,
        }

        last_price = _symbol.get('lastPrice')
        new_price = _handler.get('new_price')(ticker)

        _perc = {
            'nominal': trader.get_percent_change(last_price, new_price),
            'comparative': trader.get_percent_change(_symbol.get('lastBuyPrice'), _handler.get('new_price')(ticker))
        }

        if new_price >= last_price and last_price != 0:
            add_ticker_price(stdscr, _delta, new_price, _perc.get('nominal'), 'UP')
        
        elif new_price < last_price:
            add_ticker_price(stdscr, _delta, new_price,_perc.get('nominal'), 'DOWN')
        
        else:
            add_ticker_price(stdscr, _delta, new_price, _perc.get('nominal'))


        _qty = 0
        _call = trader.get_macd_indicator(ticker)
        if _call:
            _price = _handler.get('new_price')(ticker)
            avl_usdt = _symbol.get('avl_usdt')
            
            _qty = {
                'BUY': float(avl_usdt / _price),
                'SELL': float(_symbol.get('Quantity'))
            }.get(_call)

            trader.execute_call(_call, ticker, _qty, _price)

        add_trade_call(stdscr, _call, _qty, ticker)
        add_call_attr(stdscr, ticker, _perc.get('comparative'), _delta)

        trader.update_ticker(ticker, 'lastPrice', _handler.get('new_price')(ticker))
        stdscr.refresh()
        
        _delta += 1

def sell_all_exit():
    for ticker in trader.tickers:
        _qty = float(trader.tickers[str(ticker)]['Quantity'])
        _price = controller.get_ticker(str(ticker))

        if trader.tickers[str(ticker)]['lastPosition'] == "BUY":
            trader.execute_call("SELL", ticker, _qty, _price)
    
    return

def init_screen(stdscr):
    stdscr.nodelay(1)
    curses.resize_term(30, 120)
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    
    MAX_X = stdscr.getmaxyx()[1]
    MAX_Y = stdscr.getmaxyx()[0]
    DIVIDER_BOTTOM = MAX_Y-4

    return MAX_X, MAX_Y, DIVIDER_BOTTOM


def update_usdt(stdscr, MAX_Y, MAX_X):
    _usdt = 0

    for ticker in trader.tickers:
        _usdt += trader.tickers['{0}'.format(ticker)]['avl_usdt']

    stdscr.addstr(MAX_Y-2, 0, " " * MAX_X)
    stdscr.addstr(MAX_Y-2, 2, "CURRENT BALANCE SINCE STARTUP = ${0}".format(_usdt))
    stdscr.refresh()


def init_ui(stdscr, MAX_X, MAX_Y, DIVIDER_BOTTOM):
    stdscr.addstr(DIVIDER_TOP-2, 2, "Binance cryptocurrency ticker - BETA")
    stdscr.addstr(DIVIDER_TOP-2, (MAX_X//2)+LEN_PERCHG, "PRESS 'F' KEY TO EXIT")
    stdscr.addstr(DIVIDER_TOP, 0, "=" * MAX_X)
    stdscr.addstr(DIVIDER_BOTTOM, 0, "=" * MAX_X)

    stdscr.addstr(TICKER_BASELINE-2, 2, "TICKER\tPRICE")
    stdscr.addstr(TICKER_BASELINE-2, LEN_PERCHG, "PERCENT CHANGE")
    stdscr.addstr(TICKER_BASELINE-2, (MAX_X//2)+4, "TICKER")
    stdscr.addstr(TICKER_BASELINE-2, (MAX_X//2)+LEN_PRICE, "POSITION")
    stdscr.addstr(TICKER_BASELINE-2, (MAX_X//2)+LEN_PRICE+13, "GAIN/LOSS")

    stdscr.addstr(TICKER_BASELINE-1, 2, "-"*((MAX_X//2)-1))
    stdscr.addstr(TICKER_BASELINE-1, MAX_X//2, "|")
    stdscr.addstr(TICKER_BASELINE-1, (MAX_X//2)+1, "-"*((MAX_X//2)-1))
    stdscr.addstr(7, MAX_X//2, "|")
    stdscr.addstr(8, MAX_X//2, "|")
    stdscr.addstr(9, MAX_X//2, "|")
    stdscr.addstr(10, MAX_X//2, "|")
    stdscr.addstr(11, MAX_X//2, "|")
    stdscr.addstr(12, MAX_X//2, "|")
    stdscr.addstr(13, 0, "-"*MAX_X)

    _delta = 0
    for ticker in trader.tickers:
        stdscr.addstr(TICKER_BASELINE+_delta, 2, "{0}".format(ticker))
        stdscr.addstr(TICKER_BASELINE+_delta, (MAX_X//2)+4, "{0}".format(ticker))
        _delta += 1
    
    stdscr.refresh()


def add_trade_call(stdscr, _call, _qty, _symbol):
    global _slope
    MAX_X = stdscr.getmaxyx()[1]

    if _slope == CALL_SLOPE_LAST:
        _delta = CALL_SLOPE_FIRST
        
        while _delta < CALL_SLOPE_LAST:
            stdscr.addstr(_delta, 0, " " * MAX_X)
            _delta += 1

        _slope = CALL_SLOPE_FIRST
    
    if _call:
        stdscr.addstr(_slope, 2, "{0} {1} CALL EXECUTED FOR {2} {3}".format(TODAY_TIME, _call, round(_qty, 5), _symbol))
        _slope += 1
    
    return 


def add_call_attr(stdscr, ticker, perc_change, _delta):
    MAX_X = stdscr.getmaxyx()[1]

    if trader.tickers[str(ticker)]['lastPosition'] == "BUY":
        stdscr.addstr(TICKER_BASELINE+_delta, (MAX_X//2)+LEN_PRICE, "HOLD")
        stdscr.addstr(TICKER_BASELINE+_delta, (MAX_X//2)+LEN_PRICE+13, " "*10)
        
        if perc_change >= 0:
            stdscr.addstr(TICKER_BASELINE+_delta, (MAX_X//2)+LEN_PRICE+13, "{0}%".format(perc_change), curses.color_pair(1))
            return
        
        stdscr.addstr(TICKER_BASELINE+_delta, (MAX_X//2)+LEN_PRICE+13, "{0}%".format(perc_change), curses.color_pair(2))
        return

    stdscr.addstr(TICKER_BASELINE+_delta, (MAX_X//2)+LEN_PRICE, " "*4)
    stdscr.addstr(TICKER_BASELINE+_delta, (MAX_X//2)+LEN_PRICE, "---")
    stdscr.addstr(TICKER_BASELINE+_delta, (MAX_X//2)+LEN_PRICE+13, " "*10)
    stdscr.addstr(TICKER_BASELINE+_delta, (MAX_X//2)+LEN_PRICE+13, "---")

    return


def add_ticker_price(stdscr, _delta, price, perc_change, trend=None):
    if not trend:
        stdscr.addstr(TICKER_BASELINE+_delta, LEN_PERCHG, " "*10)
        stdscr.addstr(TICKER_BASELINE+_delta, LEN_PERCHG, "{0}%".format(perc_change))
        stdscr.addstr(TICKER_BASELINE+_delta, LEN_PRICE, "{0}".format(price))
        return

    if 'UP' in trend:
        stdscr.addstr(TICKER_BASELINE+_delta, LEN_PERCHG, " "*10)   
        stdscr.addstr(TICKER_BASELINE+_delta, LEN_PERCHG, "{0}%".format(perc_change))
        stdscr.addstr(TICKER_BASELINE+_delta, LEN_PRICE, "{0}".format(price), curses.color_pair(1))
        return

    stdscr.addstr(TICKER_BASELINE+_delta, LEN_PERCHG, " "*10)
    stdscr.addstr(TICKER_BASELINE+_delta, LEN_PERCHG, "{0}%".format(perc_change))
    stdscr.addstr(TICKER_BASELINE+_delta, LEN_PRICE, "{0}".format(price), curses.color_pair(2))
    return


curses.wrapper(main)