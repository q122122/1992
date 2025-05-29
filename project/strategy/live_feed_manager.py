import multiprocessing
import time
import json
import queue # For queue.Empty exception

# Relative imports, assuming the script is run as part of the 'project.strategy' package
# or from the 'project/strategy/' directory.
from .common_data_structures import OrderBookUpdate
from .binance_websocket_feed import connect_binance_ws

# --- Data Storage ---
# Stores the latest OrderBookUpdate for each symbol from each exchange.
# Structure: market_data[symbol][exchange_name] = OrderBookUpdate_instance
# For this script, we are only handling 'binance'
market_data = {} 

# --- Parser Function for Binance Messages ---
def parse_binance_message(raw_json_string: str) -> OrderBookUpdate | None:
    """
    Parses a raw JSON string from a Binance WebSocket feed (aggTrade or depthUpdate)
    and converts it into an OrderBookUpdate object.

    Args:
        raw_json_string (str): The raw JSON message string from the feed.

    Returns:
        OrderBookUpdate | None: An OrderBookUpdate object if parsing is successful
                                and data is relevant, otherwise None.
    """
    try:
        data = json.loads(raw_json_string)
        event_type = data.get('e')
        symbol = data.get('s') # Standard symbol like BTCUSDT
        
        # Standardize symbol format (e.g., BTC/USDT)
        # Binance uses "BTCUSDT", we might prefer "BTC/USDT"
        if symbol and len(symbol) > 3 and not '/' in symbol:
            # A simple heuristic for common pairs like BTCUSDT, ETHUSDT
            if "USDT" in symbol.upper():
                standard_symbol = symbol.upper().replace("USDT", "/USDT")
            elif "BUSD" in symbol.upper():
                 standard_symbol = symbol.upper().replace("BUSD", "/BUSD")
            # Add more rules if needed for other quote currencies
            else: # Fallback for less common symbols
                standard_symbol = f"{symbol[:3]}/{symbol[3:]}" if len(symbol) > 3 else symbol
        else:
            standard_symbol = symbol


        if event_type == 'aggTrade':
            # Aggregate Trade Stream
            # Example: {"e":"aggTrade","E":1672517950001,"s":"BTCUSDT","a":12345,"p":"16500.00","q":"0.001","f":100,"l":105,"T":1672517950000,"m":true,"M":true}
            trade_price = float(data.get('p'))
            trade_timestamp_ms = data.get('T') # Trade time
            
            if trade_price and standard_symbol and trade_timestamp_ms:
                # For aggTrade, we don't have explicit bid/ask.
                # We can use the trade price as a proxy for both, or for a 'last_price'.
                # Here, we simplify by setting bid and ask to the trade price.
                return OrderBookUpdate(exchange_name='binance',
                                       symbol=standard_symbol,
                                       best_bid=trade_price,
                                       best_ask=trade_price,
                                       timestamp=trade_timestamp_ms / 1000.0) # Convert ms to s
            else:
                print(f"[Parser - Binance aggTrade] Missing data in message: {data}")
                return None

        elif event_type == 'depthUpdate':
            # Depth Update Stream (from @depth)
            # Example: {"e":"depthUpdate","E":1672517950002,"s":"BTCUSDT","U":157,"u":160,"b":[["16500.00","0.001"],...],"a":[["16501.00","0.002"],...]}
            event_time_ms = data.get('E') # Event time
            
            best_bid_price = None
            best_ask_price = None

            # 'b' for bids, 'a' for asks. These are arrays of [price, quantity].
            # The best bid is the first entry in 'b' (highest price).
            # The best ask is the first entry in 'a' (lowest price).
            if data.get('b') and len(data['b']) > 0 and len(data['b'][0]) > 0:
                best_bid_price = float(data['b'][0][0])
            
            if data.get('a') and len(data['a']) > 0 and len(data['a'][0]) > 0:
                best_ask_price = float(data['a'][0][0])

            if best_bid_price is not None and best_ask_price is not None and standard_symbol and event_time_ms:
                return OrderBookUpdate(exchange_name='binance',
                                       symbol=standard_symbol,
                                       best_bid=best_bid_price,
                                       best_ask=best_ask_price,
                                       timestamp=event_time_ms / 1000.0) # Convert ms to s
            else:
                # This might happen if an update clears one side of the book momentarily
                # or if the data is incomplete.
                # print(f"[Parser - Binance depthUpdate] Missing bid/ask data or symbol in message: {data}")
                return None
        
        else:
            # Message type not handled (e.g., could be a subscription confirmation)
            # print(f"[Parser - Binance] Unhandled event type '{event_type}': {raw_json_string[:100]}")
            return None

    except json.JSONDecodeError as e:
        print(f"[Parser - Binance] JSONDecodeError: {e} for message: {raw_json_string}")
        return None
    except Exception as e:
        print(f"[Parser - Binance] Unexpected error parsing message: {e}. Data: {raw_json_string}")
        return None


# --- Main Manager Logic ---
if __name__ == "__main__":
    print("Starting Live Feed Manager...")

    # Create a multiprocessing Queue for data from feed processes
    data_queue = multiprocessing.Queue()

    # --- Start Binance Feed Process ---
    # The `connect_binance_ws` function is imported from binance_websocket_feed.py
    # It's designed to accept an `output_queue` argument.
    print("Initializing Binance feed process...")
    binance_feed_process = multiprocessing.Process(
        target=connect_binance_ws,
        args=(data_queue,), # Pass the queue to the feed process
        daemon=True # Optional: make it a daemon process so it exits when main process exits
    )
    binance_feed_process.start()
    print("Binance feed process started.")

    # --- Main Loop to Process Data from Queue ---
    print("Listening for data from feed processes...")
    running_duration_seconds = 60 # Run for 60 seconds for testing
    start_time = time.time()

    try:
        while time.time() - start_time < running_duration_seconds:
            try:
                # Get data from the queue with a timeout
                # Data format expected: (exchange_name_str, raw_message_json_str)
                exchange_name, raw_message = data_queue.get(timeout=1.0)

                if exchange_name == 'binance':
                    parsed_update = parse_binance_message(raw_message)
                    if parsed_update:
                        # Store the parsed data
                        if parsed_update.symbol not in market_data:
                            market_data[parsed_update.symbol] = {}
                        market_data[parsed_update.symbol][parsed_update.exchange_name] = parsed_update
                        
                        print(f"LIVE MANAGER: Received {parsed_update}")
                        # Here, you could also trigger arbitrage calculations if new data is available
                        # for multiple exchanges for the same symbol.
                else:
                    print(f"LIVE MANAGER: Received data from unknown exchange: {exchange_name}")

            except queue.Empty:
                # Timeout occurred, no data in queue. This is normal.
                # print("LIVE MANAGER: Queue empty, continuing...")
                continue
            except Exception as e:
                print(f"LIVE MANAGER: Error processing message from queue: {e}")
                time.sleep(0.1) # Avoid rapid looping on persistent error

    except KeyboardInterrupt:
        print("LIVE MANAGER: KeyboardInterrupt received. Shutting down...")
    finally:
        print("LIVE MANAGER: Terminating feed processes...")
        if binance_feed_process.is_alive():
            binance_feed_process.terminate() # Terminate the child process
            binance_feed_process.join(timeout=5) # Wait for it to exit
            if binance_feed_process.is_alive():
                print("LIVE MANAGER: Binance feed process did not terminate cleanly, killing.")
                binance_feed_process.kill() # Force kill if terminate fails

        print("LIVE MANAGER: Shutdown complete.")
