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
