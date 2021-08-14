__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2020 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

import numpy as np


def dataset_properties(X_train, y_train):
    '''
    retrieve characteristics from the given dataset
    :param self:
    :param X_train: an sktime numpy ndarray
    :param y_train: an sktime numpy ndarray
    :return: a dictionary containing the following keys:
        num_of_dimensions, num_of_instances,
        num_of_timestamps, num_of_classes
    '''
    return {

        'num_of_dimensions': X_train.shape[1],
        'num_of_instances': X_train.shape[0],
        'num_of_timestamps': len(X_train.iloc[0, 0]),
        'num_of_classes': len(np.unique(y_train)),
        'unique_lengths': has_equal_length_in_all_time_series(X_train),
        'missing_values_count': int(
            count_of_missing_values_in_sktime_df(X_train)
        )
    }


def has_equal_length_in_all_time_series(sktime_df, verbose=False):
    """
    check whether any (possibly) multivariate time series is actually a
    time series in the given dataframe
    :param verbose:
    :param sktime_df:
    :return:
    """
    if not has_same_time_series_length_for_each_dimension(sktime_df, verbose):
        print("Some row(s) of the given dataframe does(do) not contain "
              "equal number of timestamps for each dimension")
        return False

    # compare lengths of first dimension of each instance
    first_dimension = 0
    first_time_series_length = len(sktime_df.iloc[0, first_dimension])
    for i in range(1, len(sktime_df.index)):
        if first_time_series_length != len(sktime_df.iloc[i, first_dimension]):
            return False
    return True


def has_same_time_series_length_for_each_dimension(sktime_df, verbose=False):
    """
    function to check whether in sktime_df, for every row, length of
    panda series in each column is the same, for multivariate time series
    datasets, this check ensures that a single multivariate time series is
    actually the time series
    (whether number of time stamps of every dimension is the same)
    :param sktime_df:
    :param verbose:
    :return:
    """
    unique_row_wise_lengths_dict = {}
    for index in sktime_df.index:
        unique_lengths_for_this_index = \
            set([len(sktime_df.loc[index, col]) for col in sktime_df])
        if len(unique_lengths_for_this_index) > 1:
            # there is more than one different time series lengths
            unique_row_wise_lengths_dict[index] = unique_lengths_for_this_index

    if verbose:
        for key in unique_row_wise_lengths_dict:
            print("time series at index", key, " have different lengths =>",
                  unique_row_wise_lengths_dict[key])

    # if there is at least one key,
    # then there is at least one problematic time series in the data
    return len(unique_row_wise_lengths_dict) == 0


def count_of_missing_values_in_sktime_df(sktime_df, verbose=False):
    count = 0
    for col in sktime_df.columns:
        df_dim = sktime_df[col]
        count += missing_values_count_in_nested_pd_series(df_dim, verbose)
    return count


def missing_values_count_in_nested_pd_series(nested_pd_series, verbose=False):
    count = 0
    for i in nested_pd_series.index:
        count += nested_pd_series[i].isna().sum()
        if verbose:
            print('Missing Values count: ', count)
    return count
