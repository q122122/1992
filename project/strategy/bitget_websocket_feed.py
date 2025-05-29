import websockets
import asyncio
import json
import time

# Bitget V2 public WebSocket endpoint
BITGET_PUBLIC_WS_ENDPOINT = "wss://ws.bitget.com/v2/ws/public"

# Subscription message for BTCUSDT USDT-FUTURES tickers
SUBSCRIBE_MESSAGE = {
    "op": "subscribe",
    "args": [
        {
            "instType": "USDT-FUTURES",
            "channel": "ticker",
            "instId": "BTCUSDT"
        }
    ]
}

# Keep-alive and reconnection settings
CLIENT_PING_INTERVAL_SECONDS = 25  # Send a "ping" string every 25 seconds
RECONNECT_DELAY_SECONDS = 5      # Wait 5 seconds before attempting to reconnect

async def connect_bitget_ws():
    """
    Establishes a WebSocket connection to Bitget public feed,
    subscribes to the BTCUSDT futures ticker, prints received messages,
    handles keep-alive (sends "ping"), and implements reconnection logic.
    """
    while True:  # Outer loop for reconnection
        try:
            print(f"Attempting to connect to {BITGET_PUBLIC_WS_ENDPOINT}...")
            # Bitget V2 endpoint requires a User-Agent, though websockets library might send a default one.
            # For specific headers: extra_headers={'User-Agent': 'MyClient'}
            async with websockets.connect(BITGET_PUBLIC_WS_ENDPOINT) as websocket:
                print("Successfully connected to Bitget WebSocket.")

                # Subscribe to the ticker stream
                await websocket.send(json.dumps(SUBSCRIBE_MESSAGE))
                print(f"Sent subscription message: {json.dumps(SUBSCRIBE_MESSAGE)}")

                last_client_ping_time = time.time()

                while True:  # Inner loop for receiving messages and sending pings
                    try:
                        # Set a timeout for receiving messages to allow periodic pings
                        # The websockets library automatically handles server pings by sending pongs.
                        # We will also send our own client-side pings.
                        message = await asyncio.wait_for(websocket.recv(), timeout=CLIENT_PING_INTERVAL_SECONDS)
                        print(f"Received message: {message}")
                        
                        # Bitget might send a ping as a JSON string like '{"event":"ping"}' or just 'ping'
                        # The library handles 'real' ping control frames.
                        # If it's a string message 'ping', we should send 'pong'
                        if message == "ping": # Or handle specific JSON ping from Bitget if needed
                            await websocket.send("pong")
                            print("Received server text ping, sent text pong.")
                            last_client_ping_time = time.time() # Reset ping timer

                    except asyncio.TimeoutError:
                        # No message received for CLIENT_PING_INTERVAL_SECONDS, time to send our client ping
                        print(f"No message received for {CLIENT_PING_INTERVAL_SECONDS}s, sending client ping...")
                        await websocket.send("ping") # Bitget expects a "ping" string for application-level ping
                        last_client_ping_time = time.time()
                        print("Client text ping sent.")
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
                    if time.time() - last_client_ping_time >= CLIENT_PING_INTERVAL_SECONDS:
                        print(f"Proactively sending client text ping every {CLIENT_PING_INTERVAL_SECONDS} seconds...")
                        await websocket.send("ping")
                        last_client_ping_time = time.time()
                        print("Client text ping sent.")

        except websockets.exceptions.WebSocketException as e:
            print(f"WebSocket connection/protocol error: {e}")
        except ConnectionRefusedError:
            print("Connection refused by the server.")
        except Exception as e:
            print(f"An error occurred during connection setup: {e}")

        print(f"Waiting {RECONNECT_DELAY_SECONDS} seconds before retrying...")
        await asyncio.sleep(RECONNECT_DELAY_SECONDS)

if __name__ == "__main__":
    print("Starting Bitget WebSocket feed script...")
    try:
        asyncio.run(connect_bitget_ws())
    except KeyboardInterrupt:
        print("Bitget WebSocket feed script stopped by user.")
    except Exception as e:
        print(f"Script level error: {e}")
