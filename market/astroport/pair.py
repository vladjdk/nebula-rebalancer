import base64
import json

from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core import Coins, Coin
from terra_sdk.core.wasm import MsgExecuteContract

import constants
from terra_sdk.client.lcd import LCDClient, Wallet


# queries
from objects.asset import Asset


def query_pair(client: LCDClient, pair_address):
    return client.wasm.contract_query(
        pair_address,
        {
            "pair": {}
        }
    )


def query_pool(client: LCDClient, pair_address):
    return client.wasm.contract_query(
        pair_address,
        {
            "pool": {}
        }
    )


def query_config(client: LCDClient, pair_address):
    return client.wasm.contract_query(
        pair_address,
        {
            "config": {}
        }
    )


def query_share(client: LCDClient, pair_address, amount: int):
    return client.wasm.contract_query(
        pair_address,
        {
            "share": {
                "amount": str(amount)
            }
        }
    )


def query_simulation(client: LCDClient, pair_address, offer_asset: Asset):
    return client.wasm.contract_query(
        pair_address,
        {
            "simulation": {
                "offer_asset": offer_asset.get_dict()
            }
        }
    )


def query_reverse_simulation(client: LCDClient, pair_address, ask_asset: Asset):
    return client.wasm.contract_query(
        pair_address,
        {
            "reverse_simulation": {
                "ask_asset": ask_asset.get_dict()
            }
        }
    )


def query_cumulative_prices(client: LCDClient, pair_address):
    return client.wasm.contract_query(
        pair_address,
        {
            "cumulative_prices": {}
        }
    )


def execute_swap(client: LCDClient, wallet: Wallet, pair_address, offer_asset: Asset, max_spread):
    swap_msg = {
        "send": {
            "amount": str(offer_asset.amount),
            "contract": pair_address,
            "msg": base64.b64encode(json.dumps(
                {
                    "swap": {
                        "max_spread": str(max_spread),
                        "belief_price": str(offer_asset.amount/int(query_simulation(client, pair_address, offer_asset)['return_amount']))
                    }
                }
            ).encode('utf-8')).decode('ascii')
        }
    } if offer_asset.contract_addr else {
        "swap": {
            "belief_price": str(offer_asset.amount/int(query_simulation(client, pair_address, offer_asset)['return_amount'])),
            "max_spread": str(max_spread),
            "offer_asset": offer_asset.get_dict()
        }
    }
    msgs = [
        MsgExecuteContract(
            wallet.key.acc_address,
            pair_address if offer_asset.denom else offer_asset.contract_addr,
            swap_msg,
            Coins([Coin(denom=offer_asset.denom, amount=offer_asset.amount)] if offer_asset.denom else None)
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
