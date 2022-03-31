# Rebalancing Bots

## Flow

For an arbitrary cluster:

- Assumes that the bot account has access to a certain amount of UST
- Calculates the current cluster imbalance
- Check if the rebalance flow will be profitable
- Rebalance flow
    - Two Options
        - Mints
            - Calculates the optimale `create` basket asset composition `asset amounts`
            - Use UST to buy `asset_amounts` off an AMM (can use the pool's `simulation` and `reverse_simulation` queries to get the expected returns amount)
            - Use the assets to mint cluster tokens using the cluster contract's `create` function
            - (Optional - Arbitrage Mint) Sell the cluster tokens on the AMM
        - Burns
            - Calculates the optimal asset tokens (`asset_amounts`) to redeem from cluster
            - Use UST to buy cluster off an AMM
            - Burn the cluster tokens to redeem `asset_amounts` assets from the cluster
            - (Optional - Arbitrage Burn) Sell the asset tokens on the AMM