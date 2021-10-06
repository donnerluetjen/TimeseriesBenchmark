# This Python file uses the following encoding: utf-8
__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

import json
import csv
import math
from math import sqrt
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sktime.datasets import load_UCR_UEA_dataset

import pgfplots as pp
import textable as tt
from sktime_dataset_analyses import count_of_missing_values_in_sktime_df, \
    has_equal_length_in_all_time_series


def transformFloat(value):
    return str(value).replace('.', ',')


def ranking(scores, do_not_rank=[]):
    keys = scores.keys()
    squared_result = 0
    for key in keys:

        # do not evaluate arguments and runtime
        # and skip this scores in do_not rank for ranking
        if key in ['arguments', 'runtime'] + do_not_rank:
            continue

        squared_result += scores[key] ** 2
    return sqrt(squared_result)


def generate_average_diagram(json_path, table_name_specific='', score_name='ranking', do_not_rank=[]):
    path_dict = path_dictionary(json_path)
    pgf_path = Path(path_dict['tex_dir'], f'pgfplot_{score_name}_{"".join([c for c in table_name_specific if c != " "])}.tex')
    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read metrics and drop properties
        metrics = list(data[datasets[0]].keys())
        metrics.remove('properties')

        header = ['metric', f'average-{score_name}', 'average-runtime']
        pp.init_pgfplots_file(pgf_path,
                              f'Mean {score_name.capitalize()} vs. Mean Runtime',
                              'Mean Runtime', f'Mean {score_name.capitalize()}')

        for metric in metrics:
            # iterate over datasets for metric and find averages
            accumulated_scoring = 0
            accumulated_runtime = 0
            for dataset in datasets:
                if score_name == 'ranking':
                    accumulated_scoring += ranking(data[dataset][metric], do_not_rank)
                else:
                    accumulated_scoring += data[dataset][metric][score_name]
                accumulated_runtime += data[dataset][metric]['runtime']

            table_data = [[accumulated_runtime / len(datasets), accumulated_scoring / len(datasets)]]
            pp.add_table(pgf_path, metric, table_data)


def generate_table(json_path, dataset_details_file, table_name_specific='', split_table_metrics=[], do_not_rank=[]):
    path_dict = path_dictionary(json_path)
    dataset_archive = path_dict['archive']

    # load dataset details
    with open(dataset_details_file) as dd_file:
        dataset_details = json.load(dd_file)
    
    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read metrics and drop properties
        metrics = list(data[datasets[0]].keys())
        metrics.remove('properties')
        
        # split metrics into schemes for the two tables
        table_metrics_schemes = [sorted(split_table_metrics), sorted(list(set(metrics) - set(split_table_metrics)))]

        # read scores and drop arguments
        scores = list(data[datasets[0]][metrics[0]].keys())
        scores.remove('arguments')
        for remove in do_not_rank:
            scores.remove(remove)
        
        for table_metrics_scheme in table_metrics_schemes:
            if len(table_metrics_scheme) == 0: continue
            table_file_name = f'table_{dataset_archive}_{"-".join(table_metrics_scheme)}_{"".join([c for c in table_name_specific if c != " "])}.tex'
            table_path = Path(path_dict['tex_dir'], table_file_name)
            
            table_caption = dataset_archive + ' Datasets for Metrics ' + ', '.join(table_metrics_scheme).upper() + f' ({table_name_specific})'
            table_label = dataset_archive + '_' + '-'.join(table_metrics_scheme) + f'_{"".join([c for c in table_name_specific if c != " "])}'
            
            tt.open_score_table(table_path, table_metrics_scheme, scores, table_caption)
        
            for dataset in datasets:
                dataset_data = [dataset_details[dataset]['short_name']]
                
                # get highscores for this dqtaset
                highscore_dict = {key:0 if key != 'runtime' else float('inf') for key in scores}
                for metric in metrics:
                    for score in scores:
                        highscore_dict = highscores(score, data[dataset][metric][score], highscore_dict)
                        
                for metric in table_metrics_scheme:
                    for score in scores:
                    
                        if score in do_not_rank:
                            continue
                        
                        score_value = data[dataset][metric][score]
                        dataset_data.append(score_value)
                tt.add_table_line(table_path, dataset_data, list(highscore_dict.values()))
                
            tt.close_score_table(table_path, table_caption, table_label)


def highscores(score, value, dict):
    highscore = dict[score]
    if score == 'runtime':
        if value < highscore: dict[score] = value
    else:
        if value > highscore: dict[score] = value
    return dict


def generate_datasets_details_dict(json_path, datasets):
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
    """
    result_dict = {}
    # load dataset
    for index, dataset in enumerate(datasets):
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
        writeJson(json_path, result_dict)
    return result_dict


def writeJson(json_file_path, property_dict):
    with open(json_file_path, "w") as json_file:
        json.dump(property_dict, json_file, indent=6)
        json_file.flush()


def dataset_properties(X_train, y_train, X_test):
    """
    retrieve characteristics from the given dataset
    :param self:
    :param X_train: an sktime numpy ndarray
    :param y_train: an sktime numpy ndarray
    :return: a dictionary containing the following keys:
        num_of_dimensions, num_of_instances,
        num_of_timestamps, num_of_classes
    """
    distribution = y_train.value_counts().values
    imbalance = (distribution.max() - distribution.min())/distribution.sum()
    imbalance_str = f'{imbalance * 100:.2f}%'
    return {

        'num_of_dimensions': X_train.shape[1],
        'num_of_instances': X_train.shape[0],
        'num_of_timestamps': len(X_train.iloc[0, 0]),
        'num_of_classes': len(np.unique(y_train)),
        'imbalance': imbalance_str,
        'unique_lengths': has_equal_length_in_all_time_series(X_train),
        'missing_values_count': int(
            count_of_missing_values_in_sktime_df(X_train)
        ),
        'len train set': len(X_train),
        'len test set': len(X_test)
    }


def generate_datasets_table(json_path):
    path_dict = path_dictionary(json_path)
    dataset_archive = path_dict['archive']

    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read properties
        properties = list(data[datasets[0]].keys())

        table_file_name = f'table_{dataset_archive}_datasets.tex'
        table_path = Path(path_dict['tex_dir'], table_file_name)

        table_caption = dataset_archive + ' Datasets Details'
        table_label = dataset_archive + '_details'

        tt.open_details_table(table_path, properties, table_caption)

        # iterate through all datasets
        for dataset in datasets:
            dataset_data = data[dataset]
            tt.add_details_table_line(table_path, dataset_data.values())

        tt.close_details_table(table_path, table_caption, table_label)


def path_dictionary(json_path):
    tex_converted_json_path = Path(json_path.replace('json', 'tex'))
    archive = tex_converted_json_path.stem[0:3]
    tex_dir = Path(tex_converted_json_path.parent, tex_converted_json_path.stem)
    tex_dir.mkdir(parents=True, exist_ok=True)
    return {'tex_dir': tex_dir, 'archive': archive}


def csv_path_for(metric, path_dict):
    return Path(path_dict['csv_dir'],
                f'{metric}{path_dict["csv_path"].suffix}')


if __name__ == '__main__':
    datasets = [
        # datasets from UEA archive (multivariate)
        "ArticularyWordRecognition",
        "AtrialFibrillation",
        "BasicMotions",
        "Cricket", # needs prediction except for dagdtw
        "Epilepsy",
        "EyesOpenShut",
        "FingerMovements",
        "HandMovementDirection",
        "Libras",
        "NATOPS",
        "RacketSports",
        "SelfRegulationSCP1",
        "SelfRegulationSCP2",
        "StandWalkJump",
        "UWaveGestureLibrary",

        # datasets from UCR archive (univariate)
        "ACSF1",
        "ArrowHead",
        "Beef",
        "BeetleFly",
        "BirdChicken",
        "BME",
        "Car",
        "CBF",
        "Chinatown",
        "Coffee",
        "Computers",
        "CricketX",
        "CricketY",
        "CricketZ",
        "EOGHorizontalSignal",
        "EOGVerticalSignal",
        "FaceAll",
        "Fish",
        "FreezerRegularTrain",
        "FreezerSmallTrain",
        "GunPoint",
        "GunPointAgeSpan",
        "GunPointMaleVersusFemale",
        "GunPointOldVersusYoung",
        "Ham",
        "Haptics",
        "ItalyPowerDemand",
        "LargeKitchenAppliances",
        "Meat",
        "MoteStrain",
        "PowerCons",
        "RefrigerationDevices",
        "Rock",
        "ScreenType",
        "SemgHandGenderCh2",
        "SemgHandMovementCh2",
        "SemgHandSubjectCh2",
        "ShapeletSim",
        "ShapesAll",
        "SmallKitchenAppliances",
        "SmoothSubspace",
        "SonyAIBORobotSurface2",
        "SwedishLeaf",
        "SyntheticControl",
        "ToeSegmentation1",
        "ToeSegmentation2",
        "Trace",
        "TwoLeadECG",
        "TwoPatterns",
        "UMD",
        "UWaveGestureLibraryAll",
        "Wine",
        "WormsTwoClass",
        ]
    dataset_json_file_name = 'datasets_details'
    json_store = './Benchmarks/json/'

    # datasets_props = generate_datasets_details_dict(json_store + 'datasets_details', datasets)
    # generate_datasets_table(json_store + dataset_json_file_name)

    json_files = ['UEA_archive_2021-08-27.json', 'UCR_archive_2021-08-28.json']
    for json_file in json_files:
        generate_table(json_store + json_file, json_store + dataset_json_file_name,
                       'warping window = 1.0', ['agdtw', 'dagdtw', 'sdtw'], do_not_rank=['recall'])
        # generate_average_diagram(json_store + json_file, 'warping window = 1.0', 'ranking',
        #                          do_not_rank=['recall'])
        # generate_average_diagram(json_store + json_file, 'warping window = 1.0', 'accuracy')
        # generate_average_diagram(json_store + json_file, 'warping window = 1.0', 'f1-score')
        # generate_average_diagram(json_store + json_file, 'warping window = 1.0', 'auroc')
