from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

import constants
import os

import market.astroport.factory as factory
from objects.asset import Asset

home = os.environ['HOME']

mnemonic = open(home + "/mk.txt").readline()

CLUSTER_ADDRESS = "terra1ae33wpqqymjyrgjc4fexzz4msl7qwclmvxzrvy"

mk = MnemonicKey(mnemonic)  # TODO: safer mnemonic handling
terra = LCDClient(chain_id=constants.network_info[constants.net]['moniker'],
                  url=constants.network_info[constants.net]['url'])
wallet = terra.wallet(mk)

a = Asset(contract_addr="terra1046n0fx3yc7l8vxeztzkvrchezmqf4ah2x2zc3", amount=0)
b = Asset(denom="uusd", amount=0)

q = factory.query_pair(terra, a, b)
print(q)
