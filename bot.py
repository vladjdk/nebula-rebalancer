from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

import constants

from bots.rebalance import create_then_redeem
import config

mk = MnemonicKey(config.mnemonic)

terra = LCDClient(chain_id=constants.network_info[config.net]['moniker'],
                  url=constants.network_info[config.net]['url'])
wallet = terra.wallet(mk)
cluster_address = constants.cluster_contracts[config.net][config.cluster]

create_then_redeem(config.total_capital, cluster_address, config.imbalance_threshold)
