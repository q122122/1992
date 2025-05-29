import time

class OrderBookUpdate:
    """
    Represents a simplified order book update from a cryptocurrency exchange.

    This data structure standardizes the format for basic bid/ask information
    received from different exchange feeds, facilitating common processing.
    """
    def __init__(self, exchange_name: str, symbol: str, best_bid: float, best_ask: float, timestamp: float = None):
        """
        Initializes an OrderBookUpdate instance.

        Args:
            exchange_name (str): The name of the exchange (e.g., "binance", "bybit").
            symbol (str): The trading symbol (e.g., "BTC/USDT", "ETH/USDT").
            best_bid (float): The highest current bid price.
            best_ask (float): The lowest current ask price.
            timestamp (float, optional): The Unix timestamp of the update.
                                         Defaults to the current time if not provided.
        """
        self.exchange_name: str = exchange_name
        self.symbol: str = symbol
        self.best_bid: float = best_bid
        self.best_ask: float = best_ask
        self.timestamp: float = timestamp if timestamp is not None else time.time()

    def __repr__(self) -> str:
        """
        Returns a string representation of the OrderBookUpdate instance.
        """
        return (f"OrderBookUpdate(exchange='{self.exchange_name}', symbol='{self.symbol}', "
                f"bid={self.best_bid}, ask={self.best_ask}, ts={self.timestamp:.3f})")

# Example usage (can be removed or commented out if not needed for direct execution):
if __name__ == '__main__':
    # Example of creating an instance
    update = OrderBookUpdate(exchange_name="example_exchange",
                             symbol="BTC/USD",
                             best_bid=50000.1,
                             best_ask=50000.5)
    print(update)

    update_with_ts = OrderBookUpdate(exchange_name="another_exchange",
                                     symbol="ETH/USD",
                                     best_bid=4000.0,
                                     best_ask=4000.2,
                                     timestamp=time.time() - 5) # 5 seconds ago
    print(update_with_ts)
