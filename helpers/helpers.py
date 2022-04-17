import time

import numpy as np
from terra_sdk.client.lcd import LCDClient, Wallet
from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core import AccAddress, Coin
from terra_sdk.core.market import MsgSwap

import constants
from market.astroport import factory as astro_factory, pair as pair
from market.market import market_swap
from nebula import cluster as cluster
from objects.asset import Asset


def get_info_from_state(client, cluster_address):
    state = cluster.query_cluster_state(client, cluster_address)
    inventory = state['inv']
    target = state['target']
    prices = state['prices']
    underlying_assets = [
        asset['info']['native_token']['denom'] if "native_token" in asset['info'].keys() else asset['info']['token'][
            'contract_addr'] for asset in state['target']]
    outstanding_balance_tokens = state['outstanding_balance_tokens']

    i = np.array(inventory, dtype=int)
    w = np.array([asset['amount'] for asset in target], dtype=int)
    p = np.array(prices, dtype=float)

    return i, w, p, outstanding_balance_tokens, underlying_assets


def get_ust_pairs_for_assets(terra: LCDClient, assets: [str]):
    pairs = []
    for i in range(len(assets)):
        if assets[i] == "uusd":
            pairs.append("uusd")
        elif assets[i].startswith("u"):
            pairs.append(assets[i])
        else:
            pairs.append(
                astro_factory.query_pair(terra, Asset(denom="uusd"), Asset(contract_addr=assets[i]))['contract_addr'])
    return pairs


def get_sorted_assets(capital, imbalances, cluster_assets):
    sorted_assets = []
    asset_spend = []
    while capital > 0 and len(imbalances) != 0:
        ranks = np.argsort(np.argsort(np.negative(imbalances)))
        top_ranked_dollar_value = imbalances[np.argmin(ranks)]/1000000
        if top_ranked_dollar_value == 0:
            break
        sorted_assets.append(str(cluster_assets[np.argmin(ranks)]))
        imbalances = np.delete(imbalances, np.argmin(ranks))
        cluster_assets = np.delete(cluster_assets, np.argmin(ranks))

        if int(capital*1000000) == 0 or int(top_ranked_dollar_value*1000000) == 0:
            # TODO: if spending this money returns 0 in astroport, remove it from the assets to buy
            sorted_assets.pop()
            return sorted_assets, asset_spend
        if top_ranked_dollar_value <= capital:
            asset_spend.append(int(top_ranked_dollar_value*1000000))
            capital -= top_ranked_dollar_value
        else:
            asset_spend.append(int(capital*1000000))
            capital = 0
    return sorted_assets, asset_spend


def swap_ust_for_assets(terra: LCDClient, wallet: Wallet, pairs, asset_spend, sorted_assets):
    acquired_assets = []
    for i in range(len(pairs)):
        if pairs[i].startswith("terra"):
            res = pair.execute_swap(terra, wallet, pairs[i], Asset(denom="uusd", amount=asset_spend[i]),
                                    0.005)
            time.sleep(7)
            acquired_assets.append(Asset(contract_addr=sorted_assets[i],
                                      amount=res.logs[0].events_by_type['from_contract']['return_amount'][0]) if
                                sorted_assets[i].startswith("terra1") else Asset(denom=sorted_assets[i], amount=
            res.logs[0].events_by_type['from_contract']['return_amount'][0]))
        elif pairs[i] == "uusd":
            acquired_assets.append(Asset(denom="uusd", amount=asset_spend[i]))
        elif pairs[i].startswith("u"):
            res = market_swap(terra, wallet, offer_denom="uusd", offer_amount=asset_spend[i], ask_denom=pairs[i])
            acquired_assets.append(Asset(denom=pairs[i], amount=res.logs[0].events_by_type['coin_received']['amount'][2][:res.logs[0].events_by_type['coin_received']['amount'][2].find("u")]))
    return acquired_assets


def split_imbalances(imbalances):
    positive_imbalances = np.array([abs(imbalance) if imbalance > 0 else 0 for imbalance in imbalances])
    negative_imbalances = np.array([imbalance if imbalance < 0 else 0 for imbalance in imbalances])

    return positive_imbalances, negative_imbalances


def sell_assets_from_redeem(terra: LCDClient, wallet: Wallet, redeem_res):
    actions = redeem_res.logs[len(redeem_res.logs) - 1].events_by_type['from_contract']['action'] if 'from_contract' in \
                                                                                                     redeem_res.logs[
                                                                                                         len(redeem_res.logs) - 1].events_by_type.keys() else []
    contract_addresses = redeem_res.logs[len(redeem_res.logs) - 1].events_by_type['from_contract'][
        'contract_address'] if 'from_contract' in redeem_res.logs[
        len(redeem_res.logs) - 1].events_by_type.keys() else []
    native_token_res = redeem_res.logs[len(redeem_res.logs) - 1].events_by_type['coin_spent'][
        'amount'] if 'coin_spent' in redeem_res.logs[len(redeem_res.logs) - 1].events_by_type.keys() else []
    token_addresses = []
    tokens = []
    for i in range(len(actions)):
        if actions[i] == "transfer":
            token_addresses.append(contract_addresses[i])
    token_amounts = redeem_res.logs[len(redeem_res.logs) - 1].events_by_type['from_contract'][
        'amount'] if 'from_contract' in redeem_res.logs[len(redeem_res.logs) - 1].events_by_type.keys() else []
    for i in range(len(token_addresses)):
        tokens.append(Asset(contract_addr=token_addresses[i], amount=int(token_amounts[i])))
    for i in range(len(native_token_res)):
        tokens.append(Asset(denom=native_token_res[i][native_token_res[i].find("u"):],
                            amount=int(native_token_res[i][:native_token_res[i].find("u")])))
    print("Redeemed assets: {}".format(tokens))
    print("Selling assets for UST.")
    totals = 0
    for token in tokens:
        if token.denom == "uusd":
            totals += token.amount
        else:
            q = astro_factory.query_pair(terra, Asset(denom="uusd"), token)
            redeem_res = pair.execute_swap(terra, wallet, q['contract_addr'], token, 0.005)
            time.sleep(6)
            totals += int(redeem_res.logs[len(redeem_res.logs) - 1].events_by_type['coin_received']['amount'][0][
                          :redeem_res.logs[len(redeem_res.logs) - 1].events_by_type['coin_received']['amount'][0].find(
                              "u")])
    totals = float(totals / 1000000)
    return totals