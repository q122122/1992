# Cross-Exchange Perpetual Contract Arbitrage System

## Overview

This project aims to develop a system for identifying and potentially executing arbitrage opportunities in perpetual contracts across various cryptocurrency exchanges. The development of this system is guided by an internal development plan, with an initial and ongoing focus on **simulated trading** to ensure stability and validate strategies before any consideration of live market interaction.

The core idea is to leverage price discrepancies between the same perpetual contracts listed on different exchanges to generate potential profits.

## Modules / Components (High-Level)

The system architecture, as outlined in the development guide, is planned to include the following major components:

*   **Market Data Subscription:** Individual WebSocket feed scripts have been developed to connect to and stream raw market data from several exchanges (Binance, OKX, Bybit, Bitget). The `binance_websocket_feed.py` and `okx_websocket_feed.py` scripts have been enhanced to support outputting data to a `multiprocessing.Queue` for integration with a central manager.
*   **Data Integration and Processing:** Conceptual work has commenced on a "Feed Manager" system. This system will be responsible for:
    *   Managing the execution of individual feed scripts as separate processes.
    *   Collecting raw data from these feeds via inter-process communication (queues).
    *   Parsing exchange-specific data formats and translating them into a standardized internal structure (e.g., `OrderBookUpdate`).
    An initial implementation, `live_feed_manager.py`, now handles this for the Binance and OKX feeds.
*   **Strategy Development:** For implementing and testing various arbitrage strategies. The `project/strategy/` directory currently houses:
    *   `arbitrage_discovery.py`: An initial script for identifying arbitrage from REST API order book data.
    *   `multi_exchange_arbitrage.py`: A script demonstrating arbitrage logic using simulated WebSocket data streams.
*   **Backend System:** (Future) To manage data processing, strategy execution logic, and communication between components. This will likely incorporate the Feed Manager.
*   **Frontend Interface:** (Future) For monitoring system status, viewing potential opportunities, and managing configurations.
*   **Execution Engine:** (Future consideration) To manage order placement and execution in a live trading environment, once strategies are thoroughly vetted via simulation.

## Current Status

The project is currently in the **initial development and conceptualization phase**. Key milestones achieved include:

*   **Individual WebSocket Feeds:** Standalone Python scripts for connecting to and streaming public market data (primarily tickers or order book snapshots) have been created for:
    *   Binance (`binance_websocket_feed.py` - *now supports `multiprocessing.Queue` output*)
    *   OKX (`okx_websocket_feed.py` - *now supports `multiprocessing.Queue` output*)
    *   Bybit (`bybit_websocket_feed.py`)
    *   Bitget (`bitget_websocket_feed.py`)
*   **Standardized Data Structure:** `project/strategy/common_data_structures.py` has been created, defining an `OrderBookUpdate` class. This class provides a common format for representing simplified order book data (best bid/ask, symbol, exchange, timestamp) internally.
*   **Simulated Arbitrage Logic:** `project/strategy/multi_exchange_arbitrage.py` has been developed. This script simulates multiple exchange data feeds and demonstrates the core logic for identifying arbitrage opportunities using the standardized `OrderBookUpdate` structure. It serves as a testbed for strategy mechanics.
*   **Feed Integration Planning:** `project/strategy/feed_manager_concept.py` has been written as a conceptual outline. This script details the proposed architecture for a "Feed Manager" that would use multiprocessing to run individual feed scripts, collect their data via queues, parse exchange-specific formats, and standardize it into `OrderBookUpdate` objects.
*   **Initial Live Feed Management:** `project/strategy/live_feed_manager.py` has been implemented and enhanced. This script now:
    *   Manages the `binance_websocket_feed.py` and `okx_websocket_feed.py` scripts as separate processes.
    *   Receives live data from both Binance and OKX feeds via a shared `multiprocessing.Queue`.
    *   Parses Binance's `aggTrade`/`depthUpdate` streams and OKX's `tickers` stream messages into the standardized `OrderBookUpdate` format.
    *   Stores and logs these standardized updates. This serves as a foundational step for a multi-feed system.
*   **Initial REST-based Arbitrage Script:** The `arbitrage_discovery.py` script was an early component for fetching order book data via REST APIs to find basic arbitrage spreads.

Further development will focus on extending `live_feed_manager.py` to support more exchanges (by updating their respective feed scripts for queue output and implementing parsers), refining data parsing logic, and then integrating this live, standardized data into the arbitrage calculation engine.

## Disclaimer

**Important:** This project is under development and is intended strictly for **simulation and educational purposes only**.

Trading cryptocurrencies, and arbitrage in particular, involves **significant financial risk**, including the potential loss of capital. This system, in its current or future state, should not be used for live trading without a comprehensive understanding of the risks involved, extensive testing in a simulated environment, and robust risk management practices.

No information or output from this project should be considered financial advice. Always do your own research and consult with a qualified financial advisor before making any investment decisions. The developers assume no liability for any financial losses incurred as a result of using or misusing this system.
