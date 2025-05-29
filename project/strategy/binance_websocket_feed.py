import websockets
import asyncio
import json
import time
from multiprocessing import Queue # For type hinting, can be removed if queue is always passed

# Binance USDT-M Futures WebSocket endpoint
BINANCE_FUTURES_WS_ENDPOINT = "wss://fstream.binance.com/ws"

# Subscription message for BTC/USDT aggregate trade and depth streams
SUBSCRIBE_MESSAGE = {
    "method": "SUBSCRIBE",
    "params": [
        "btcusdt@aggTrade",  # Aggregate Trades
        "btcusdt@depth"      # Best Bid/Ask and Order Book Updates (default frequency)
    ],
    "id": 1
}

# Keep-alive settings
PING_INTERVAL_SECONDS = 2.5 * 60  # Send a ping every 2.5 minutes
RECONNECT_DELAY_SECONDS = 5      # Wait 5 seconds before attempting to reconnect

async def connect_binance_ws(output_queue: Queue = None):
    """
    Establishes a WebSocket connection to Binance USDT-M Futures,
    subscribes to specified streams, and handles messages.

    If an output_queue is provided, raw JSON messages are put onto the queue
    as a tuple ('binance', message_string). Otherwise, messages are printed to stdout.

    Handles keep-alive and implements reconnection logic.

    Args:
        output_queue (multiprocessing.Queue, optional): A queue to send data to.
                                                        Defaults to None.
    """
    while True:  # Outer loop for reconnection
        try:
            print(f"Attempting to connect to {BINANCE_FUTURES_WS_ENDPOINT}...")
            async with websockets.connect(BINANCE_FUTURES_WS_ENDPOINT) as websocket:
                print("Successfully connected to Binance Futures WebSocket.")

                # Subscribe to streams
                await websocket.send(json.dumps(SUBSCRIBE_MESSAGE))
                print(f"Sent subscription message: {SUBSCRIBE_MESSAGE}")

                last_ping_time = time.time()

                while True:  # Inner loop for receiving messages and sending pings
                    try:
                        # Set a timeout for receiving messages to allow periodic pings
                        message = await asyncio.wait_for(websocket.recv(), timeout=PING_INTERVAL_SECONDS / 2)
                        
                        if output_queue:
                            # Send data to the queue if it's provided
                            try:
                                output_queue.put(('binance', message))
                            except Exception as e:
                                print(f"[BinanceFeed] Error putting message to queue: {e}")
                        else:
                            # Default behavior: print to console
                            print(f"Received message: {message}")
                        
                        # Reset last_ping_time if a message is received (optional, as server pings might be sufficient)
                        # last_ping_time = time.time() 
                    except asyncio.TimeoutError:
                        # No message received, time to send a ping
                        if time.time() - last_ping_time >= PING_INTERVAL_SECONDS:
                            print("No message received for a while, sending ping...")
                            await websocket.ping()
                            last_ping_time = time.time()
                            print("Ping sent.")
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(f"Connection closed error: {e}. Attempting to reconnect...")
                        break  # Break inner loop to trigger reconnection
                    except websockets.exceptions.ConnectionClosedOK as e:
                        print(f"Connection closed normally: {e}. Attempting to reconnect...")
                        break # Break inner loop to trigger reconnection
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}. Attempting to reconnect...")
                        break # Break inner loop to trigger reconnection
                    
                    # Proactive ping based on interval, regardless of received messages
                    # This is an alternative to timeout-based pinging
                    if time.time() - last_ping_time >= PING_INTERVAL_SECONDS:
                        print(f"Sending proactive ping every {PING_INTERVAL_SECONDS} seconds...")
                        await websocket.ping()
                        last_ping_time = time.time()
                        print("Proactive ping sent.")


        except websockets.exceptions.WebSocketException as e:
            print(f"WebSocket connection/protocol error: {e}")
        except ConnectionRefusedError:
            print("Connection refused by the server.")
        except Exception as e:
            print(f"An error occurred during connection setup: {e}")

        print(f"Waiting {RECONNECT_DELAY_SECONDS} seconds before retrying...")
        await asyncio.sleep(RECONNECT_DELAY_SECONDS)

if __name__ == "__main__":
    # This block allows the script to be run standalone for testing.
    # When run directly, it will default to printing messages to the console
    # as output_queue is None.
    print("Starting Binance Futures WebSocket feed script (standalone mode)...")
    try:
        # For testing the queue mechanism directly in standalone mode, you could do:
        # from multiprocessing import Queue as MpQueue
        # test_q = MpQueue()
        # asyncio.run(connect_binance_ws(output_queue=test_q))
        # # Then, you might want to get items from test_q here to see them.
        # # For simplicity, we just run it with default print behavior.
        asyncio.run(connect_binance_ws())
    except KeyboardInterrupt:
        print("WebSocket feed script stopped by user.")
    except Exception as e:
        print(f"Script level error: {e}")
