# -*- coding: utf-8 -*-
"""
Created on Tue June 11 10:56:03 2019

@author: Paul
"""

import numpy as np
from sklearn.linear_model import LinearRegression


def p(prices_historical=None, demand_historical=None, information_dump=None):
    """
    this pricing algorithm returns a random price for the first three time periods
    and then returns a weighted moving average of the competitor prices.
    
    input:
        prices_historical: numpy 2-dim array: (number competitors) x (past iterations)
                           it contains the past prices of each competitor 
                           (you are at index 0) over the past iterations
        demand_historical: numpy 1-dim array: (past iterations)
                           it contains the history of your own past observed demand
                           over the last iterations
        information_dump: some information object you like to pass to yourself 
                          at the next iteration
    """

    # Check if we are in the very first call to our function and then return a random price
    if prices_historical is None and demand_historical is None:

        # Initialize our Information Dump
        information_dump = {
            "Message": "Very First Call to our function",
            "Number of Competitors": None,
            "Time Period": 1
        }

        random_prices = np.round(np.random.uniform(30, 80), 1)

        return (random_prices, information_dump)

    else:
        # Get current Time Period and store in information dump
        current_period = prices_historical.shape[1] + 1
        information_dump["Time Period"] = current_period

        # Update information dump message
        information_dump["Message"] = ""

        # Get number of competitors from information dump
        if information_dump["Number of Competitors"] != None:
            n_competitors = information_dump["Number of Competitors"]
        else:
            n_competitors = prices_historical.shape[0] - 1
            information_dump["Number of Competitors"] = n_competitors

        # In the first three periods we still use random prices
        if current_period <= 3:
            random_prices = np.round(np.random.uniform(30, 80), 1)
            return (random_prices, information_dump)

        # From the fourth period onwards we use the moving average
        elif current_period > 3:

            # Get last 3 competitor prices for each competitor
            look_back_time = 8
            max_regression_lookback = 50
            # last_prices = prices_historical[1:, -look_back_time:]

            historical_prices = np.array(prices_historical)
            demand_historical_array = np.array(demand_historical)# [1:]

            # Compute Mean of oldest, middle and newest prices separately
            # oldest_prices_mean = np.mean(last_prices[:,0])
            # middle_prices_mean = np.mean(last_prices[:,1])
            # newest_prices_mean = np.mean(last_prices[:,2])

            # price_values = np.array([oldest_prices_mean, middle_prices_mean, newest_prices_mean])

            # Combine means using separate weights
            # next_price = np.round(0.2*oldest_prices_mean + 0.3 * middle_prices_mean + 0.5 * newest_prices_mean, 1)

            # weights = lm_model.fit(historical_prices, demand_historical_array)
            x = historical_prices[:, -max_regression_lookback:].T
            to_stack = np.ones((x.shape[0], 1))
            x_with_coef = np.hstack((to_stack, x))
            y = demand_historical_array[-max_regression_lookback:].T
            # m, c = np.linalg.lstsq(historical_prices, demand_historical_array, rcond=None)[0]
            reg_coefs = np.linalg.pinv((x_with_coef.T).dot(x_with_coef)).dot(x_with_coef.T.dot(y))

            latest_prices_array = x_with_coef[-1,:]
            demand_prediction = reg_coefs.dot(latest_prices_array)

            # where does predicted demand fall within hisotrical distribution?
            mean_historical_demand = np.mean(demand_historical_array)
            mean_historical_demand_std = np.std(demand_historical_array)

            historical_market_avg_price = np.mean(historical_prices, axis=0)
            historical_market_price_std = np.std(historical_market_avg_price)

            # adjust pricing based on z-score
            z_score_forecast_demand = (demand_prediction - mean_historical_demand)/mean_historical_demand_std

            next_price_lm = np.mean(historical_market_avg_price[-look_back_time:]) + z_score_forecast_demand*historical_market_price_std
            
            return (next_price_lm, information_dump)
