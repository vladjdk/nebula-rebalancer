import constants
from terra_sdk.client.lcd import LCDClient

CONTRACT_ADDRESS = constants.nebula_contracts[constants.net]["nebula_cluster_factory"]

# queries
def query_config(client: LCDClient):
    return client.wasm.contract_query(
        CONTRACT_ADDRESS,
        {
            "config": {}
        }
    )


def query_cluster_exists(client: LCDClient, cluster_address):
    return client.wasm.contract_query(
        CONTRACT_ADDRESS,
        {
            "cluster_exists": cluster_address
        }
    )


def query_cluster_list(client: LCDClient):
    return client.wasm.contract_query(
        CONTRACT_ADDRESS,
        {
            "cluster_list": {}
        }
    )


def query_distribution_info(client: LCDClient):
    return client.wasm.contract_query(
        CONTRACT_ADDRESS,
        {
            "distribution_info": {}
        }
    )


# executions
