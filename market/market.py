from terra_sdk.client.lcd import Wallet, LCDClient
from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core import AccAddress, Coin
from terra_sdk.core.market import MsgSwap

import constants


def market_swap(terra: LCDClient, wallet: Wallet, offer_denom, offer_amount, ask_denom):
    msg = MsgSwap(AccAddress(wallet.key.acc_address), Coin(denom=offer_denom, amount=offer_amount), ask_denom=ask_denom)
    tx = wallet.create_and_sign_tx(
        options=CreateTxOptions(
            msgs=[msg],
            gas_prices=constants.gas['gas_prices'],
            gas_adjustment=constants.gas['gas_adjustment']
        )
    )
    return terra.tx.broadcast(tx)