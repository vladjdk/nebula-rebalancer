from terra_sdk.client.lcd import LCDClient
import numpy as np

import helpers.helpers as helpers
import nebula.cluster as cluster
from objects.asset import Asset
import market.astroport.pair as pair
import nebula.factory as factory

from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

import constants

import config

def get_premiums(terra: LCDClient, clusters):
    cluster_infos = [helpers.get_info_from_state(terra, c) for c in clusters]
    # get info for each cluster
    cluster_infos = [{
        'i': c[0],
        'w': c[1],
        'p': c[2],
        'outstanding_balance_tokens': c[3],
        'underlying_assets': c[4]
    } for c in cluster_infos]

    cluster_token_addresses = [cluster.query_cluster_state(terra, c)['cluster_token'] for c in clusters]

    # calculate the intrinsic value
    intrinsic_values = [sum(np.array(c['i']) * np.array(c['p']))/float(c['outstanding_balance_tokens']) if float(c['outstanding_balance_tokens']) != 0 else 0 for c in cluster_infos]

    # get the token price from astroport
    astroport_pairs = helpers.get_ust_pairs_for_assets(terra, cluster_token_addresses)
    astroport_values = []
    for i in range(len(clusters)):
        if intrinsic_values[i] != 0:
            pool = pair.query_pool(terra, astroport_pairs[i])
            astroport_values.append(float(pool['assets'][0]['amount'])/float(pool['assets'][1]['amount']))
        else:
            astroport_values.append(0)
    premiums = []
    for i in range(len(intrinsic_values)):
        if astroport_values[i] == 0:
            premiums.append(0)
        else:
            premiums.append((astroport_values[i] - intrinsic_values[i]) / intrinsic_values[i])
    return [{
        "premium": premiums[i],
        "pair": astroport_pairs[i]
    } for i in range(len(astroport_pairs))]

mk = MnemonicKey(config.mnemonic)

terra = LCDClient(chain_id=constants.network_info[config.net]['moniker'],
                  url=constants.network_info[config.net]['url'])
wallet = terra.wallet(mk)
cluster_address = constants.cluster_contracts[config.net][config.cluster]

clusters = [c[0] for c in factory.query_cluster_list(terra)['contract_infos'] if c[1]]

print(clusters)
print(get_premiums(terra, clusters))

