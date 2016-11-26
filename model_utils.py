# Functions which Brandon will implement
from __future__ import division
import math

blocks_per_period = 144
asic_recuperation_period = 240
block_reward = 12.5
recovery_cap_multiplier = 1.0 # float between [0, 1]
default_btc_to_usd_rate = 730 # current bitcoin rate

def compute_lower_bound(btc_f_stolen):
    percent_stolen = btc_f_stolen*100
    # 2-degree polynomial fit to data (4%, 60%), (0.75%, 80%)
    percent_new_worth = -1.531*math.pow(percent_stolen, 2) + 1.116*percent_stolen + 80.02
    lower_bound = max((percent_new_worth/100.0) * default_btc_to_usd_rate, 0.0)
    return lower_bound

def btc_to_usd_exchange_rate(time, btc_f_stolen):
    # Attack time, if applicable, is 0
    # This function is modeled after tanh.
    # After an attack the btc-to-usd rate drops dramatically.
    # Assuming no further attacks, the rate slowly recovers.
    # |   _ _ __
    # |  /
    # | /
    # |/
    # notice the free fall and then tanh(>=0)
    if btc_f_stolen == 0.0:
        return default_btc_to_usd_rate # assume rate is constant
    else:
        # Crude assumption: rate decreases according to polynomial fit to Brandon's data.
        lower_bound_rate = compute_lower_bound(btc_f_stolen)
        # Crude assumption: rate can __fully__ recover.
        upper_bound_rate = recovery_cap_multiplier * default_btc_to_usd_rate
        # Since attack time = 0, any time post attack is positive.
        # And so, second derivative of rate is negative.
        # This ranges from 0 to 1.
        # Modifying tanh to account for btc_f_stolen.
        # The higher the btc_f_stolen, the longer it takes to recover.
        tanh = math.tanh((1 - btc_f_stolen) * time)
        delta_rate = tanh * (upper_bound_rate - lower_bound_rate)
        new_btc_to_usd = lower_bound_rate + delta_rate
        return new_btc_to_usd

def mining_asic_sell_price(mining_power, btc_f_stolen, sell_machines_time,
                           discount_rate):
    effective_recuperation_periods = asic_recuperation_period
    if discount_rate < 1:
        effective_recuperation_periods = \
                (1 - discount_rate ** asic_recuperation_period) \
                / (1 - discount_rate)
    earnings_per_period = mining_power * block_reward * blocks_per_period * \
                          btc_to_usd_exchange_rate(sell_machines_time, btc_f_stolen)
    return earnings_per_period * effective_recuperation_periods
