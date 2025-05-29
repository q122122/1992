import asyncio
import random
import time
import collections

# Attempt to import OrderBookUpdate from the specified path
# This structure assumes the script is run in an environment where 'project' is a recognizable package
# or the PYTHONPATH is set up accordingly. For direct execution within 'project/strategy/',
# a relative import might be more robust if 'project' itself isn't a package root recognized by Python.
try:
    from project.strategy.common_data_structures import OrderBookUpdate
except ImportError:
    # Fallback for direct execution or if 'project' is not in sys.path
    # This makes the script more portable for different execution contexts.
    from common_data_structures import OrderBookUpdate

# --- Configuration ---
SIMULATION_ITERATIONS = 50  # Number of updates each simulated feed will generate
ARBITRAGE_CALCULATION_ITERATIONS = 45 # Number of times arbitrage logic will run
ARBITRAGE_THRESHOLD = 0.0 # Minimum spread to report as an opportunity

# --- Data Storage ---
# Stores the latest OrderBookUpdate for each symbol from each exchange.
# Structure: latest_market_data[symbol][exchange_name] = OrderBookUpdate_instance
latest_market_data = collections.defaultdict(dict)

# --- Simulated Data Feed Functions ---
async def simulate_exchange_feed(exchange_name: str, 
                                 symbol: str, 
                                 market_data_store: collections.defaultdict, 
                                 base_price: float, 
                                 volatility: float,
                                 iterations: int = SIMULATION_ITERATIONS):
    """
    Simulates a real-time market data feed from a single exchange.
    Generates random bid/ask prices and stores them as OrderBookUpdate instances.
    """
    print(f"[{exchange_name}] Starting simulated feed for {symbol} around base price {base_price:.2f}")
    for i in range(iterations):
        # Generate a new mid_price based on base_price and volatility
        mid_price = base_price + random.uniform(-volatility, volatility)
        
        # Ensure bid is slightly lower and ask is slightly higher than mid_price
        # and ask is always greater than bid.
        spread_percentage = random.uniform(0.0005, 0.0015) # 0.05% to 0.15% spread
        bid_price = mid_price * (1 - spread_percentage)
        ask_price = mid_price * (1 + spread_percentage)

        if bid_price >= ask_price: # Ensure ask is always higher
            ask_price = bid_price + (base_price * 0.0001) # Add a small fixed amount if they cross or are equal

        # Create an OrderBookUpdate instance
        update = OrderBookUpdate(exchange_name=exchange_name,
                                 symbol=symbol,
                                 best_bid=round(bid_price, 2),
                                 best_ask=round(ask_price, 2),
                                 timestamp=time.time())

        # Store this update in the market_data_store
        market_data_store[symbol][exchange_name] = update

        print(f"[SIM FEED - {exchange_name}] {i+1}/{iterations} | {symbol}: Bid={update.best_bid:.2f}, Ask={update.best_ask:.2f}")
        
        # Wait for a short random interval
        await asyncio.sleep(random.uniform(0.5, 2.0))
    print(f"[{exchange_name}] Finished simulated feed for {symbol}")


# --- Arbitrage Calculation Function ---
async def calculate_arbitrage_opportunities(market_data_store: collections.defaultdict, 
                                          symbol: str, 
                                          exchanges_to_compare: list,
                                          iterations: int = ARBITRAGE_CALCULATION_ITERATIONS):
    """
    Calculates and prints arbitrage opportunities for a given symbol
    between a list of exchanges using data from the market_data_store.
    """
    if len(exchanges_to_compare) < 2:
        print("[ARBITRAGE CALC] Needs at least two exchanges to compare.")
        return

    print(f"[ARBITRAGE CALC] Starting arbitrage calculation for {symbol} between {', '.join(exchanges_to_compare)}")
    
    for i in range(iterations):
        all_data_available = True
        current_updates = {}

        for ex_name in exchanges_to_compare:
            if ex_name in market_data_store[symbol]:
                current_updates[ex_name] = market_data_store[symbol][ex_name]
            else:
                all_data_available = False
                # print(f"[ARBITRAGE CALC] Data for {symbol} on {ex_name} not yet available.")
                break
        
        if not all_data_available or len(current_updates) < len(exchanges_to_compare):
            # print(f"[ARBITRAGE CALC] Waiting for data from all specified exchanges for {symbol}...")
            await asyncio.sleep(1.5) # Wait a bit longer if data is missing
            continue

        # For simplicity, let's assume we are comparing the first two exchanges in the list
        ex_A_name = exchanges_to_compare[0]
        ex_B_name = exchanges_to_compare[1]

        update_A = current_updates[ex_A_name]
        update_B = current_updates[ex_B_name]

        # Opportunity 1: Buy on Exchange A (ask_A), Sell on Exchange B (bid_B)
        # Profit if bid_B > ask_A
        ask_A = update_A.best_ask
        bid_B = update_B.best_bid
        spread_1 = bid_B - ask_A

        if spread_1 > ARBITRAGE_THRESHOLD:
            print(f"[ARBITRAGE FOUND! Iter {i+1}] {symbol}: Buy {ex_A_name} ({ask_A:.2f}), Sell {ex_B_name} ({bid_B:.2f}) -> Spread: {spread_1:.2f}")

        # Opportunity 2: Buy on Exchange B (ask_B), Sell on Exchange A (bid_A)
        # Profit if bid_A > ask_B
        ask_B = update_B.best_ask
        bid_A = update_A.best_bid
        spread_2 = bid_A - ask_B

        if spread_2 > ARBITRAGE_THRESHOLD:
            print(f"[ARBITRAGE FOUND! Iter {i+1}] {symbol}: Buy {ex_B_name} ({ask_B:.2f}), Sell {ex_A_name} ({bid_A:.2f}) -> Spread: {spread_2:.2f}")
        
        if spread_1 <= ARBITRAGE_THRESHOLD and spread_2 <= ARBITRAGE_THRESHOLD:
            print(f"[ARBITRAGE CALC Iter {i+1}] No significant arbitrage for {symbol} (A:{ask_A:.2f}/{bid_A:.2f}, B:{ask_B:.2f}/{bid_B:.2f})")

        # Wait for a short interval before the next calculation
        # This should generally be less frequent than data updates to work with recent data.
        await asyncio.sleep(1.0) 
    print(f"[ARBITRAGE CALC] Finished arbitrage calculation for {symbol}")

# --- Main Execution Logic ---
async def main():
    """
    Sets up and runs the simulated exchange feeds and arbitrage calculation.
    """
    target_symbol = "BTC/USDT"
    
    # Define exchanges and their simulated base prices
    # Slightly different base prices to make arbitrage opportunities more likely in simulation
    exchanges_config = {
        "Binance": {"base_price": 60000.00, "volatility": 50.0},
        "Bybit":   {"base_price": 60050.00, "volatility": 55.0}
    }
    
    exchange_names = list(exchanges_config.keys())

    tasks = []

    # Create and schedule tasks for simulated exchange feeds
    for ex_name, config in exchanges_config.items():
        task = asyncio.create_task(
            simulate_exchange_feed(exchange_name=ex_name,
                                   symbol=target_symbol,
                                   market_data_store=latest_market_data,
                                   base_price=config["base_price"],
                                   volatility=config["volatility"])
        )
        tasks.append(task)

    # Create and schedule a task for arbitrage calculation
    arbitrage_task = asyncio.create_task(
        calculate_arbitrage_opportunities(market_data_store=latest_market_data,
                                          symbol=target_symbol,
                                          exchanges_to_compare=exchange_names)
    )
    tasks.append(arbitrage_task)

    print(f"Starting main simulation with {SIMULATION_ITERATIONS} feed updates and {ARBITRAGE_CALCULATION_ITERATIONS} arbitrage checks.")
    # Run all tasks concurrently
    # Using asyncio.gather will run them until the one with fewest iterations completes
    # or all complete if they have the same number of iterations.
    await asyncio.gather(*tasks)
    print("All simulation tasks finished.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Multi-exchange arbitrage simulation stopped by user.")
    except Exception as e:
        print(f"An error occurred at the script level: {e}")
