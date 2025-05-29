import ccxt
import pandas as pd

def discover_arbitrage():
    """
    Fetches order book data from Binance and Bybit for BTC/USDT,
    calculates the arbitrage spread, and prints the results.
    """
    # Initialize exchange instances
    try:
        binance = ccxt.binance({
            'enableRateLimit': True, # Optional: helps avoid API rate limit issues
        })
        bybit = ccxt.bybit({
            'enableRateLimit': True, # Optional
        })
    except Exception as e:
        print(f"Error initializing exchanges: {e}")
        return

    symbol = 'BTC/USDT'

    # --- Fetch order books ---
    try:
        print(f"Fetching order book for {symbol} from Binance...")
        binance_order_book = binance.fetch_order_book(symbol)
        print(f"Fetching order book for {symbol} from Bybit...")
        bybit_order_book = bybit.fetch_order_book(symbol)
    except ccxt.NetworkError as e:
        print(f"Network error while fetching order books: {e}")
        return
    except ccxt.ExchangeError as e:
        print(f"Exchange error while fetching order books: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred while fetching order books: {e}")
        return

    # --- Extract best bid and ask prices ---
    # Best ask from Binance (lowest price someone is willing to sell at)
    binance_ask = None
    if binance_order_book and 'asks' in binance_order_book and len(binance_order_book['asks']) > 0:
        binance_ask = binance_order_book['asks'][0][0] # [price, volume]
    else:
        print(f"Could not retrieve valid ask data from Binance for {symbol}.")

    # Best bid from Bybit (highest price someone is willing to buy at)
    bybit_bid = None
    if bybit_order_book and 'bids' in bybit_order_book and len(bybit_order_book['bids']) > 0:
        bybit_bid = bybit_order_book['bids'][0][0] # [price, volume]
    else:
        print(f"Could not retrieve valid bid data from Bybit for {symbol}.")

    if binance_ask is None or bybit_bid is None:
        print("Could not determine arbitrage spread due to missing price data.")
        return

    # --- Calculate arbitrage spread ---
    arbitrage_spread = bybit_bid - binance_ask

    # --- Create and print DataFrame ---
    data = {
        'binance_ask': [binance_ask],
        'bybit_bid': [bybit_bid],
        'arb_spread': [arbitrage_spread]
    }
    df = pd.DataFrame(data)

    print("\nArbitrage Opportunity Analysis:")
    print(df)

if __name__ == '__main__':
    discover_arbitrage()
