"""
    Title: Moving Average Crossover Momentum Strategy Template
    Description: The moving average crossover momentum strategy is
    implemented on the selected asset.
    Dataset: US Equities

    ############################# DISCLAIMER #############################
    This is a strategy template only and should not be used for live
    trading without appropriate backtesting and tweaking of the strategy
    parameters.
    ######################################################################
"""

# Import numpy
import numpy as np


# Import blueshift libraries
from blueshift.api import (
                            symbol,
                            order_target_percent,
                            schedule_function,
                            date_rules,
                            time_rules,
                            get_datetime
                        )


def initialize(context):
    # Define symbol
    context.security = symbol('QCOM')

    # Define short term window size
    context.short_term_window = 40

    # Define long term window size
    context.long_term_window = 70

    # Define lookback
    context.lookback = context.long_term_window + context.short_term_window

    # Schedule the rebalance function
    schedule_function(
                        rebalance,
                        date_rule=date_rules.every_day(),
                        time_rule=time_rules.market_close(minutes=5)
                     )


def rebalance(context, data):
    """
        A function to rebalance the portfolio. This function is called by the
        schedule_function above.
    """


    try:
        # Fetch lookback no. days data for the given security
        prices = data.history(
        context.security,
        ['close'],
        context.lookback,
        '1d')
    except IndexError:
        return

    # Store the short term moving average in a new column 'window_ST'
    prices.loc[:, 'window_ST'] = prices['close'].rolling(
                                            context.short_term_window).mean()

    # Store the long term moving average in a new column 'window_LT'
    prices.loc[:, 'window_LT'] = prices['close'].rolling(
                                            context.long_term_window).mean()

    # Get the latest signal
    prices.loc[:, 'signal'] = np.where(
                            prices['window_ST'] > prices['window_LT'], 1, -1)

    latest_signal = prices.loc[:, 'signal'][-1]
    print("{} Signal generated {}".format(get_datetime(), latest_signal))
    # Place the order
    if latest_signal == 1:
        print("{} Going long on {}".format(get_datetime(), context.security))
        order_target_percent(context.security, 1)

    elif latest_signal == -1:
        print("{} Going short on {}".format(get_datetime(), context.security))
        order_target_percent(context.security, -1)

    else:
        print("{} Exiting position in {}".format(get_datetime(), context.security))
        order_target_percent(context.security, 0)