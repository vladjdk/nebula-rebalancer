# Rebalancing Bots

This bot is meant for rebalancing clusters on Terra's Nebula Protocol. **IT ONLY WORKS IF ALL THE ASSETS IN THE CLUSTER HAVE UST PAIRS ON ASTROPORT.**

## Current Markets:

- Astroport

## Flow

It works by looping through the following flow:

1. Find best assets to rebalance with available UST.
2. Swap UST for one asset at a time for the amount required to rebalance that particular asset.
   1. If the asset can be rebalanced completely, the bot swaps UST the next asset.
   2. If all assets can be rebalanced, the bot does not use up all the capital and proceeds to step 3.
3. Perform a Nebula CREATE operation with the swapped assets.
4. Calculate the optimal redeem rebalance assets.
5. Perform a Nebula REDEEM operation with the calculated optimal redeem rebalance assets.
6. Swap all redeemed assets to UST.
7. Repeat steps 1-6 until `imbalance_threshold` is hit.

## Disclaimer

- This code is unaudited and is not guaranteed to rebalance.
- This script does not guarantee profits and may result in a loss of funds.
- This script is not endorsed by Nebula Protocol and is a personal contribution.
- **USE THIS SCRIPT AT YOUR OWN RISK. I am not responsible for lost funds.**

By running this script, you agree to the above conditions.

With that being said, let's proceed to the setup!

## Setup
To install all dependencies, run `pip install -r requirements.txt`.

Next, open up the `config.py` file. It should resemble the following:
```python
import os

net = 'testnet'
cluster = 'terraform'
mnemonic = "MNEMONIC"

total_capital = 10
imbalance_threshold = 1000000

# home = os.environ['HOME']
# mnemonic = open(home + "/mk.txt").readline()
```

### Options:
#### Net

- `mainnet`: Uses Terra Mainnet (Nebula is not currently released on mainnet
- `testnet`: Uses the Terra Testnet (This is the recommended option for new users to test out the code)

#### Cluster

Mainnet Clusters Available:

- **Currently Unavailable**

Testnet Clusters Available:

- `mirancust`
- `first_three_cluster`
- `lunaust`

#### mnemonic

You can provide your mnemonic in any way that you wish, but ensure that the variable is populated with a string version of your mnemonic.

#### total_capital

Here, input the amount of UST that you would like to use in floating-point decimal numbers. Ensure that the numbers are a maximum of 6 decimals after the point.

For example:

- `6.1`: Correct
- `10`: Correct
- `10.123456`: Correct
- `10.1234567`: Incorrect

#### imbalance_threshold

Input the imbalance amount in `uust` for which the bot should stop. For example, setting it to `1000000` would mean the bot stops running after the imbalance reaches 1000000 or less.

## Running the Bot

After the [Config File](./config.py) has been filled out to the desired specifications, you can run the bot by running the following in the root directory:
```
python3 bot.py
```

## License

Contents of this repository are open source under [GNU General Public License v3](./LICENSE) or later.
