from terra_sdk.client.lcd import LCDClient

import constants
from objects.asset import Asset


FACTORY_ADDRESS = constants.market_contracts['astroport_factory']

def query_pair(client: LCDClient, a: Asset, b: Asset):
    msg = {
            "pair": {
                "asset_infos": [
                    {
                        "token": {
                            "contract_addr": a.contract_addr
                        }
                    } if a.contract_addr else {
                        "native_token": {
                            "denom": a.denom
                        }
                    },
                    {
                        "token": {
                            "contract_addr": b.contract_addr
                        }
                    } if b.contract_addr else {
                        "native_token": {
                            "denom": b.denom
                        }
                    }
                ]
            }
        }

    return client.wasm.contract_query(
        FACTORY_ADDRESS,
        msg
    )