import time

import numpy as np

from helpers.helpers import get_info_from_state, split_imbalances, get_sorted_assets, get_ust_pairs_for_assets, \
    swap_ust_for_assets, sell_assets_from_redeem
from helpers.math import calculate_notional_imbalance, calculate_separate_imbalances
from nebula import cluster as cluster, factory as cluster_factory
from objects.asset import Asset


def create_then_redeem(ust_used, cluster_address, imbalance_threshold):
    print("Total UST available for spending: {}".format(ust_used))
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