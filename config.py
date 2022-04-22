import os

import constants

from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey
from dotenv import load_dotenv

load_dotenv()

EOD_API = os.getenv("ALPHADEFI_1")


net = 'testnet'
cluster = 'lunaust'
# mnemonic = "MNEMONIC"

total_capital = 10000
imbalance_threshold = 2000000

# home = os.environ['HOME']
# mnemonic = open(home + "/mk.txt").readline()
mnemonic = os.getenv("ALPHADEFI_1")

mk = MnemonicKey(mnemonic)

terra = LCDClient(chain_id=constants.network_info[net]['moniker'],
                  url=constants.network_info[net]['url'])
wallet = terra.wallet(mk)

