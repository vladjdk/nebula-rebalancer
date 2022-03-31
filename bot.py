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


def calculate_capital_allocation(i, p):
    return np.multiply(i, p)


def calculate_target_capital_allocation(i, w, p):
    return np.multiply(np.divide(np.multiply(w, p), np.dot(w, p)), np.dot(i, p))


def calculate_notional_imbalance(i, w, p):
    return np.sum(np.abs(np.subtract(calculate_target_capital_allocation(i, w, p), calculate_capital_allocation(i, p))))


# we could likely use this function to find out what the most impactful changes to make will be
def calculate_separate_imbalances(i, w, p):
    return np.subtract(calculate_target_capital_allocation(i, w, p), calculate_capital_allocation(i, p))


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


def get_ust_pairs_for_assets(assets: [Asset]):
    pairs = []
    for i in range(len(assets)):
        if assets[i] == "uusd":
            pairs.append(None)
        elif assets[i].startswith("u"):
            pairs.append(astro_factory.query_pair(terra, Asset(denom="uusd"), Asset(denom=assets[i]))['contract_addr'])
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


def swap_ust_for_assets(pairs, asset_spend, sorted_assets):
    acquired_assets = []
    for i in range(len(pairs)):
        if pairs[i]:
            res = pair.execute_swap(terra, wallet, pairs[i], Asset(denom="uusd", amount=asset_spend[i]),
                                    0.005)
            time.sleep(7)
            acquired_assets.append(Asset(contract_addr=sorted_assets[i],
                                      amount=res.logs[0].events_by_type['from_contract']['return_amount'][0]) if
                                sorted_assets[i].startswith("terra1") else Asset(denom=sorted_assets[i], amount=
            res.logs[0].events_by_type['from_contract']['return_amount'][0]))
        else:
            acquired_assets.append(Asset(denom="uusd", amount=asset_spend[i]))
    return acquired_assets


def split_imbalances(imbalances):
    positive_imbalances = np.array([abs(imbalance) if imbalance > 0 else 0 for imbalance in imbalances])
    negative_imbalances = np.array([imbalance if imbalance < 0 else 0 for imbalance in imbalances])

    return positive_imbalances, negative_imbalances

def sell_assets_from_redeem(redeem_res):
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


def create_then_redeem(ust_used, cluster_address, imbalance_threshold):
    print("Total UST available for spending: {}".format(total_capital))
    i_, w_, p_, outstanding_balance_tokens, cluster_assets = get_info_from_state(terra, cluster_address)
    x_ = calculate_notional_imbalance(i_, w_, p_)
    loops = 0
    while x_ > imbalance_threshold:
        print("Notional imbalance before rebalance: {}".format(x_))
        print("Need {} UST to fully rebalance.".format(x_/1000000))
        imbalances = calculate_separate_imbalances(i_, w_, p_)
        positive_imbalances, negative_imbalances = split_imbalances(imbalances)
        sorted_assets, spend_values = get_sorted_assets(ust_used, positive_imbalances, cluster_assets)
        print("Sorted assets by imbalance: {}".format(sorted_assets))
        print("Spend values by sorted asset: {}".format(spend_values))
        print("Total UST value to be spent: {}".format(sum(spend_values)/1000000))
        pairs = get_ust_pairs_for_assets(sorted_assets)
        print("Astroport pair for each sorted asset: {}".format(pairs))
        rebalance_create_assets = swap_ust_for_assets(pairs, spend_values, sorted_assets)
        print("Assets for create rebalance: {}".format(rebalance_create_assets))

        create_res = cluster.execute_rebalance_create(terra, wallet, cluster_address, rebalance_create_assets)
        time.sleep(7)
        tokens_received = create_res.logs[len(create_res.logs) - 1].events_by_type['from_contract'][
                                                   'mint_to_sender'][0]
        print("**Created!**")
        print("Amount of cluster tokens received from create: {}".format(tokens_received))

        inventory, weights, prices, outstanding_balance_tokens, cluster_assets = get_info_from_state(terra, cluster_address)
        positive_imbalances, negative_imbalances = split_imbalances(imbalances)

        spendable_capital = (float(int(tokens_received) / float(outstanding_balance_tokens) * np.dot(inventory, prices))*(1 - float(cluster_factory.query_config(terra)['protocol_fee_rate']))**2)/1000000 # the **2 is to
        print("Maximum UST value returnable from underlying assets: {}".format(spendable_capital))
        sorted_assets, spend_values = get_sorted_assets(spendable_capital, abs(negative_imbalances), cluster_assets)

        rebalance_redeem_assets = []
        for i in range(len(sorted_assets)):
            if sorted_assets[i].startswith("terra1"):
                rebalance_redeem_assets.append(Asset(contract_addr=sorted_assets[i], amount=int(spend_values[i]/(prices[np.where(np.array(cluster_assets)==sorted_assets[i])[0][0]]))))
            else:
                rebalance_redeem_assets.append(Asset(denom=sorted_assets[i], amount=int(spend_values[i]/(prices[np.where(np.array(cluster_assets)==sorted_assets[i])[0][0]]))))

        print("Assets to redeem: {}".format(rebalance_redeem_assets))

        redeem_res = cluster.execute_rebalance_redeem(terra, wallet, cluster_address,
                                               tokens_received, rebalance_redeem_assets)

        print("**Redeemed!**")

        totals = sell_assets_from_redeem(redeem_res)
        print("Total UST received: {}".format(totals))
        i_, w_, p_, _outstanding_balance_tokens, _cluster_assets = get_info_from_state(terra, cluster_address)
        x_ = calculate_notional_imbalance(i_, w_, p_)
        print("Notional imbalance after rebalance: {}".format(x_))
        loops += 1
        print("FINISHED {} REBALANCE LOOPS".format(loops))

    print("Notional imbalance ({}) is under threshold ({}). Finishing script".format(x_, imbalance_threshold))


home = os.environ['HOME']
mnemonic = open(home + "/mk.txt").readline()
mk = MnemonicKey(mnemonic)  # TODO: safer mnemonic handling

terra = LCDClient(chain_id=constants.network_info[constants.net]['moniker'],
                  url=constants.network_info[constants.net]['url'])
wallet = terra.wallet(mk)
cluster_address = constants.cluster_contracts['testnet']['terraform']

total_capital = 10
imbalance_threshold = 1000000

create_then_redeem(total_capital, cluster_address, imbalance_threshold)
