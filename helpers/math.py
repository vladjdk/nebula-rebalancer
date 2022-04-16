import numpy as np


def calculate_capital_allocation(i, p):
    return np.multiply(i, p)


def calculate_target_capital_allocation(i, w, p):
    return np.multiply(np.divide(np.multiply(w, p), np.dot(w, p)), np.dot(i, p))


def calculate_notional_imbalance(i, w, p):
    return np.sum(np.abs(np.subtract(calculate_target_capital_allocation(i, w, p), calculate_capital_allocation(i, p))))


def calculate_separate_imbalances(i, w, p):
    return np.subtract(calculate_target_capital_allocation(i, w, p), calculate_capital_allocation(i, p))