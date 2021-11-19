# -*- coding: utf-8 -*-
"""
Created on Tue June 11 10:56:03 2019

@author: Larkin
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt

def action_binner(v):
    # 4 categories of actions
    # Small undercut -1
    if v < 1.0 and v > 0.95:
        return "-1"
    # small premium +1
    if v > 1.0 and v < 1.05:
        return "+1"
    # medium undercut
    if v <= 0.95 and v > 0.7:
        return "-2"
    # medium premium
    if v >= 1.05 and v < 1.3:
        return "+2"
    # large undercut
    if v <= 0.7:
        return "-3"
    # medium premium
    if v >= 1.3:
        return "+3"
    return "+1"

def rev_binner(v):
    # small undercut +1
    if v == "-1":
        return np.random.uniform(0.95, 1.0, 1)[0]
    # small premium +1
    if v == "+1":
        return np.random.uniform(1.0, 1.05, 1)[0]
    # medium undercut
    if v == "-2":
        return np.random.uniform(0.7, 0.95, 1)[0]
    # medium premium
    if v == "+2":
        return np.random.uniform(1.05, 1.3, 1)[0]
    # large undercut
    if v == "-3":
        return np.random.uniform(0.7, 0.1, 1)[0]
    # medium premium
    if v == "+3":
        return np.random.uniform(1.3, 2.0, 1)[0]
    return np.random.uniform(0.75, 1.25, 1)[0]
    
def olig_mab_mechanism(mab_input, recent_market_price):
    mab_arr = np.asarray(mab_input)
    thetas = mab_arr[:, 0]
    list_thetas = [list(x) for x in list(thetas)]

    actions = [list([action_binner(x) for x in y]) for y in list_thetas]
    revenues = mab_arr[:, 1]

    # format the data
    oligo_arms = ["-1", "-1", "-1"]
    mean_reward_tracker = []
    std_reward_tracker = []
    for p in range(0, revenues.shape[1]):
        flat_actions = np.asarray(actions)[:, p]
        flat_revenues = revenues[:, p]
        action_reward_array = list(zip(flat_actions, flat_revenues))

        action_reward_df = pd.DataFrame(action_reward_array, columns=['action', 'reward'])
        mean_reward_dic = action_reward_df.groupby('action').mean().to_dict()['reward']
        st_dev_reward_dic = action_reward_df.groupby('action').std().to_dict()['reward']

        mean_reward_tracker.append(mean_reward_dic)
        std_reward_tracker.append(st_dev_reward_dic)

        # thompson sampling, simulate each arm using normal distribution
        arms = list(mean_reward_dic.keys())
        max_arm = arms[0]
        previous_random_max = 0.0
        for a in arms:
            arm_mean = mean_reward_dic[a]
            arm_std = st_dev_reward_dic[a]
            random_play = np.random.normal(arm_mean, arm_std, 1)[0]
            if np.isnan(random_play):
                random_play = arm_mean
            if random_play > previous_random_max:
                max_arm = a
        oligo_arms[p] = max_arm
    theta_values = [rev_binner(x) for x in oligo_arms]
    price_suggestion = [a*b for a,b in zip(theta_values, recent_market_price)]
    
    return price_suggestion

def p(prices_historical=None, demand_historical=None, information_dump=None):
    """
    This pricing algorithm would return the minimum price for the products
    used by any competitor in the last iteration if there are 2 competitors
    and it returns the mean price for the product
    used by any competitor in the last iteration if there are more than 2 competitors.
    In the first iteration it returns 3 random prices.
    
    input:
        prices_historical: numpy 3-dim array: (number competitors) x (number of products = 3) x (past iterations)
                           it contains the past prices of each competitor 
                           (you are at index 0) over the past iterations
        demand_historical: numpy 2-dim array: (number of products = 3) x (past iterations) 
                           it contains the history of your own past observed demand
                           over the last iterations
        information_dump: some information object you like to pass to yourself 
                          at the next iteration
    """
    # Check if we are in the very first call to our function and then return random prices
    if prices_historical is None and demand_historical is None:

        # Initialize our Information Dump
        information_dump = {
            "Message": "Very First Call to our function",
            "Number of Competitors": None,
            "Time Period": 1,
            "revenue_history": []
        }

        random_prices = np.round(np.random.uniform(30, 80, 3), 1)
        # return ([79, 79, 79], information_dump)
        return (random_prices, information_dump)

    else:
        # Get current Time Period and store in information dump
        current_period = prices_historical.shape[2] + 1
        information_dump["Time Period"] = current_period

        # Get number of competitors from information dump
        if information_dump["Number of Competitors"] != None:
            n_competitors = information_dump["Number of Competitors"]
        else:
            n_competitors = prices_historical.shape[0] - 1
            information_dump["Number of Competitors"] = n_competitors

        # Get last competitor prices for each product (note that we are at index 0
        # so we start from index 1 to only select our competitors)
        last_prices_p1 = prices_historical[1:, 0, -1]
        last_prices_p2 = prices_historical[1:, 1, -1]
        last_prices_p3 = prices_historical[1:, 2, -1]


        my_last_price = prices_historical[0, :, :]

        # Product prices
        last_prices_item1 = np.asarray(prices_historical[:, 0, :])
        last_prices_item2 = np.asarray(prices_historical[:, 1, :])
        last_prices_item3 = np.asarray(prices_historical[:, 2, :])

        # Our last price
        our_last_price = np.asarray(prices_historical[0, :, -1])


        # Use exponential smoothing to forecast expected competitor price.
        lag = 4

        # Expected pricing of each competitor, call this theta value
        item1_price = np.mean(last_prices_item1[1:, -lag:])
        item2_price = np.mean(last_prices_item2[2:, -lag:])
        item3_price = np.mean(last_prices_item3[3:, -lag:])
        recent_market_price = [item1_price, item2_price, item3_price]

        # Historical revenues, theta defined as ratio of our price to market prices
        last_revenues = [a*b for a,b in zip(our_last_price, demand_historical[:, -1])]  
        market_thetas = [a/b for a,b in zip(our_last_price, recent_market_price)]       
        
        # 5 categories of pricing

        information_dump["revenue_history"].append( [market_thetas, last_revenues, recent_market_price, list(demand_historical[:, -1])] )

        z_score_red_factor = 0.1
        next_price_p1 = np.mean(last_prices_p1).round(1) - z_score_red_factor * np.std(last_prices_p1)
        next_price_p2 = np.mean(last_prices_p2).round(1) - z_score_red_factor * np.std(last_prices_p2)
        next_price_p3 = np.mean(last_prices_p3).round(1) - z_score_red_factor * np.std(last_prices_p3)

        if information_dump["Time Period"] < 11:
            return_val = ([next_price_p1, next_price_p2, next_price_p3], information_dump)
        else:
            price_values = olig_mab_mechanism(information_dump["revenue_history"], recent_market_price)
            return_val = (price_values, information_dump)        
        # Update information dump message
        information_dump["Message"] = ""
        # return ([998, 998, 998], information_dump)

        return return_val