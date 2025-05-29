# Cross-Exchange Perpetual Contract Arbitrage System

## Overview

This project aims to develop a system for identifying and potentially executing arbitrage opportunities in perpetual contracts across various cryptocurrency exchanges. The development of this system is guided by an internal development plan, with an initial and ongoing focus on **simulated trading** to ensure stability and validate strategies before any consideration of live market interaction.

The core idea is to leverage price discrepancies between the same perpetual contracts listed on different exchanges to generate potential profits.

## Modules / Components (High-Level)

The system architecture, as outlined in the development guide, is planned to include the following major components:

*   **Market Data Subscription:** To receive real-time market data (order books, trades) from multiple exchanges.
*   **Strategy Development:** For implementing and testing various arbitrage strategies. The `project/strategy/` directory currently houses an initial script, `arbitrage_discovery.py`, which focuses on identifying potential arbitrage between Binance and Bybit for BTC/USDT spot prices as a foundational step.
*   **Backend System:** To manage data processing, strategy execution logic, and communication between components.
*   **Frontend Interface:** For monitoring system status, viewing potential opportunities, and managing configurations.
*   **Execution Engine:** (For future consideration) To manage order placement and execution in a live trading environment, once strategies are thoroughly vetted via simulation.

## Current Status

The project is currently in the **initial development phase**.

The first component, a Python script named `arbitrage_discovery.py`, has been implemented within the `project/strategy/` directory. This script serves as a proof-of-concept for fetching order book data from Binance and Bybit and identifying basic arbitrage spreads.

Further development will focus on expanding the capabilities of existing components and building out the additional modules as per the development guide.

## Disclaimer

**Important:** This project is under development and is intended strictly for **simulation and educational purposes only**.

Trading cryptocurrencies, and arbitrage in particular, involves **significant financial risk**, including the potential loss of capital. This system, in its current or future state, should not be used for live trading without a comprehensive understanding of the risks involved, extensive testing in a simulated environment, and robust risk management practices.

No information or output from this project should be considered financial advice. Always do your own research and consult with a qualified financial advisor before making any investment decisions. The developers assume no liability for any financial losses incurred as a result of using or misusing this system.
