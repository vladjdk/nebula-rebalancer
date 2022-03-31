from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core import Coins, Coin
from terra_sdk.core.wasm import MsgExecuteContract

import nebula.cluster as cluster

import constants
from terra_sdk.client.lcd import LCDClient, Wallet

from objects.asset import Asset

CONTRACT_ADDRESS = constants.nebula_contracts[constants.net]["nebula_incentives"]


# queries
def query_config(client: LCDClient):
    return client.wasm.contract_query(
        CONTRACT_ADDRESS,
        {
            "config": {}
        }
    )


def query_penalty_period(client: LCDClient):
    return client.wasm.contract_query(
        CONTRACT_ADDRESS,
        {
            "penalty_period": {}
        }
    )


def query_pool_info(client: LCDClient, pool_type, cluster_address, n=None):
    return client.wasm.contract_query(
        CONTRACT_ADDRESS,
        {
            "pool_info": {
                "pool_type": pool_type,
                "cluster_address": cluster_address,
                "n": n
            }
        }
    )


def query_current_contributor_info(client: LCDClient, pool_type, contributor_address, cluster_address):
    return client.wasm.contract_query(
        CONTRACT_ADDRESS,
        {
            "current_contributor_info": {
                "pool_type": pool_type,
                "contributor_address": contributor_address,
                "cluster_address": cluster_address
            }
        }
    )


def query_contributor_pending_rewards(client: LCDClient, contributor_address):
    return client.wasm.contract_query(
        CONTRACT_ADDRESS,
        {
            "current_contributor_info": {
                "contributor_address": contributor_address
            }
        }
    )


# execute
# TODO: might want to add check to see if assets are a part of the cluster and cancel if not
def execute_arb_cluster_mint(client: LCDClient, wallet: Wallet, cluster_contract, assets: [Asset], min_ust=None):
    arb_cluster_create_msg = {
                "arb_cluster_create": {
                    "cluster_contract": cluster_contract,
                    "assets": [assets.get_dict() for assets in assets],
                    "min_ust": str(min_ust)
                }
            } if min_ust else {
                "arb_cluster_create": {
                    "cluster_contract": cluster_contract,
                    "assets": [assets.get_dict() for assets in assets],
                }
            }
    msgs = [
        MsgExecuteContract(
            wallet.key.acc_address,
            asset.contract_addr,
            {
                "increase_allowance": {
                    "amount": str(asset.amount),
                    "spender": CONTRACT_ADDRESS
                }
            }
        ) for asset in assets if asset.contract_addr
    ]
    msgs.append(
        MsgExecuteContract(
            wallet.key.acc_address,
            CONTRACT_ADDRESS,
            arb_cluster_create_msg,
            Coins([Coin(asset.denom, asset.amount) for asset in assets if asset.denom is not None])
        )
    )
    tx = wallet.create_and_sign_tx(
        options=CreateTxOptions(
            msgs=msgs,
            gas_prices=constants.gas['gas_prices'],
            gas_adjustment=constants.gas['gas_adjustment']
        )
    )
    return client.tx.broadcast(tx)


def execute_arb_cluster_redeem(client: LCDClient, wallet: Wallet, cluster_contract, asset: Asset):
    if not asset.denom:
        raise Exception("Asset must be a native token.")
    msgs = [
        MsgExecuteContract(
            wallet.key.acc_address,
            CONTRACT_ADDRESS,
            {
                "arb_cluster_redeem": {
                    "cluster_contract": cluster_contract,
                    "asset": asset.get_dict(),
                }
            },
            Coins([Coin(asset.denom, asset.amount)])
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


def execute_incentives_create(client: LCDClient, wallet: Wallet, cluster_contract, asset_amounts: [Asset],
                              min_tokens=None):
    incentives_create_msg = {
                "incentives_create": {
                    "cluster_contract": cluster_contract,
                    "asset_amounts": [asset.get_dict() for asset in asset_amounts],
                    "min_tokens": str(min_tokens)
                }
            } if min_tokens else {
                "incentives_create": {
                    "cluster_contract": cluster_contract,
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
                    "spender": CONTRACT_ADDRESS
                }
            }
        ) for asset in asset_amounts if asset.contract_addr
    ]
    msgs.append(
        MsgExecuteContract(
            wallet.key.acc_address,
            CONTRACT_ADDRESS,
            incentives_create_msg,
            Coins([Coin(asset.denom, asset.amount) for asset in asset_amounts if asset.denom is not None])
        )
    )
    tx = wallet.create_and_sign_tx(
        options=CreateTxOptions(
            msgs=msgs,
            gas_prices=constants.gas['gas_prices'],
            gas_adjustment=constants.gas['gas_adjustment']
        )
    )

    return client.tx.broadcast(tx)


def execute_incentives_redeem(client: LCDClient, wallet: Wallet, cluster_contract, max_tokens,
                              asset_amounts: [Asset] = None):
    cluster_token = cluster.query_config(client, cluster_contract)['config']['cluster_token']
    incentives_redeem_msg = {
                "incentives_redeem": {
                    "cluster_contract": cluster_contract,
                    "max_tokens": str(max_tokens),
                    "assets_amount": [asset.get_dict() for asset in asset_amounts] if asset_amounts else []
                }
            } if asset_amounts else {
                "incentives_redeem": {
                    "cluster_contract": cluster_contract,
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
                    "spender": CONTRACT_ADDRESS
                }
            }
        ),
        MsgExecuteContract(
            wallet.key.acc_address,
            CONTRACT_ADDRESS,
            incentives_redeem_msg,
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
