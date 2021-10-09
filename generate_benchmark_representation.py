# This Python file uses the following encoding: utf-8
__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

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
import file_ops as fo
from selected_datasets import datasets
from dataset_details import datasets_details_json_path
import formatting as frm
import json


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
    path_dict = fo.path_dictionary(json_path)
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
    path_dict = fo.path_dictionary(json_path)
    dataset_archive = path_dict['archive']

    # load dataset details
    with open(dataset_details_file) as dd_file:
        dataset_details = json.load(dd_file)
    
    frm.progress_start('Writing datasets scoring tables')
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
        scores = [score for score in scores if score not in do_not_rank]
        
        for table_metrics_scheme in table_metrics_schemes:
            if len(table_metrics_scheme) == 0: continue
            table_file_name = f'table_{dataset_archive}_{"-".join(table_metrics_scheme)}_{"".join([c for c in table_name_specific if c != " "])}.tex'
            table_path = Path(path_dict['tex_dir'], table_file_name)
            
            table_caption = dataset_archive + ' Datasets for Metrics ' + ', '.join(table_metrics_scheme).upper() + f' \\gls{{scb}} {table_name_specific}'
            table_label = dataset_archive + '_' + '-'.join(table_metrics_scheme) + f'_scb_{"".join([c for c in table_name_specific if c != " "])}'

            score_columns_formatter = 'c' * len(scores)
            table_column_formatter = f'|l{"|".join(score_columns_formatter for i in range(len(table_metrics_scheme)))}'
            scores_table = tt.ScoreTexTable(table_path, table_column_formatter,
                                            table_caption, table_label, table_metrics_scheme, scores)
            # tt.open_score_table(table_path, table_metrics_scheme, scores)
        
            for dataset in datasets:
                table_line_list = [dataset_details[dataset]['short_name']]
                
                # get high scores for this dataset
                highscore_dict = dataset_high_scores(data[dataset], metrics, scores)
                        
                for metric in table_metrics_scheme:
                    for score in scores:
                        table_line_list.append(data[dataset][metric][score])
                table_line_list = scores_table.format_data(table_line_list, list(highscore_dict.values()))
                scores_table.add_line(table_line_list)
                # tt.add_score_table_line(table_path, table_line_list, list(highscore_dict.values()))

                frm.progress_increase()
            del scores_table  # to make sure destructor is called
            #tt.close_score_table(table_path, table_caption, table_label)
        frm.progress_end()


def dataset_high_scores(dataset, metrics, scores):
    high_score_dict = {key: 0 if key != 'runtime' else float('inf') for key in scores}
    for score in scores:
        for metric in metrics:
            high_score = high_score_dict[score]
            if score == 'runtime':
                high_score_dict[score] = min(dataset[metric][score], high_score)
            else:
                high_score_dict[score] = max(dataset[metric][score], high_score)
    return high_score_dict


if __name__ == '__main__':
    
    json_store = './Benchmarks/json/'
    wws = '1.0'

    json_files = ['UEA_archive_wws--1.json', 'UCR_archive_wws--1.json']
    for json_file in json_files:
        generate_table(json_store + json_file, datasets_details_json_path,
                       f'size={wws}', ['agdtw', 'dagdtw', 'sdtw'], do_not_rank=['recall'])
        # generate_average_diagram(json_store + json_file, f'wws={wws}', 'ranking',
        #                           do_not_rank=['recall'])
        # generate_average_diagram(json_store + json_file, f'wws={wws}', 'accuracy')
        # generate_average_diagram(json_store + json_file, f'wws={wws}', 'f1-score')
        # generate_average_diagram(json_store + json_file, f'wws={wws}', 'auroc')
