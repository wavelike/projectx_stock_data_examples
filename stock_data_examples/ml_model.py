from stock_data_examples.utils.ConfigsParameters import *
from stock_data_examples.basic_financials.Environment import Environment

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def linear_fit(data):
    x = list(range(0, data.shape[0]))
    y = data.tolist()

    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)

    return z[0], z[1], p


def calc_deviation_from_mean_over_std(close_prices):

    # Take last 10 days window and subtract mean from each value to get values fluctuating around 0.
    prices_mean_reduced = close_prices - close_prices.rolling(10, min_periods=1).mean()

    # Linear fit
    _, _, p_l1 = linear_fit(prices_mean_reduced)
    x = list(range(0, prices_mean_reduced.shape[0]))

    # Subtract trend from the values
    prices_trend_reduced = pd.Series(np.asarray(prices_mean_reduced) - p_l1(x), index=prices_mean_reduced.index)

    # Calculate standard deviation for a window of 10 days and ratio of each days deviation to mean over local standard deviation
    prices_std = prices_trend_reduced.rolling(10, min_periods=1).std()
    deviation_from_mean_over_std = prices_mean_reduced / prices_std

    return deviation_from_mean_over_std


def prepare_observations(stocks):
    # Iterate over all stocks and calculate features, stored in a dataframe 'observation'

    observations = pd.DataFrame(None)
    for stock_symbol in stocks:
        print(stock_symbol)
        active_stock = stocks[stock_symbol]
        stock_observations = pd.DataFrame(index=active_stock.price_history.index)
        close_prices = active_stock.price_history["close"]

        # Feature "close_price_ratio": Relative difference of current close price and prior close price
        close_prices_shifted = close_prices.shift(1)  # shift all prices down by one row
        stock_observations["close_price_ratio"] = close_prices / close_prices_shifted

        # Feature 'slope': slope of linear fit of last 10 days window of close prices
        fit_function = lambda x: linear_fit(x)[0]
        stock_observations["slope"] = close_prices.rolling(10, min_periods=1).apply(fit_function)

        # Feature 'deviation_from_mean_over_std': Calculates ratio of a day's close price deviation from mean relative to last 10 days
        #   standard deviation, thus detecting unusual strong deviations
        stock_observations["deviation_from_mean_over_std"] = calc_deviation_from_mean_over_std(close_prices)

        # Property used for model evaluation: Relative change of price one day ahead
        close_prices_shifted = close_prices.shift(-1)  # shift all prices down by one row
        stock_observations["next_day_close_price_ratio"] = close_prices_shifted / close_prices

        observations = observations.append(stock_observations.dropna())

    return observations


def categorise_observations(observations):
    # categorise the "next_day_close_price-ratio" values into 6 categories
    indexes = observations[observations["next_day_close_price_ratio"] >= 1.0].index.values
    observations.loc[indexes, "evaluation"] = "+0"

    indexes = observations[observations["next_day_close_price_ratio"] > 1.002].index.values
    observations.loc[indexes, "evaluation"] = "1"

    indexes = observations[observations["next_day_close_price_ratio"] > 1.015].index.values
    observations.loc[indexes, "evaluation"] = "2"

    indexes = observations[observations["next_day_close_price_ratio"] < 1.0].index.values
    observations.loc[indexes, "evaluation"] = "-0"

    indexes = observations[observations["next_day_close_price_ratio"] < 0.998].index.values
    observations.loc[indexes, "evaluation"] = "-1"

    indexes = observations[observations["next_day_close_price_ratio"] < 0.985].index.values
    observations.loc[indexes, "evaluation"] = "-2"

# load stock data from filesystem or database (pickled objects), as specified in configs
stocks = Environment.load_all(configs)

# get feature observations for all stocks and each day in index
observations = prepare_observations(stocks)

# Divide each observation into one category used as evaluation in the ml model
categorise_observations(observations)

# drop property columns that should not be used to train
observations = observations.drop(columns=["next_day_close_price_ratio"])

# split observations dataset into train and test sets
observations['train'] = np.random.uniform(0, 1, observations.shape[0]) <= 0.85
train, test = observations[observations['train'] == True], observations[observations['train'] == False]
print('Number of observations in the training data:', len(train))
print('Number of observations in the test data:', len(test))
print('\n')

# Create a list of the feature column's names
features = observations.drop(columns=["evaluation", "train"]).columns
print("features: " + str(features.values))
print('\n')

# evaluation set
evaluation = train["evaluation"]

# Create a random forest Classifier
rf_classifier = RandomForestClassifier(n_jobs=2, random_state=0)  # n_jobs: number of jobs run in aprallel (if -1: number of cores)

# Train the model
rf_classifier.fit(train[features], evaluation)

# Calculate accuracy of the prediction twice: First measures exact prediction rate, second measure the trend prediction rate,
#   meaning if the stock price trend increases, all predictions indicating positive increase are considered as correctly predicted
predicted_values = rf_classifier.predict(test[features])
amount = 0
correctly_predicted = 0
correct_trend_predicted = 0
for ii in range(0, len(predicted_values)):

    amount += 1
    if predicted_values[ii] == test["evaluation"].iloc[ii]:
        correctly_predicted += 1

    if test["evaluation"].iloc[ii] in ["+0", "1", "2"]:
        if predicted_values[ii] in ["+0", "1", "2"]:
            correct_trend_predicted += 1

    elif test["evaluation"].iloc[ii] in ["-0", "-1", "-2"]:
        if predicted_values[ii] in ["-0", "-1", "-2"]:
            correct_trend_predicted += 1

print("accuracy_exact: " + str(correctly_predicted/amount))
print("accuracy_trend: " + str(correct_trend_predicted / amount))

# Create confusion matrix
confusion_matrix = pd.crosstab(test['evaluation'], predicted_values, rownames=['Real evaluation'],
                               colnames=['Predicted Evaluation'])
print("\n")
print("confusion matrix:")
print(confusion_matrix)

# View a list of the features and their importance scores
print('\n')
print("feature importance:")
print(list(zip(train[features], rf_classifier.feature_importances_)))

# Plot each stock and save image in output folder
for symbol, active_stock in stocks.items():
    close_prices = active_stock.price_history["close"]
    title = active_stock.name + "\n" + active_stock.price_history.index.values[0] + " - " + \
            active_stock.price_history.index.values[-1]
    ax = close_prices.plot(title=title, xticks=[0, close_prices.shape[0]])
    ax.set_ylabel("close prices")
    ax.set_xticklabels([close_prices.index.values[0], close_prices.index.values[-1]])
    fig = ax.get_figure()
    fig.savefig(configs["output_folderpath"] + symbol + ".png", format='png')
    fig.clear()