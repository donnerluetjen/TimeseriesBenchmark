import json
import file_ops as fo
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sktime.datasets import load_UCR_UEA_dataset
from sktime_dataset_analyses import count_of_missing_values_in_sktime_df, \
    has_equal_length_in_all_time_series

from selected_datasets import datasets, dataset_domains
import progress_indication as p
import textable as tt

datasets_details_json_path = './Benchmarks/json/datasets_details.json'


def datasets_property_values_list(property=''):
    with open(datasets_details_json_path) as dd:
        dataset_details = json.load(dd)
    cardinalities = set()
    for dataset in datasets:
        cardinalities.add(dataset_details[dataset][property])
    return sorted(cardinalities)


def datasets_with_property_value(property='', cardinality=0):
    with open(datasets_details_json_path) as dd:
        dataset_details = json.load(dd)
    return [dataset for dataset in datasets if dataset_details[dataset][property] == cardinality]


def generate_datasets_details(datasets):
    """
    loads datasets and generates analytics for them
    :param datasets: a list of datasets to be analyzed
    :return: a dictionary containing the following analytics
        - short_name
        - name
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
    p.progress_start('Processing datasets')
    # load dataset
    for index, dataset in enumerate(datasets):
        p.progress_increase()
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
        domain = dataset_domains[dataset]
        result_dict[dataset]['domain'] = domain
        fo.writeJson(datasets_details_json_path, result_dict)
    p.progress_end()


def dataset_properties(X_train, y_train, X_test):
    """
    retrieve characteristics from the given dataset
    :param X_train: an sktime numpy ndarray
    :param y_train: an sktime numpy ndarray
    :param X_test: an sktime numpy ndarray
    :return: a dictionary containing the following keys:
        num_of_train_instances, num_of_test_instances, num_of_dimensions,
        num_of_timestamps, num_of_classes,
        missing_values_count, unique_lengths,
        imbalance, class_ratios
    """
    distribution = list(y_train.value_counts())
    distribution_sum = sum(distribution)
    imbalance = (max(distribution) - min(distribution))/distribution_sum
    imbalance_str = f'{imbalance * 100:.2f}%'
    ratios = [x/distribution_sum for x in distribution]
    return {

        'num_of_train_instances': len(X_train),
        'num_of_test_instances': len(X_test),
        'num_of_dimensions': X_train.shape[1],
        'num_of_timestamps': len(X_train.iloc[0, 0]),
        'num_of_classes': len(np.unique(y_train)),
        'missing_values_count': int(count_of_missing_values_in_sktime_df(X_train)),
        'unique_lengths': has_equal_length_in_all_time_series(X_train),
        'imbalance': imbalance_str,
        'class_ratios': ratios
    }


def generate_details_tables(json_path):
    path_dict = fo.path_dictionary(json_path)

    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read properties
        properties = [key for key in data[datasets[0]] if key != "class_ratios"]  # remove class_ratios

        table_file_name = f'table_datasets_details.tex'
        table_path = Path(path_dict['tex_dir'], table_file_name)

        table_caption = 'Datasets Details'
        table_label = 'datasets-details'

        columns_formatter = f'|ll|{"c" * (len(properties) - 2)}|'  # works as list since all formats are single chars

        p.progress_start(f'Writing datasets imbalance table {table_file_name}')

        details_table = tt.DetailsTexTable(table_path, columns_formatter, table_caption, table_label, properties,
                                           [json_path])

        # iterate through all datasets
        for dataset in datasets:
            p.progress_increase()
            dataset_data = data[dataset]
            dataset_values = [dataset_data[property] for property in dataset_data.keys()
                              if property != 'class_ratios']  # remove class_ratios
            details_table.add_line(details_table.format_details(dataset_values))

        del details_table
        p.progress_end()


def generate_imbalance_table(json_path):
    path_dict = fo.path_dictionary(json_path)

    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read properties short_name, name, class_ratios
        properties = [prop for prop in list(data[datasets[0]].keys()) if prop in ['short_name', 'name', 'class_ratios']]

        table_file_name = f'table_datasets_imbalance.tex'
        table_path = Path(path_dict['tex_dir'], table_file_name)

        table_caption = 'Datasets Class Ratios'
        table_label = 'datasets-class-ratios'

        columns_formatter = ['|', 'l', 'l', '|', 'p{17cm}', '|']

        p.progress_start(f'Writing datasets details table {table_file_name}')

        imbalance_table = tt.ImbalanceTexTable(table_path, columns_formatter, table_caption, table_label, properties,
                                               [json_path])

        # iterate through all datasets
        for dataset in datasets:
            p.progress_increase()
            dataset_data = data[dataset]
            dataset_values = [dataset_data[prop] for prop in properties]
            imbalance_table.add_line(imbalance_table.format_details(dataset_values))

        del imbalance_table
        p.progress_end()


if __name__ == '__main__':
    # generate json file with dataset details
    # generate_datasets_details(datasets)

    # generate the datasets details table
    generate_details_tables(datasets_details_json_path)

    # generate datasets imbalance table
    generate_imbalance_table(datasets_details_json_path)

    # for cardinality in datasets_property_values_list():
    #     print(f'datasets with {cardinality} classes:\n{datasets_with_num_of_classes(cardinality)}')

    # for domain in domains():
    #     print(f'datasets with domain >{domain}<:\n{datasets_with_domain(domain)}')
    