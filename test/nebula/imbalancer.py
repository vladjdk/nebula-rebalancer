import math
import os
import time

from terra_sdk.client.lcd import LCDClient, Wallet
from terra_sdk.key.mnemonic import MnemonicKey

import constants
import nebula.cluster as cluster
import nebula.factory as cluster_factory
import market.astroport.factory as astro_factory
import market.astroport.pair as pair

import numpy as np

from objects.asset import Asset

cluster_address = constants.cluster_contracts['testnet']['terraform']

home = os.environ['HOME']

mnemonic = open(home + "/mk.txt").readline()
mk = MnemonicKey(mnemonic)  # TODO: safer mnemonic handling

terra = LCDClient(chain_id=constants.network_info[constants.net]['moniker'],
                  url=constants.network_info[constants.net]['url'])
wallet = terra.wallet(mk)

state = (cluster.query_cluster_state(terra, "terra1ae33wpqqymjyrgjc4fexzz4msl7qwclmvxzrvy"))

inventory = state['inv']
target = state['target']
prices = state['prices']
underlying_assets = [
    asset['info']['native_token']['denom'] if "native_token" in asset['info'].keys() else asset['info']['token'][
        'contract_addr'] for asset in state['target']]
outstanding_balance_tokens = state['outstanding_balance_tokens']

assets_to_inject = [Asset(denom=asset, amount=10000000) if asset.startswith("u") else Asset(contract_addr=asset, amount=10000000) for asset in underlying_assets]

cluster.execute_rebalance_create(terra, wallet, cluster_address, assets_to_inject)