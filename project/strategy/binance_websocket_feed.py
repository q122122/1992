import websockets
import asyncio
import json
import time

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

async def connect_binance_ws():
    """
    Establishes a WebSocket connection to Binance USDT-M Futures,
    subscribes to specified streams, prints received messages,
    handles keep-alive, and implements reconnection logic.
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
    print("Starting Binance Futures WebSocket feed script...")
    try:
        asyncio.run(connect_binance_ws())
    except KeyboardInterrupt:
        print("WebSocket feed script stopped by user.")
    except Exception as e:
        print(f"Script level error: {e}")
