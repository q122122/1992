import websockets
import asyncio
import json
import time

# OKX public WebSocket endpoint
OKX_PUBLIC_WS_ENDPOINT = "wss://ws.okx.com:8443/ws/v5/public"

# Subscription message for BTC-USDT-SWAP tickers
SUBSCRIBE_MESSAGE = {
    "op": "subscribe",
    "args": [
        {
            "channel": "tickers",
            "instType": "SWAP",
            "instId": "BTC-USDT-SWAP"
        }
    ]
}

# Keep-alive and reconnection settings
PING_INTERVAL_SECONDS = 25  # Send a "ping" string every 25 seconds
RECONNECT_DELAY_SECONDS = 5 # Wait 5 seconds before attempting to reconnect

async def connect_okx_ws():
    """
    Establishes a WebSocket connection to OKX public feed,
    subscribes to the BTC-USDT-SWAP ticker, prints received messages,
    handles keep-alive (sends "ping"), and implements reconnection logic.
    """
    while True:  # Outer loop for reconnection
        try:
            print(f"Attempting to connect to {OKX_PUBLIC_WS_ENDPOINT}...")
            async with websockets.connect(OKX_PUBLIC_WS_ENDPOINT) as websocket:
                print("Successfully connected to OKX WebSocket.")

                # Subscribe to the ticker stream
                await websocket.send(json.dumps(SUBSCRIBE_MESSAGE))
                print(f"Sent subscription message: {json.dumps(SUBSCRIBE_MESSAGE)}")

                last_ping_time = time.time()

                while True:  # Inner loop for receiving messages and sending pings
                    try:
                        # Set a timeout for receiving messages to allow periodic pings
                        # OKX server sends pings every 30s, client should respond with pong or send its own pings
                        # We will send our own pings proactively.
                        message = await asyncio.wait_for(websocket.recv(), timeout=PING_INTERVAL_SECONDS)
                        print(f"Received message: {message}")
                        
                        # If server sends 'ping', client should respond with 'pong'
                        if message == "ping":
                            await websocket.send("pong")
                            print("Received server ping, sent pong.")
                            last_ping_time = time.time() # Reset ping timer as we've interacted

                    except asyncio.TimeoutError:
                        # No message received for PING_INTERVAL_SECONDS, time to send our ping
                        print(f"No message received for {PING_INTERVAL_SECONDS}s, sending client ping...")
                        await websocket.send("ping")
                        last_ping_time = time.time()
                        print("Client ping sent.")
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(f"Connection closed error: {e}. Attempting to reconnect...")
                        break  # Break inner loop to trigger reconnection
                    except websockets.exceptions.ConnectionClosedOK as e:
                        print(f"Connection closed normally: {e}. Attempting to reconnect...")
                        break # Break inner loop to trigger reconnection
                    except Exception as e:
                        print(f"An unexpected error occurred in message loop: {e}. Attempting to reconnect...")
                        break # Break inner loop to trigger reconnection
                    
                    # Proactive ping if PING_INTERVAL_SECONDS has passed since last ping
                    # This ensures we meet the 30s requirement even if we are receiving messages
                    if time.time() - last_ping_time >= PING_INTERVAL_SECONDS:
                        print(f"Proactively sending client ping every {PING_INTERVAL_SECONDS} seconds...")
                        await websocket.send("ping")
                        last_ping_time = time.time()
                        print("Client ping sent.")

        except websockets.exceptions.WebSocketException as e:
            print(f"WebSocket connection/protocol error: {e}")
        except ConnectionRefusedError:
            print("Connection refused by the server.")
        except Exception as e:
            print(f"An error occurred during connection setup: {e}")

        print(f"Waiting {RECONNECT_DELAY_SECONDS} seconds before retrying...")
        await asyncio.sleep(RECONNECT_DELAY_SECONDS)

if __name__ == "__main__":
    print("Starting OKX WebSocket feed script...")
    try:
        asyncio.run(connect_okx_ws())
    except KeyboardInterrupt:
        print("OKX WebSocket feed script stopped by user.")
    except Exception as e:
        print(f"Script level error: {e}")
