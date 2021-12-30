# -*- coding: utf-8 -*-
"""
Created on Tue June 11 10:56:03 2019

@author: Paul
"""

import numpy as np

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
            "Time Period": 1
        }

        random_prices = np.round(np.random.uniform(30, 80, 3), 1)

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

        # if we have only 2 competitors we use the minimum price anyone used
        if n_competitors == 2:
            next_price_p1 = np.min(last_prices_p1).round(1)
            next_price_p2 = np.min(last_prices_p2).round(1)
            next_price_p3 = np.min(last_prices_p3).round(1)

        # if we have more than 2 competitors we use the mean price anyone used
        elif n_competitors > 2:
            next_price_p1 = np.mean(last_prices_p1).round(1)
            next_price_p2 = np.mean(last_prices_p2).round(1)
            next_price_p3 = np.mean(last_prices_p3).round(1)

        # Update information dump message
        information_dump["Message"] = ""

        if next_price_p1 < 15.0:
            next_price_p1 = 15.1
        
        if next_price_p2 < 15.0:
            next_price_p2 = 15.1
        
        if next_price_p3 < 15.0:
            next_price_p3 = 15.1
        
        if next_price_p1 > 115.1:
            next_price_p1 = 115.0
        
        if next_price_p2 > 115.1:
            next_price_p2 = 115.0
        
        if next_price_p3 > 115.1:
            next_price_p3 = 115.0
        

        return ([next_price_p1, next_price_p2, next_price_p3], information_dump)