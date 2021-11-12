import numpy as np
import sys
import importlib
import traceback
import time
import copy
import pandas as pd
import numbers

import logging, os

logging.basicConfig(format="%(asctime)s %(name)s %(levelname)-10s %(message)s")
log = logging.getLogger("test_algorithm")
log.setLevel(int(os.environ.get("LOG_LEVEL", logging.INFO)))

sys.path.append('./dpc')

### Request Functions for Duopoly, Oligopoly and Dynamic

def duopoly_request(t,s, 
                    prices_self,price,
                    prices_competitor,
                    demand, competitor_capacity,
                    information_dump):
    if t==1 :
        prices_historical = None
        demand_historical = None
        competitor_has_capacity_current_period_in_current_season = True
    else: 
        prices_self.append(price)
        prices_competitor.append(np.random.randint(20,80))
        prices_historical = [ prices_self, prices_competitor ]
        demand.append(np.random.randint(1,10))
        demand_historical = copy.deepcopy(demand)
        competitor_has_capacity_current_period_in_current_season = competitor_capacity
        if competitor_has_capacity_current_period_in_current_season == False:
            competitor_has_capacity_current_period_in_current_season = False
        else:
            competitor_has_capacity_current_period_in_current_season = False if (t>80 and np.random.rand()>0.9) else True 

        demand_historical  = np.array(demand_historical)
        prices_historical  = np.array(prices_historical)

    if t == 1 and s == 1:
        request_input = {
            "current_selling_season" : s, 
            "selling_period_in_current_season" : t,
            "prices_historical_in_current_season" : prices_historical, 
            "demand_historical_in_current_season" : demand_historical, 
            "competitor_has_capacity_current_period_in_current_season" : competitor_has_capacity_current_period_in_current_season, 
            "information_dump": None
        }
    else:
        request_input = {
            "current_selling_season" : s, 
            "selling_period_in_current_season" : t,
            "prices_historical_in_current_season" : prices_historical, 
            "demand_historical_in_current_season" : demand_historical, 
            "competitor_has_capacity_current_period_in_current_season" : competitor_has_capacity_current_period_in_current_season, 
            "information_dump": information_dump
        }
    return request_input, competitor_has_capacity_current_period_in_current_season


def dynamic_request(t, prices_self, price,
                    prices_competitor, 
                    demand,
                    information_dump):
    if t==1 :
        prices_historical = None 
        demand_historical = None
        request_input = {
                "prices_historical" : prices_historical, 
                "demand_historical" : demand_historical,
                "information_dump": None 
            }
    else:
        prices_self.append(price)
        for i in range(len(prices_competitor)):
            prices_competitor[i].append(np.random.randint(20,80))
        prices_historical = [ prices_self, prices_competitor[0], prices_competitor[1],prices_competitor[2]]
        demand.append(np.random.randint(0,10))
        demand_historical = copy.deepcopy(demand)
        request_input = {
                "prices_historical" : np.array(prices_historical), 
                "demand_historical" : np.array(demand_historical),
                "information_dump": information_dump
            }
    return request_input


def oligopoly_request(t, prices_self, prices,
                    prices_competitor,
                    demand,
                    information_dump):
    if t==1 :
        prices_historical = None
        demand_historical = None
        request_input = {
                "prices_historical" : prices_historical, 
                "demand_historical" : demand_historical,
                "information_dump": None 
            }
    else: 
        prices_self.append(list(prices))
        prices_competitor.append([np.random.randint(20,80, 3),
                                  np.random.randint(20,80, 3),
                                  np.random.randint(20,80, 3)])
        prices_self = np.array(prices_self).transpose().reshape((1, 3, t-1))
        prices_competitor = np.array(prices_competitor).reshape((3, 3, t-1))
        prices_historical = np.concatenate((prices_self, prices_competitor))
        prices_historical = prices_historical.tolist()
        demand.append([np.random.randint(0,10),
                                           np.random.randint(0,10),
                                           np.random.randint(0,10)])

        ## Bugfix: reshape Demand Array into right format (number of products = 3) x (past iterations)
        demand = np.array(demand).reshape(3, t-1)
        
        demand_historical = copy.deepcopy(demand)
        request_input = {
                "prices_historical" : np.array(prices_historical), 
                "demand_historical" : np.array(demand_historical),
                "information_dump": information_dump
                }
    return request_input


###########################################################
###########################################################          

### Test Run Functions

def test_run_duopoly(user_code, n_selling_seasons, n_selling_periods, print_output = False):
    
    test_run_times = []
    test_run_erros = set()
    
    competitor_capacity = True

    information_dump = None

    user_results = pd.DataFrame(columns=["Selling_Season", "Selling_Period", "Price", "Competitor_has_capacity", "Demand", "Revenue", "Error", "Runtime_ms"])
    
    for selling_season in range(1, n_selling_seasons + 1):
        
        print("Currently in Selling Season: " + str(selling_season))
        print("-" * 30)
        
        prices_self = []
        if scenario == "dynamic":
            prices_competitor = [[] for _ in range(3)]
        else:
            prices_competitor = []
        demand = []
        price = 1
        for selling_period_in_current_season in range(1, n_selling_periods + 1):
            
            if selling_period_in_current_season % 50 == 0:
                print("Currently in Selling Period: " + str(selling_period_in_current_season))
                print("-" * 30)

            request_input, competitor_capacity = duopoly_request(selling_period_in_current_season,selling_season, prices_self, price, prices_competitor, demand, competitor_capacity, information_dump)
            
            if selling_period_in_current_season > 1:
                user_results.at[len(user_results)-1, "Demand"] = request_input["demand_historical_in_current_season"][-1]
                user_results.at[len(user_results)-1, "Revenue"] = request_input["demand_historical_in_current_season"][-1] * price

            start_time = time.time()
            error_this_period = False
            try:
                price, information_dump = user_code.p(**request_input)
                if isinstance(price, numbers.Number):
                    if price >= 0.1 and price <= 999:
                        pass
                    else:
                        raise Exception('price output ' + str(price) + ' is not a valid number in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
                else:
                    raise Exception('price output ' + str(price) + ' is not a valid number in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
            except:
                error = traceback.format_exc()
                test_run_erros.add(error)
                price = np.random.randint(20,80)
                error_this_period = True
            end_time = time.time()

            user_results.loc[len(user_results)] = [selling_season, selling_period_in_current_season, price, request_input["competitor_has_capacity_current_period_in_current_season"], None, None, error_this_period, (end_time-start_time)*1000] 

            test_run_times.append((end_time-start_time)*1000)

            
        last_random_demand = np.random.randint(1,10)
        user_results.at[len(user_results) - 1, "Demand"] = last_random_demand
        user_results.at[len(user_results) - 1, "Revenue"] = last_random_demand * price

        print("Finished with Selling Season: " +  str(selling_season))
        print("-" * 30)
        print("-" * 30)
        print("-" * 30)


    df_errors = pd.DataFrame(columns = ["Error_Num", "Error_Code"])

    df_times = pd.DataFrame(columns = ["Time Statistic", "Time Value (in ms)"])
    df_times.loc[len(df_times)] = ["Average Time", np.mean(test_run_times)]
    df_times.loc[len(df_times)] = ["Minimum Time", np.min(test_run_times)]
    df_times.loc[len(df_times)] = ["Maximum Time", np.max(test_run_times)]

    counter = 1
    for error in list(test_run_erros):
        df_errors.loc[len(df_errors)] = [counter, error]
        counter += 1

    writer = pd.ExcelWriter('duopoly_results.xlsx')
    user_results.to_excel(writer,'user_results')
    df_errors.to_excel(writer,'errors')
    df_times.to_excel(writer,'runtimes')

    writer.save()
       
    return 1

def test_run_dynamic(user_code, n_selling_periods, print_output = False):
    
    test_run_times = []
    test_run_erros = set()

    information_dump = None

    prices_competitor = [[] for _ in range(3)]

    demand = []
    price = 1
    prices_self = []

    user_results = pd.DataFrame(columns=["Selling_Period", "Price", "Demand", "Revenue", "Error", "Runtime_ms"])
    
        
    for selling_period_in_current_season in range(1, n_selling_periods + 1):
        
        if selling_period_in_current_season % 50 == 0:
            print("Currently in Selling Period: " + str(selling_period_in_current_season))
            print("-" * 30)

        request_input = dynamic_request(selling_period_in_current_season, prices_self, price, prices_competitor, demand, information_dump)
        
        if selling_period_in_current_season > 1:
            user_results.at[len(user_results)-1, "Demand"] = request_input["demand_historical"][-1]
            user_results.at[len(user_results)-1, "Revenue"] = request_input["demand_historical"][-1] * price

        start_time = time.time()
        error_this_period = False
        try:
            price, information_dump = user_code.p(**request_input)
            if isinstance(price, numbers.Number):
                if price >= 0.1 and price <= 999:
                    pass
                else:
                    raise Exception('price output ' + str(price) + ' is not a valid number in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
            else:
                raise Exception('price output ' + str(price) + ' is not a valid number in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
        except:
            error = traceback.format_exc()
            test_run_erros.add(error)
            price = np.random.randint(20,80)
            error_this_period = True
        end_time = time.time()

        user_results.loc[len(user_results)] = [selling_period_in_current_season, price, None, None, error_this_period, (end_time-start_time)*1000] 

        test_run_times.append((end_time-start_time)*1000)

            
    last_random_demand = np.random.randint(1,10)
    user_results.at[len(user_results) - 1, "Demand"] = last_random_demand
    user_results.at[len(user_results) - 1, "Revenue"] = last_random_demand * price

    print("Finished")
    print("-" * 30)
    print("-" * 30)
    print("-" * 30)


    df_errors = pd.DataFrame(columns = ["Error_Num", "Error_Code"])

    df_times = pd.DataFrame(columns = ["Time Statistic", "Time Value (in ms)"])
    df_times.loc[len(df_times)] = ["Average Time", np.mean(test_run_times)]
    df_times.loc[len(df_times)] = ["Minimum Time", np.min(test_run_times)]
    df_times.loc[len(df_times)] = ["Maximum Time", np.max(test_run_times)]

    counter = 1
    for error in list(test_run_erros):
        df_errors.loc[len(df_errors)] = [counter, error]
        counter += 1

    writer = pd.ExcelWriter('dynamic_results.xlsx')
    user_results.to_excel(writer,'user_results')
    df_errors.to_excel(writer,'errors')
    df_times.to_excel(writer,'runtimes')

    writer.save()
       
    return 1


def test_run_oligopoly(user_code, n_selling_periods, print_output = False):
    
    test_run_times = []
    test_run_erros = set()

    information_dump = None

    prices_competitor = []

    demand = []
    price = 1
    prices_self = []

    user_results = pd.DataFrame(columns=["Selling_Period", "Price", "Demand", "Revenue", "Error", "Runtime_ms"])
    
        
    for selling_period_in_current_season in range(1, n_selling_periods + 1):
        
        if selling_period_in_current_season % 50 == 0:
            print("Currently in Selling Period: " + str(selling_period_in_current_season))
            print("-" * 30)

        request_input = oligopoly_request(selling_period_in_current_season, prices_self, price, prices_competitor, demand, information_dump)

        if selling_period_in_current_season > 1:
            user_results.at[len(user_results)-1, "Demand"] = request_input["demand_historical"][-1]
            user_results.at[len(user_results)-1, "Revenue"] = sum(request_input["demand_historical"][:, -1] * price)

        start_time = time.time()
        error_this_period = False
        try:
            price, information_dump = user_code.p(**request_input)
            if len(price) != 3:
                raise Exception("Your function did not return 3 prices in selling period: " + str(selling_period_in_current_season))
            # Check price output
            for output in price:
                if isinstance(output, numbers.Number):
                    if output >= 0.1 and output <= 999:
                        continue
                    else:
                        raise Exception('price output ' + str(price) + ' are not valid price numbers in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
                else:
                    raise Exception('price output ' + str(price) + ' are not valid price numbers in range 0.1 to 999 in selling period: ' + str(selling_period_in_current_season))
        except:
            error = traceback.format_exc()
            test_run_erros.add(error)
            price = np.random.randint(20,80, 3)
            error_this_period = True
        end_time = time.time()

        user_results.loc[len(user_results)] = [selling_period_in_current_season, price, None, None, error_this_period, (end_time-start_time)*1000] 

        test_run_times.append((end_time-start_time)*1000)

            
    last_random_demand = np.random.randint(0,10, 3)
    user_results.at[len(user_results) - 1, "Demand"] = last_random_demand
    user_results.at[len(user_results) - 1, "Revenue"] = sum(last_random_demand * price)

    print("Finished")
    print("-" * 30)
    print("-" * 30)
    print("-" * 30)


    df_errors = pd.DataFrame(columns = ["Error_Num", "Error_Code"])

    df_times = pd.DataFrame(columns = ["Time Statistic", "Time Value (in ms)"])
    df_times.loc[len(df_times)] = ["Average Time", np.mean(test_run_times)]
    df_times.loc[len(df_times)] = ["Minimum Time", np.min(test_run_times)]
    df_times.loc[len(df_times)] = ["Maximum Time", np.max(test_run_times)]

    counter = 1
    for error in list(test_run_erros):
        df_errors.loc[len(df_errors)] = [counter, error]
        counter += 1

    writer = pd.ExcelWriter('oligpoly_results.xlsx')
    user_results.to_excel(writer,'user_results')
    df_errors.to_excel(writer,'errors')
    df_times.to_excel(writer,'runtimes')

    writer.save()
       
    return 1


if __name__ == "__main__":
    
    scenario = sys.argv[1]

    if scenario not in ["duopoly", "oligopoly", "dynamic"]:
        log.exception(
                "Selected scenario: " + str(scenario) + " not supported. Stop testing!"
            )
        sys.exit()

    try:
        log.info("Importing the function for the " + str(scenario) + " pricing scenario.")
        user_code = importlib.import_module("dpc." + str(scenario))
    except:
        log.exception(
            "Could not import the relevant function from module for " + str(scenario) + " pricing scenario. Can not perform testing"
        )
        ex_type, ex_value, ex_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(ex_traceback)
        stack_trace = list()
        for trace in trace_back:
            stack_trace.append(
                "File : %s , Line : %d, Func.Name : %s, Message : %s"
                % (trace[0], trace[1], trace[2], trace[3])
            )
        sys.exit()
    
    try:
        log.info("Running evaluation for the " + str(scenario) + " pricing scenario.")
        if scenario == "duopoly":
            success = test_run_duopoly(user_code, 5, 100)
        elif scenario == "dynamic":
            success = test_run_dynamic(user_code, 1000)
        elif scenario == "oligopoly":
            success = test_run_oligopoly(user_code, 1000)
        else:
            log.exception(
                "Selected scenario: " + str(scenario) + " not supported. Stop testing!"
            )
            sys.exit()
    except:
        log.exception(
            "Error when running the " + str(scenario) + " pricing scenario. Stop testing!"
        )
        sys.exit()