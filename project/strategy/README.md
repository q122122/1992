# Arbitrage Discovery Strategy

## Description

The `arbitrage_discovery.py` script is designed to identify potential arbitrage opportunities for the `BTC/USDT` trading pair. It operates by:

1.  Fetching real-time order book data from two major cryptocurrency exchanges: Binance and Bybit.
2.  Specifically, it looks for:
    *   The best bid price on Bybit (the highest price someone is willing to buy BTC).
    *   The best ask price on Binance (the lowest price someone is willing to sell BTC).
3.  Calculating the potential arbitrage spread: `Bybit Best Bid - Binance Best Ask`. A positive spread could indicate an opportunity to buy on Binance and simultaneously sell on Bybit for a profit (before considering fees and execution risks).
4.  Displaying this information in a structured format using a pandas DataFrame.

The script utilizes the `ccxt` library for interacting with exchange APIs and `pandas` for data manipulation and display.

## Setup and Execution

To use this script, follow these steps:

1.  **Navigate to the strategy directory:**
    ```bash
    cd path/to/your/project/strategy
    ```

2.  **Install dependencies:**
    Ensure you have Python and pip installed. Then, install the required libraries using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the script:**
    Execute the script from the `project/strategy/` directory:
    ```bash
    python arbitrage_discovery.py
    ```
    The script will then attempt to fetch the data and print the analysis.

## Important Note on API Access

Successful execution of this script depends on uninterrupted network access to the Binance and Bybit APIs. Users in geographically restricted regions, or those operating under network conditions that prevent access to these exchanges, might encounter errors.

For instance, a `ccxt.NetworkError` with a message like "Service unavailable from a restricted location" (as has been observed with Binance from certain environments) indicates that the exchange's API is not accessible. If you encounter such issues, please ensure your environment has the necessary permissions and network configuration to reach these services.

---

## Binance Real-Time Market Data Feed

### Description

The `binance_websocket_feed.py` script establishes a persistent connection to the Binance USDT-M Futures WebSocket API. It is designed to stream and display real-time market data.

Key functionalities include:
*   Connecting to `wss://fstream.binance.com/ws`.
*   Subscribing to the following public market data streams for `BTCUSDT`:
    *   `btcusdt@aggTrade`: For real-time aggregated trade information (price, quantity, timestamp).
    *   `btcusdt@depth`: For real-time updates to the order book (best bid/ask and changes in depth).
*   Printing all incoming JSON messages directly to the console.
*   Implementing a keep-alive mechanism by sending periodic pings to the server to maintain the connection.
*   Featuring automatic reconnection capabilities in case of connection drops or errors.

### Dependencies

*   The script requires the `websockets` Python library. This dependency is included in the `requirements.txt` file.

### How to Run

1.  **Navigate to the strategy directory:**
    ```bash
    cd path/to/your/project/strategy
    ```
2.  **Ensure dependencies are installed:**
    If you haven't already, install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Execute the script:**
    ```bash
    python binance_websocket_feed.py
    ```
    The script will run continuously, printing live market data to your terminal. To stop the script, press `Ctrl+C`.

### Purpose / Use Case

This script serves as a foundational component for obtaining real-time market data from Binance Futures. Its primary purposes are:

*   **Live Data Observation:** Allows developers and analysts to directly observe the flow of trade and order book data for `BTCUSDT`.
*   **Development Base:** Can be used as a starting point or integrated into more complex data processing systems, trading bots, or analytical tools that require a live feed from Binance.
*   **Strategy Prototyping:** Provides the raw data necessary for developing and testing real-time trading strategies.
