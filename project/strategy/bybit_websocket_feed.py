import websockets
import asyncio
import json
import time

# Bybit V5 public linear perpetuals WebSocket endpoint
BYBIT_V5_LINEAR_PUBLIC_WS_ENDPOINT = "wss://stream.bybit.com/v5/public/linear"

# Subscription message for BTCUSDT tickers
SUBSCRIBE_MESSAGE = {
    "op": "subscribe",
    "args": ["tickers.BTCUSDT"]
}

# Ping message
PING_MESSAGE = {"op": "ping"}

# Keep-alive and reconnection settings
CLIENT_PING_INTERVAL_SECONDS = 15  # Send a ping every 15 seconds (Bybit requires ping if no msg for 20s)
RECONNECT_DELAY_SECONDS = 5      # Wait 5 seconds before attempting to reconnect

async def connect_bybit_ws():
    """
    Establishes a WebSocket connection to Bybit V5 linear public feed,
    subscribes to the BTCUSDT ticker, prints received messages,
    handles keep-alive (sends JSON ping), and implements reconnection logic.
    """
    while True:  # Outer loop for reconnection
        try:
            print(f"Attempting to connect to {BYBIT_V5_LINEAR_PUBLIC_WS_ENDPOINT}...")
            async with websockets.connect(BYBIT_V5_LINEAR_PUBLIC_WS_ENDPOINT) as websocket:
                print("Successfully connected to Bybit V5 WebSocket.")

                # Subscribe to the ticker stream
                await websocket.send(json.dumps(SUBSCRIBE_MESSAGE))
                print(f"Sent subscription message: {json.dumps(SUBSCRIBE_MESSAGE)}")

                last_ping_time = time.time()

                while True:  # Inner loop for receiving messages and sending pings
                    try:
                        # Set a timeout for receiving messages to allow periodic pings
                        # Bybit server sends pongs in response to our pings.
                        # We need to send a ping if no messages (including pongs) are received from the server for 20s.
                        # We will send our pings proactively every 15s.
                        message = await asyncio.wait_for(websocket.recv(), timeout=CLIENT_PING_INTERVAL_SECONDS * 2) # Larger timeout for recv
                        print(f"Received message: {message}")
                        # No need to reset last_ping_time on every message for Bybit,
                        # as we rely on proactive pings. Server pongs confirm connection is alive.

                    except asyncio.TimeoutError:
                        # This timeout means we haven't received *any* message (data or pong)
                        # for a while. It's good practice to ensure our pings are going out.
                        print(f"No message received for a while, ensuring proactive ping is sent if due.")
                        # The proactive ping below will handle this.
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(f"Connection closed error: {e}. Attempting to reconnect...")
                        break  # Break inner loop to trigger reconnection
                    except websockets.exceptions.ConnectionClosedOK as e:
                        print(f"Connection closed normally: {e}. Attempting to reconnect...")
                        break # Break inner loop to trigger reconnection
                    except Exception as e:
                        print(f"An unexpected error occurred in message loop: {e}. Attempting to reconnect...")
                        break # Break inner loop to trigger reconnection
                    
                    # Proactive client ping if CLIENT_PING_INTERVAL_SECONDS has passed since last ping
                    current_time = time.time()
                    if current_time - last_ping_time >= CLIENT_PING_INTERVAL_SECONDS:
                        print(f"Sending proactive client JSON ping every {CLIENT_PING_INTERVAL_SECONDS} seconds...")
                        await websocket.send(json.dumps(PING_MESSAGE))
                        last_ping_time = current_time
                        print(f"Client JSON ping sent: {json.dumps(PING_MESSAGE)}")

        except websockets.exceptions.WebSocketException as e:
            print(f"WebSocket connection/protocol error: {e}")
        except ConnectionRefusedError:
            print("Connection refused by the server.")
        except Exception as e:
            print(f"An error occurred during connection setup: {e}")

        print(f"Waiting {RECONNECT_DELAY_SECONDS} seconds before retrying...")
        await asyncio.sleep(RECONNECT_DELAY_SECONDS)

if __name__ == "__main__":
    print("Starting Bybit V5 WebSocket feed script...")
    try:
        asyncio.run(connect_bybit_ws())
    except KeyboardInterrupt:
        print("Bybit V5 WebSocket feed script stopped by user.")
    except Exception as e:
        print(f"Script level error: {e}")
