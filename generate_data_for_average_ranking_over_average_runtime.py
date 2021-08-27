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

import pgfplots as pp


def transformFloat(value):
    return str(value).replace('.', ',')


def generate_legend_dict(legend_array):
    result = {}


def ranking(scores):
    keys = scores.keys()
    squared_result = 0
    for key in keys:

        # do not evaluate arguments and runtime
        if key in ['arguments', 'runtime']:
            continue

        squared_result += scores[key] ** 2
    return sqrt(squared_result)


def generate_average_ranking_diagram(json_path, score_name='Unknown'):
    path_dict = path_dictionary(json_path, score_name)
    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read metrics and drop properties
        metrics = list(data[datasets[0]].keys())
        metrics.remove('properties')

        header = ['average-ranking', 'average-runtime']
        pp.open_pgfplots_file(path_dict['tex_path'],
                              'Average Ranking over Average Runtime',
                              'Average Runtime', 'Average Ranking')
        pp.add_legend_to_pgfplots_file(path_dict['tex_path'], metrics)

        for metric in metrics:
            # replace filename with metric score_name
            metric_csv_path = csv_path_for(metric, path_dict)
            pp.addplot_line_to_pgfplots_file_for(path_dict['tex_path'],
                                                 f'{metric}.csv',
                                                 x_col=2, y_col=1)

            with open(metric_csv_path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(header)

                # iterate over datasets for metric and find averages
                accumulated_ranking = 0
                accumulated_runtime = 0
                for dataset in datasets:
                    accumulated_ranking += ranking(data[dataset][metric])
                    accumulated_runtime += data[dataset][metric]['runtime']

                csv_writer.writerow([metric,
                                     accumulated_ranking / len(datasets),
                                     accumulated_runtime / len(datasets)])
        pp.close_pgfplots_file(path_dict['tex_path'])

def path_dictionary(json_path, score_name):
    csv_converted_json_path = Path(json_path.replace('json', 'csv'))
    csv_dir = Path(csv_converted_json_path.parent,
                   csv_converted_json_path.stem, score_name)
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = Path(csv_dir, csv_converted_json_path.stem + '.csv')
    tex_path = Path(csv_dir, f'pgfplots.tex')
    return {'csv_dir': csv_dir, 'csv_path': csv_path, 'tex_path': tex_path}

def csv_path_for(metric, path_dict):
    return Path(path_dict['csv_dir'],
                f'{metric}{path_dict["csv_path"].suffix}')

def generate_single_score_diagram(json_path, score_name='Unknown'):
    path_dict = path_dictionary(json_path, score_name)
    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read metrics and drop properties
        metrics = list(data[datasets[0]].keys())
        metrics.remove('properties')

        header = ['dataset', score_name]

        for metric in metrics:
            metric_csv_path = csv_path_for(metric, path_dict)
            with open(metric_csv_path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(header)

                for dataset in datasets:
                    csv_writer.writerow(
                        [dataset, data[dataset][metric][score_name]]
                    )

        # write pgfplots file
        capital_score_name = score_name.capitalize()
        pp.open_single_score_pgfplots_file(
            path_dict['tex_path'],
            f'{capital_score_name} over Dataset', 'Dataset',
            capital_score_name, metric_csv_path)
        pp.add_legend_to_pgfplots_file(path_dict['tex_path'], metrics)
        for metric in metrics:
            pp.addplot_line_to_single_score_pgfplots_file_for(
                path_dict['tex_path'], f'{metric}.csv', x_col=0, y_col=1
            )
        pp.close_pgfplots_file(path_dict['tex_path'])


if __name__ == '__main__':
    json_store = './Benchmarks/json/'
    json_file = '2021-08-27__18-45-44.json'
    generate_average_ranking_diagram(json_store + json_file,
                                     'average_ranking_over_average_runtime')
    generate_single_score_diagram(json_store + json_file, 'accuracy')
    generate_single_score_diagram(json_store + json_file, 'recall')
    generate_single_score_diagram(json_store + json_file, 'f1-score')
    generate_single_score_diagram(json_store + json_file, 'auroc')
