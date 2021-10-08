import json
import file_ops as fo
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sktime.datasets import load_UCR_UEA_dataset
from sktime_dataset_analyses import count_of_missing_values_in_sktime_df, \
    has_equal_length_in_all_time_series

from selected_datasets import datasets
import formatting as frm
import textable as tt

datasets_details_json_path = './Benchmarks/json/datasets_details.json'


def generate_datasets_details(json_path, datasets):
    """
    loads datasets and generates analytics for them
    :param datasets: a list of dataset names to be analyzed
    :return: a dictionary containing the following analytics
        - # dimensions
        - # instances
        - # timestamps
        - # classes
        - unique length
        - # missing values
        - len train set
        - len test set
        - imbalance ratio
        - class ratios
    """
    result_dict = {}
    frm.progress_start('Processing datasets')
    # load dataset
    for index, dataset in enumerate(datasets):
        frm.progress_increase()
        result_dict[dataset] = {}
        short_name = f'DS {index + 1}'
        result_dict[dataset]['short_name'] = short_name
        result_dict[dataset]['name'] = dataset
        # load dataset
        X, y = load_UCR_UEA_dataset(dataset, return_X_y=True)
        X_train, X_test, y_train, y_test = \
            train_test_split(X, y)
        properties = dataset_properties(X_train, y_train, y_test)
        result_dict[dataset].update(properties)
        fo.writeJson(datasets_details_json_path, result_dict)
    frm.progress_end()


def dataset_properties(X_train, y_train, X_test):
    """
    retrieve characteristics from the given dataset
    :param X_train: an sktime numpy ndarray
    :param y_train: an sktime numpy ndarray
    :param X_test: an sktime numpy ndarray
    :return: a dictionary containing the following keys:
        num_of_dimensions, num_of_instances,
        num_of_timestamps, num_of_classes,
        unique_lengths, missing_values_count,
        len train set, len test set,
        imbalance
    """
    distribution = list(y_train.value_counts())
    distribution_sum = sum(distribution)
    imbalance = (max(distribution) - min(distribution))/distribution_sum
    imbalance_str = f'{imbalance * 100:.2f}%'
    ratio_string = [f'{x/distribution_sum*100:.2f}%' for x in distribution]
    return {

        'num_of_train_instances': len(X_train),
        'num_of_test_instances': len(X_test),
        'num_of_dimensions': X_train.shape[1],
        'num_of_timestamps': len(X_train.iloc[0, 0]),
        'num_of_classes': len(np.unique(y_train)),
        'missing_values_count': int(count_of_missing_values_in_sktime_df(X_train)),
        'unique_lengths': has_equal_length_in_all_time_series(X_train),
        'imbalance': imbalance_str,
        'class_ratios': ratio_string
    }


def generate_datasets_table(json_path):
    path_dict = fo.path_dictionary(json_path)
    dataset_archive = path_dict['archive']
    
    frm.progress_start('Writing datasets details table')
    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read properties
        properties = list(data[datasets[0]].keys())
        properties.pop() # remove class_ratios

        table_file_name = f'table_{dataset_archive}_datasets.tex'
        table_path = Path(path_dict['tex_dir'], table_file_name)

        table_caption = 'Datasets Details'
        table_label = 'datasets_details'

        tt.open_details_table(table_path, properties)

        # iterate through all datasets
        for dataset in datasets:
            frm.progress_increase()
            dataset_data = data[dataset]
            dataset_values = list(dataset_data.values())
            dataset_values.pop() # remove class_ratios
            tt.add_details_table_line(table_path, dataset_values)

        tt.close_details_table(table_path, table_caption, table_label)
        frm.progress_end()

if __name__ == '__main__':
    # generate json file with dataset details
    # generate_datasets_details(datasets_details_json_path, datasets)
    # generate the datsets details table
    generate_datasets_table(datasets_details_json_path)
    