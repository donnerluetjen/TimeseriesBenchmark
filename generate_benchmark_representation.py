# This Python file uses the following encoding: utf-8
__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from math import sqrt
from pathlib import Path

import pgfplots as pp
import textable as tt
import file_ops as fo
from dataset_details import datasets_details_json_path
import progress as p
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


def generate_score_diagram(json_path, plot_name_specific='', score_name='ranking', do_not_rank=[]):
    path_dict = fo.path_dictionary(json_path)
    plot_file_name = f'pgfplot_{score_name}_{"".join([c for c in plot_name_specific if c != " "])}.tex'
    pgf_path = Path(path_dict['tex_dir'], plot_file_name)
    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read metrics and drop properties
        metrics = list(data[datasets[0]].keys())
        metrics.remove('properties')

        p.progress_start(f'Writing datasets plots {plot_file_name}')
        plot = pp.TexPlots(pgf_path, score_name.capitalize(), 'Mean Runtime', f'Mean {score_name.capitalize()}')

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
            plot.add_data(metric, table_data)
            p.progress_increase()
        del plot  # to ensure destructor is called before program exits
        p.progress_end()


def generate_table(json_path, dataset_details_file, table_name_specific='', split_table_metrics=[], do_not_rank=[]):
    path_dict = fo.path_dictionary(json_path)
    dataset_archive = path_dict['archive']

    # load dataset details
    with open(dataset_details_file) as dd_file:
        dataset_details = json.load(dd_file)

    with open(json_path) as json_file:
        data = json.load(json_file)
        high_scores = datasets_high_scores(data)

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

            table_caption = dataset_archive + ' Datasets for Metrics ' + ', '.join(
                table_metrics_scheme).upper() + f' \\gls{{scb}} {table_name_specific}'
            table_label = dataset_archive + '_' + '-'.join(
                table_metrics_scheme) + f'_scb_{"".join([c for c in table_name_specific if c != " "])}'

            score_columns_formatter = 'c' * len(scores)
            # table_column_formatter works as formatter list since all formats are single chars
            table_column_formatter = f'|l|{"|".join(score_columns_formatter for i in range(len(table_metrics_scheme)))}|'

            p.progress_start(f'Writing datasets scoring table {table_file_name}')

            scores_table = tt.ScoreTexTable(table_path, table_column_formatter,
                                            table_caption, table_label, table_metrics_scheme, scores)

            for dataset in datasets:
                table_line_list = [dataset_details[dataset]['short_name']]

                format_bold = [False]  # short_name should not be bold

                for metric in table_metrics_scheme:
                    for score in scores:
                        table_line_list.append(data[dataset][metric][score])
                        format_bold.append(True if high_scores[dataset][score] == metric else False)
                scores_table.add_line(table_line_list, format_bold)

                p.progress_increase()
            del scores_table  # to make sure destructor is called
            p.progress_end()


def datasets_high_scores(data=None):
    if data is None:
        return None
    datasets = list(data.keys())
    dataset_keys = list(data[datasets[0]].keys())
    dataset_keys.remove('properties')
    metrics = dataset_keys
    metric_keys = list(data[datasets[0]][metrics[0]].keys())
    metric_keys.remove('arguments')
    scores = metric_keys
    high_score_dict = {}
    for dataset in datasets:

        high_score_dict[dataset] = {}

        for score in scores:

            high_score = 0 if score != 'runtime' else float('inf')
            comparator = max if score != 'runtime' else min

            for metric in metrics:
                score_value = data[dataset][metric][score]
                if score_value == comparator(score_value, high_score):
                    high_score = score_value
                    high_score_dict[dataset][score] = metric
    return high_score_dict


if __name__ == '__main__':

    json_store = './Benchmarks/json/'
    json_files_dict = {
        '1.0': ['UEA_archive_wws--1.json', 'UCR_archive_wws--1.json'],
        '0.3': ['UEA_archive_wws-0-3.json', 'UCR_archive_wws-0-3.json'],
        '0.1': ['UEA_archive_wws-0-1.json', 'UCR_archive_wws-0-1.json']
    }
    wws_list = ['1.0', '0.3']

    for wws in wws_list:
        for json_file in json_files_dict[wws]:
            generate_table(json_store + json_file, datasets_details_json_path,
                           f'size={wws}', ['agdtw', 'dagdtw', 'sdtw'])
            generate_score_diagram(json_store + json_file, f'wws={wws}', 'ranking')
            generate_score_diagram(json_store + json_file, f'wws={wws}', 'accuracy')
            generate_score_diagram(json_store + json_file, f'wws={wws}', 'recall')
            generate_score_diagram(json_store + json_file, f'wws={wws}', 'f1-score')
            generate_score_diagram(json_store + json_file, f'wws={wws}', 'auroc')
