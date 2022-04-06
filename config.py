import os

net = 'testnet'
cluster = 'lunaust'
# mnemonic = "MNEMONIC"

total_capital = 1000
imbalance_threshold = 2000000

home = os.environ['HOME']
mnemonic = open(home + "/mk.txt").readline()

