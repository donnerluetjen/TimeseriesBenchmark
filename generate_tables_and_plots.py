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
from dataset_details import datasets_details_json_path, class_cardinalities, datasets_with_num_of_classes
import progress_indication as p
import json


def ranking(scores, do_not_rank=None):
    exclude = ['arguments', 'runtime']
    if do_not_rank is not None:
        exclude += do_not_rank
    keys = [key for key in scores.keys() if key not in exclude]
    squared_result = 0
    for key in keys:
        squared_result += scores[key] ** 2
    return sqrt(squared_result)


def datasets_high_scores(data=None):
    if data is None:
        return None
    datasets = list(data.keys())
    metrics = [key for key in data[datasets[0]].keys() if key != 'properties']
    scores = [key for key in data[datasets[0]][metrics[0]].keys() if key != 'arguments']
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


def generate_class_number_grouped_ranking_diagramm(uea_json_path, ucr_json_path, scb='1.0'):
    path_dict = fo.path_dictionary(uea_json_path)
    plot_file_name = f'pgfplot_{scb}_ranking_over_class_number.tex'
    pgf_path = Path(path_dict['tex_dir'], plot_file_name)
    sources = [uea_json_path, ucr_json_path, datasets_details_json_path]
    with open(uea_json_path) as uea_json_file:
        data = json.load(uea_json_file)
    with open(ucr_json_path) as ucr_json_file:
        data.update(json.load(ucr_json_file))
    cardinalities = class_cardinalities()

    metrics = [metric for metric in data[list(data.keys())[0]] if metric != 'properties']
    class_cardinality_scores = {}
    for cardinality in cardinalities:
        class_cardinality_scores[cardinality] = {}
        cardinality_datasets = datasets_with_num_of_classes(cardinality)
        for metric in metrics:
            ranking_sum = 0
            for dataset in cardinality_datasets:
                ranking_sum += ranking(data[dataset][metric])
            class_cardinality_scores[cardinality][metric] = ranking_sum / len(cardinality_datasets)
    # we have the dictionary to be in the form of { cardinality: { metric: ranking } }
    # we want the dictionary to be in the form of { metric: { cardinality: ranking } }
    metric_class_cardinality_scores = {}
    for metric in metrics:
        metric_class_cardinality_scores[metric] = {}
        for cardinality in cardinalities:
            metric_class_cardinality_scores[metric][cardinality] = class_cardinality_scores[cardinality][metric]

    p.progress_start(f'Writing datasets plots {plot_file_name}')
    plot = pp.TexPlots(pgf_path, 'Class Cardinality', 'Mean Ranking', sources)

    for metric in metrics:
        plot.add_data(metric, [[cardinality, metric_class_cardinality_scores[metric][cardinality]]
                               for cardinality in cardinalities])
        p.progress_increase()

    del plot  # to ensure destructor is called before program exits
    p.progress_end()


def generate_trend_diagram(folder='', file_list=None, name='', do_not_rank=None):
    if file_list is None:
        file_list = []
    if do_not_rank is None:
        do_not_rank = []
    if name == '' or not len(file_list):
        return

    path_dict = fo.path_dictionary(folder + 'SCB_trends.json')
    plot_file_name = f'pgfplot_{name}_scb_trend.tex'
    pgf_path = Path(path_dict['tex_dir'], plot_file_name)
    sources = []
    for file in file_list:
        sources.append(folder + file)

    all_files_data = {}  # initialize empty dictionary
    # collect all data
    for file in file_list:
        file_path = folder + file

        with open(file_path) as scoring_file:
            temp_data = json.load(scoring_file)

        datasets = temp_data.keys()
        wws = temp_data[list(datasets)[0]]['bagdtw']['arguments']['window']

        # clean dictionary of unnecessary data
        for dataset in datasets:
            temp_data[dataset].pop('properties')
            metrics = temp_data[dataset].keys()
            for metric in metrics:
                temp_data[dataset][metric].pop('arguments')

        all_files_data[wws] = temp_data

    wwss = list(all_files_data.keys())
    datasets = list(all_files_data[wwss[0]].keys())
    metrics = list(all_files_data[wwss[0]][datasets[0]].keys())
    scores = list(all_files_data[wwss[0]][datasets[0]][metrics[0]].keys())

    p.progress_start(f'Writing datasets plots {plot_file_name}')
    plot = pp.TrendPlots(pgf_path, 'Mean Runtime', 'Mean Ranking', sources, True)

    for metric in metrics:
        table_data = []
        for wws in wwss:
            datasets = list(all_files_data[wws].keys())
            accumulated_scoring = 0
            accumulated_runtime = 0
            for dataset in datasets:
                accumulated_scoring += ranking(all_files_data[wws][dataset][metric], do_not_rank)
                accumulated_runtime += all_files_data[wws][dataset][metric]['runtime']
            table_data.append([accumulated_runtime / len(datasets), accumulated_scoring / len(datasets), abs(wws)])
            plot.add_data(metric, table_data)
            p.progress_increase()

    del plot  # to ensure destructor is called before program exits
    p.progress_end()


def generate_score_diagram(json_path, plot_name_specific='', score_name='ranking', do_not_rank=None):
    path_dict = fo.path_dictionary(json_path)
    plot_file_name = f'pgfplot_{score_name}_{"".join([c for c in plot_name_specific if c != " "])}.tex'
    pgf_path = Path(path_dict['tex_dir'], plot_file_name)
    sources = [json_path]
    with open(json_path) as json_file:
        data = json.load(json_file)

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = list(data[datasets[0]].keys())
    metrics.remove('properties')

    p.progress_start(f'Writing datasets plots {plot_file_name}')
    plot = pp.TexPlots(pgf_path, 'Mean Runtime', f'Mean {score_name.capitalize()}', sources, True)

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


def generate_table(json_path, dataset_details_file, table_name_specific='', split_table_metrics=None, do_not_rank=None):
    path_dict = fo.path_dictionary(json_path)
    dataset_archive = path_dict['archive']

    if split_table_metrics is None:
        split_table_metrics = []
    if do_not_rank is None:
        do_not_rank = []
    sources = [json_path, dataset_details_file]

    # load dataset details
    with open(dataset_details_file) as dd_file:
        dataset_details = json.load(dd_file)

    with open(json_path) as json_file:
        data = json.load(json_file)

    high_scores = datasets_high_scores(data)

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = [key for key in data[datasets[0]] if key != 'properties']

    # split metrics into schemes for the two tables
    table_metrics_schemes = [sorted(split_table_metrics), sorted(list(set(metrics) - set(split_table_metrics)))]

    # read scores and drop arguments
    omitted = do_not_rank + ['arguments']
    scores = [key for key in data[datasets[0]][metrics[0]] if key not in omitted]
    scores = [score for score in scores if score not in do_not_rank]

    for table_metrics_scheme in table_metrics_schemes:
        if len(table_metrics_scheme) == 0:
            continue
        table_file_name = f'table_{dataset_archive}_{"-".join(table_metrics_scheme)}_{"".join([c for c in table_name_specific if c != " "])}.tex'
        table_path = Path(path_dict['tex_dir'], table_file_name)

        table_caption = dataset_archive + ' Datasets for Metrics ' + ', '.join(
            table_metrics_scheme).upper() + f' \\gls{{scb}} {table_name_specific}'
        table_label = dataset_archive + '_' + '-'.join(
            table_metrics_scheme) + f'_scb_{"".join([c for c in table_name_specific if c != " "])}'

        score_columns_formatter = 'c' * len(scores)
        # table_column_formatter works as formatter list since all formats are single chars
        table_column_formatter = f'|l|{"|".join(score_columns_formatter for _ in range(len(table_metrics_scheme)))}|'

        p.progress_start(f'Writing datasets scoring table {table_file_name}')

        scores_table = tt.ScoreTexTable(table_path, table_column_formatter,
                                        table_caption, table_label, table_metrics_scheme, scores, sources)

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


def generate_distance_consolidations_diagram(json_path, score_name='ranking', do_not_rank=None):
    path_dict = fo.path_dictionary(json_path)
    plot_file_name = f'pgfplot_{score_name}_distance_consolidations.tex'
    pgf_path = Path(path_dict['tex_dir'], plot_file_name)
    sources = [json_path]
    with open(json_path) as json_file:
        data = json.load(json_file)

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = sorted([key for key in data[datasets[0]] if key != 'properties'])

    p.progress_start(f'Writing datasets plots {plot_file_name}')
    plot = pp.TexPlots(pgf_path, 'Mean Runtime', f'Mean {score_name.capitalize()}', sources)

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


def generate_distance_consolidations_table(json_path, dataset_details_file, do_not_rank=None):
    path_dict = fo.path_dictionary(json_path)
    dataset_archive = path_dict['archive']

    if do_not_rank is None:
        do_not_rank = []

    sources = [json_path, dataset_details_file]

    # load dataset details
    with open(dataset_details_file) as dd_file:
        dataset_details = json.load(dd_file)

    with open(json_path) as json_file:
        data = json.load(json_file)

    high_scores = datasets_high_scores(data)

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = sorted([key for key in data[datasets[0]] if key != 'properties'])

    # read scores and drop arguments
    omitted = do_not_rank + ['arguments']
    scores = [key for key in data[datasets[0]][metrics[0]] if key not in omitted]
    scores = [score for score in scores if score not in do_not_rank]

    table_file_name = f'table_distance_consolidations.tex'
    table_path = Path(path_dict['tex_dir'], table_file_name)

    table_caption = 'Datasets for Distance Consolidation Methods'
    table_label = 'distance-consolidations'

    score_columns_formatter = 'c' * len(scores)
    # table_column_formatter works as formatter list since all formats are single chars
    table_column_formatter = f'|l|{"|".join(score_columns_formatter for _ in range(len(metrics)))}|'

    p.progress_start(f'Writing datasets scoring table {table_file_name}')

    norms_table = tt.ScoreTexTable(table_path, table_column_formatter,
                                   table_caption, table_label, metrics, scores, sources)

    for dataset in datasets:
        table_line_list = [dataset_details[dataset]['short_name']]

        format_bold = [False]  # short_name should not be bold

        for metric in metrics:
            for score in scores:
                table_line_list.append(data[dataset][metric][score])
                format_bold.append(True if high_scores[dataset][score] == metric else False)
        norms_table.add_line(table_line_list, format_bold)

        p.progress_increase()

    del norms_table  # to make sure destructor is called
    p.progress_end()


if __name__ == '__main__':

    json_store = './Benchmarks/json/'
    json_files_dict = {
        '1.0': ['UEA_archive_wws--1.json', 'UCR_archive_wws--1.json'],
        '0.3': ['UEA_archive_wws-0-3.json', 'UCR_archive_wws-0-3.json'],
        '0.1': ['UEA_archive_wws-0-1.json', 'UCR_archive_wws-0-1.json']
    }
    wws_list = ['1.0', '0.3', '0.1']

    uea_list = []
    ucr_list = []

    for wws in wws_list:
        #    for json_file in json_files_dict[wws]:
        #         generate_table(json_store + json_file, datasets_details_json_path,
        #                        f'size={wws}')  # , ['bagdtw', 'dagdtw', 'sdtw'])
        #         generate_score_diagram(json_store + json_file, f'wws={wws}', 'ranking')
        #         generate_score_diagram(json_store + json_file, f'wws={wws}', 'accuracy')
        #         generate_score_diagram(json_store + json_file, f'wws={wws}', 'recall')
        #         generate_score_diagram(json_store + json_file, f'wws={wws}', 'f1-score')
        #         generate_score_diagram(json_store + json_file, f'wws={wws}', 'auroc')
        #
        #     uea_list.append(json_files_dict[wws][0])
        #     ucr_list.append(json_files_dict[wws][1])
        #
        # generate_trend_diagram(json_store, uea_list, 'UEA')
        # generate_trend_diagram(json_store, ucr_list, 'UCR')
        #
        # json_data_file = 'UEA_distance_consolidations_0-03.json'
        # generate_distance_consolidations_table(json_store + json_data_file, datasets_details_json_path)
        # generate_distance_consolidations_diagram(json_store + json_data_file, 'ranking')
        generate_class_number_grouped_ranking_diagramm(json_store + json_files_dict[wws][0],
                                                       json_store + json_files_dict[wws][1],
                                                       wws)
