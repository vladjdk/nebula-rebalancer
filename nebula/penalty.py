from terra_sdk.client.lcd import LCDClient, Wallet


def query_params(client: LCDClient, penalty_address):
    return client.wasm.contract_query(
        penalty_address,
        {
            "params": {}
        }
    )


def query_create(client: LCDClient, penalty_address, block_height: int, cluster_token_supply: int, inventory: list([int]),
                 create_asset_amounts:list([int]), asset_prices: list([int]), target_weights: list([int])):
    return client.wasm.contract_query(
        penalty_address,
        {
            "penalty_query_create": {
                "block_height": block_height,
                "cluster_token_supply": str(cluster_token_supply),
                "inventory": [str(i) for i in inventory],
                "create_asset_amounts": [str(amount) for amount in create_asset_amounts],
                "asset_prices": [str(price) for price in asset_prices],
                "target_weights": [str(weight) for weight in target_weights]
            }
        }
    )


def query_redeem(client: LCDClient, penalty_address, block_height: int, cluster_token_supply: int, inventory: list([int]),
                 max_tokens: int, redeem_asset_amounts: list([int]), asset_prices: list([int]), target_weights: list([int])):
    return client.wasm.contract_query(
        penalty_address,
        {
            "penalty_query_redeem": {
                "block_height": block_height,
                "cluster_token_supply": str(cluster_token_supply),
                "inventory": [str(i) for i in inventory],
                "max_tokens": [str(max_tokens)],
                "redeem_asset_amounts": [str(amount) for amount in redeem_asset_amounts],
                "asset_prices": [str(price) for price in asset_prices],
                "target_weights": [str(weight) for weight in target_weights]
            }
        }
    )
