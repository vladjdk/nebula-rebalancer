from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

import constants
import os

import nebula.cluster as cluster
import nebula.incentives as incentives
from objects.asset import Asset

home = os.environ['HOME']

mnemonic = open(home + "/mk.txt").readline()

CLUSTER_ADDRESS = "terra1ae33wpqqymjyrgjc4fexzz4msl7qwclmvxzrvy"

mk = MnemonicKey(mnemonic)  # TODO: safer mnemonic handling
terra = LCDClient(chain_id=constants.network_info[constants.net]['moniker'],
                  url=constants.network_info[constants.net]['url'])
wallet = terra.wallet(mk)

config = cluster.query_config(terra, CLUSTER_ADDRESS)
target = cluster.query_target(terra, CLUSTER_ADDRESS)
cluster_state = cluster.query_cluster_state(terra, CLUSTER_ADDRESS)
cluster_info = cluster.query_cluster_info(terra, CLUSTER_ADDRESS)

assets = [
    Asset(denom="uluna", amount=10000000),
    Asset(denom="uusd", amount=10000000),
    Asset(contract_addr="terra10llyp6v3j3her8u3ce66ragytu45kcmd9asj3u", amount=100000),  # MIR
    Asset(contract_addr="terra1747mad58h0w4y589y3sk84r5efqdev9q4r02pc", amount=10000000),  # ANC
    Asset(contract_addr="terra1jqcw39c42mf7ngq4drgggakk3ymljgd3r5c3r5", amount=1000000),  # ASTRO
    Asset(contract_addr="terra1a8hskrwnccq0v7gq3n24nraaqt7yevzy005uf5", amount=100000000),  # VKR
    Asset(contract_addr="terra1lqm5tutr5xcw9d5vc4457exa3ghd4sr9mzwdex", amount=1000000),  # MINE
    Asset(contract_addr="terra1azu2frwn9a4l6gl5r39d0cuccs4h7xlu9gkmtd", amount=10000),  # KUJI
]


while True:
    test = incentives.execute_incentives_create(terra, wallet, CLUSTER_ADDRESS, assets, None)
    print(test)

    test2 = incentives.execute_incentives_redeem(terra, wallet, CLUSTER_ADDRESS, 1000000000, None)
    print(test2)
#
# test3 = incentives.execute_arb_cluster_mint(terra, wallet, CLUSTER_ADDRESS, assets, 10000000)
# print(test3)

# asset = Asset(denom="uusd", amount=10)
#
# test4 = incentives.execute_arb_cluster_redeem(terra, wallet, CLUSTER_ADDRESS, asset)
# print(test4)