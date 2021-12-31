# -*- coding: utf-8 -*-
"""
Created on Tue June 11 10:56:03 2019

@author: Paul
"""

import numpy as np

LEARNING_RATE = 1e-2
DISCOUNT_FACTOR = 0.95


PRICE_GRID = np.linspace(25, 85, num=61)
CAPACITY_GRID = np.linspace(0, 80, num=81)

# initialize Q Matrix as dict()
Q_MATRIX = dict()


for i in range(CAPACITY_GRID.shape[0]):
    PRICE_DICT = dict()
    for c in range(PRICE_GRID.shape[0]):
        PRICE_DICT[PRICE_GRID[c]] = np.random.uniform(0, 100)
    
    Q_MATRIX[CAPACITY_GRID[i]] = PRICE_DICT


def get_global_max_q_state(q_matrix):
    max_key1 = 0
    max_key = 0
    max_val = 0
    for i in range(len(q_matrix)):
        max_key_temp = max(q_matrix[i], key=q_matrix[i].get)
        max_val_temp = max(q_matrix[i].values())
        max_key1_temp = i

        if max_val_temp > max_val:
            max_key = max_key_temp
            max_val = max_val_temp
            max_key1 = max_key1_temp
    
    return max_key1, max_key, max_val

def get_max_q_from_state(q_matrix, max_key1):
    max_key = 0
    max_val = 0
    state_q_dic = q_matrix[max_key1]

    for i in state_q_dic.keys():
        max_key_temp = i
        max_val_temp = state_q_dic[i]
        if max_val_temp > max_val:
            max_key = i
            max_val = max_val_temp
    
    return max_key, max_val



def p(
    current_selling_season,
    selling_period_in_current_season,
    prices_historical_in_current_season=None,
    demand_historical_in_current_season=None,
    competitor_has_capacity_current_period_in_current_season=True,
    information_dump=None,
):
    """
    this pricing algorithm would return the moving average of the last 3 prices 
    of the competitor for all selling periods > 10. 
    It utilizes the information dump (in form of a dictionary) to store information 
    on whether to adjust the moving average output.
    It returns a random price if it is the first 10 selling periods.

    input:
        current_selling_season:
                int of current selling season 1..100
        selling_period_in_current_season:
                int of current period in current selling season 1..100
        prices_historical_in_current_season:
                numpy 2-dim array: (number competitors) x (past iterations)
                it contains the past prices of each competitor
                (you are at index 0) over the past iterations
        demand_historical_in_current_season:
                numpy 1-dim array: (past iterations)
                it contains the history of your own past observed demand
                over the last iterations
        competitor_has_capacity_current_period_in_current_season:
                boolean indicator if the competitor has some free capacity
                at the beginning of the current period/ selling interval
        information_dump: 
                some information object you like to pass to yourself
                at the next iteration
    """

    # Check if we are in the very first call to our function and then return a random price
    if selling_period_in_current_season == 1 and current_selling_season == 1:
        
        capacity = 80
        
        # Initialize our Information Dump
        information_dump = {
            "Message": "Very First Call to our function",
            "Selling_Season": current_selling_season,
            "Selling_Period": selling_period_in_current_season,
            "Moving_Average_Adjustment": 0,
            "Capacity": capacity,
            "Period_Capacity_Empty": False
        }

        return (round(np.random.uniform(30, 80), 1), information_dump)

    # Check if we are in the first selling period of any selling season > 1
    if demand_historical_in_current_season is None and prices_historical_in_current_season is None:
        
        # Set Capacity to 80
        capacity = 80

        # get selling period when we stocked out in the last season
        stockout_last_season = information_dump["Period_Capacity_Empty"]

        # get moving average adjustment from the last season
        ma_adjustment_last_season = information_dump["Moving_Average_Adjustment"]
        
        # Reduce our price output by 10 % if we stocked out before the 50th period last season
        if stockout_last_season != False and stockout_last_season < 50:
            new_ma_adjustment = ma_adjustment_last_season - 0.1

        # Reduce output by 5 % if we stocked out before the 75th period
        elif stockout_last_season != False and stockout_last_season < 75:
            new_ma_adjustment = ma_adjustment_last_season - 0.05

        # if we did not stock out or after the 75th period we do not adjust 
        else:
            new_ma_adjustment = ma_adjustment_last_season

        information_dump = {
            "Message": "First Selling Period in Selling Season",
            "Selling_Season": current_selling_season,
            "Selling_Period": selling_period_in_current_season,
            "Moving_Average_Adjustment": new_ma_adjustment,
            "Capacity": capacity,
            "Period_Capacity_Empty": False
        }

        
        return (round(np.random.uniform(30, 80), 1), information_dump)

    # Return random price for first 10 periods
    if selling_period_in_current_season <= 10:
        
        # Update Capacity
        capacity_last_period = information_dump["Capacity"]
        new_capacity = capacity_last_period - demand_historical_in_current_season[-1]

        # Get Stockout Period where capacity became 0
        capacity_empty = information_dump["Period_Capacity_Empty"]

        # Check if our capacity dropped to zero and if so save the period where this happened
        if new_capacity <= 0 and capacity_empty == False:
            stockout_period = selling_period_in_current_season
        else:
            stockout_period = capacity_empty

        information_dump["Message"] = "First 10 selling periods, returning random price"
        information_dump["Selling_Season"] = current_selling_season
        information_dump["Selling_Period"] = selling_period_in_current_season
        information_dump["Capacity"] = new_capacity
        information_dump["Period_Capacity_Empty"] = stockout_period

        

        return (round(np.random.uniform(30, 80), 1), information_dump)

    # Use moving average for selling periods larger than 10
    if selling_period_in_current_season > 10:

        # Update Capacity
        capacity_last_period = information_dump["Capacity"]
        new_capacity = capacity_last_period - demand_historical_in_current_season[-1]

        # Get Stockout Period where capacity became 0
        capacity_empty = information_dump["Period_Capacity_Empty"]

        # Check if our capacity dropped to zero and if so save the period where this happened
        if new_capacity <= 0 and capacity_empty == False:
            stockout_period = selling_period_in_current_season
        else:
            stockout_period = capacity_empty

        # Get Current Moving Average Adjustment
        ma_adjustment = information_dump["Moving_Average_Adjustment"]

        # Get last 3 prices from the competitor and compute next price as mean * (1 + adjustment)
        previous_self_price = prices_historical_in_current_season[0][-1]
        prices_competitor = prices_historical_in_current_season[1]
        last_3_prices_competitor = prices_competitor[-3:]
        next_price = np.mean(last_3_prices_competitor) * (1 + ma_adjustment)
        latest_demand = demand_historical_in_current_season[-1]

        # set price that maximizes Q
        # opt_inventory, opt_price, q_value = get_max_q_state(Q_MATRIX)
        clipped_capacity = capacity_last_period if capacity_last_period > 0 else 0
        opt_price, max_q_value = get_max_q_from_state(Q_MATRIX, clipped_capacity)
        _, max_q_value_next = get_max_q_from_state(Q_MATRIX, clipped_capacity)

        # update q value, based on demand maximization, unfortunately profit is not passed in, neither do we know the immediate next demand...
        prev_q_val = Q_MATRIX[clipped_capacity][round(previous_self_price)]
        Q_MATRIX[clipped_capacity][round(previous_self_price)] = prev_q_val + LEARNING_RATE * (latest_demand + DISCOUNT_FACTOR * max_q_value_next - prev_q_val )

        information_dump["Message"] = "Moving Average"
        information_dump["Selling_Season"] = current_selling_season
        information_dump["Selling_Period"] = selling_period_in_current_season
        information_dump["Capacity"] = new_capacity
        information_dump["Period_Capacity_Empty"] = stockout_period

        return (opt_price, information_dump)
