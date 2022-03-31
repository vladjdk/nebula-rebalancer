from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core import Coin, Coins
from terra_sdk.core.wasm import MsgExecuteContract

import constants
from terra_sdk.client.lcd import LCDClient, Wallet


# queries
from objects.asset import Asset


def query_config(client: LCDClient, cluster_address):
    return client.wasm.contract_query(
        cluster_address,
        {
            "config": {}
        }
    )


def query_target(client: LCDClient, cluster_address):
    return client.wasm.contract_query(
        cluster_address,
        {
            "target": {}
        }
    )


def query_cluster_state(client: LCDClient, cluster_address):
    return client.wasm.contract_query(
        cluster_address,
        {
            "cluster_state": {}
        }
    )


def query_cluster_info(client: LCDClient, cluster_address):
    return client.wasm.contract_query(
        cluster_address,
        {
            "cluster_info": {}
        }
    )


# execute
def execute_rebalance_create(client: LCDClient, wallet: Wallet, cluster_address, asset_amounts: [Asset], min_tokens=None):
    rebalance_create_msg = {
            "rebalance_create": {
                "asset_amounts": [asset.get_dict() for asset in asset_amounts],
                "min_tokens": str(min_tokens)
            }
        } if min_tokens else {
            "rebalance_create": {
                "asset_amounts": [asset.get_dict() for asset in asset_amounts],
            }
        }

    msgs = [
        MsgExecuteContract(
            wallet.key.acc_address,
            asset.contract_addr,
            {
                "increase_allowance": {
                    "amount": str(asset.amount),
                    "spender": cluster_address
                }
            }
        ) for asset in asset_amounts if asset.contract_addr
    ]

    msgs.append(MsgExecuteContract(
        wallet.key.acc_address,
        cluster_address,
        rebalance_create_msg,
        Coins([Coin(asset.denom, asset.amount) for asset in asset_amounts if asset.denom is not None])
    ))
    tx = wallet.create_and_sign_tx(
        options=CreateTxOptions(
            msgs=msgs,
            gas_prices=constants.gas['gas_prices'],
            gas_adjustment=constants.gas['gas_adjustment']
        )
    )
    return client.tx.broadcast(tx)


def execute_rebalance_redeem(client: LCDClient, wallet: Wallet, cluster_address, max_tokens, asset_amounts: [Asset]=None):
    cluster_token = query_config(client, cluster_address)['config']['cluster_token']
    rebalance_msg = {
                "rebalance_redeem": {
                    "max_tokens": str(max_tokens),
                    "asset_amounts": [asset.get_dict() for asset in
                                      asset_amounts]
                }
            } if asset_amounts else {
                "rebalance_redeem": {
                    "max_tokens": str(max_tokens),
                }
            }
    msgs = [
        MsgExecuteContract(
            wallet.key.acc_address,
            cluster_token,
            {
                "increase_allowance": {
                    "amount": str(max_tokens),
                    "spender": cluster_address
                }
            }
        ),
        MsgExecuteContract(
            wallet.key.acc_address,
            cluster_address,
            rebalance_msg
        )
    ]
    tx = wallet.create_and_sign_tx(
        options=CreateTxOptions(
            msgs=msgs,
            gas_prices=constants.gas['gas_prices'],
            gas_adjustment=constants.gas['gas_adjustment']
        )
    )
    return client.tx.broadcast(tx)



