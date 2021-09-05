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

import pgfplots as pp
import textable as tt


def transformFloat(value):
    return str(value).replace('.', ',')


def generate_legend_dict(legend_array):
    result = {}


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


def generate_average_diagram(json_path, score_name='ranking', do_not_rank=[]):
    path_dict = path_dictionary(json_path, score_name)
    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read metrics and drop properties
        metrics = list(data[datasets[0]].keys())
        metrics.remove('properties')

        header = ['metric', f'average-{score_name}', 'average-runtime']
        pp.open_pgfplots_file(path_dict['tex_path'],
                              f'Average {score_name.capitalize()} over Average Runtime',
                              'Average Runtime', f'Average {score_name.capitalize()}')
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
                accumulated_scoring = 0
                accumulated_runtime = 0
                for dataset in datasets:
                    if score_name == 'ranking':
                        accumulated_scoring += ranking(data[dataset][metric], do_not_rank)
                    else:
                        accumulated_scoring += data[dataset][metric][score_name]
                    accumulated_runtime += data[dataset][metric]['runtime']

                csv_writer.writerow([metric,
                                     accumulated_scoring / len(datasets),
                                     accumulated_runtime / len(datasets)])
        pp.close_pgfplots_file(path_dict['tex_path'])


def generate_table(json_path, do_not_rank=[]):
    path_dict = path_dictionary(json_path, 'score_table')
    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        # read metrics and drop properties
        metrics = list(data[datasets[0]].keys())
        metrics.remove('properties')

        # read scores and drop arguments
        scores = list(data[datasets[0]][metrics[0]].keys())
        scores.remove('arguments')
        for remove in do_not_rank:
            scores.remove(remove)
        
        tt.open_score_table(path_dict['tex_table_path'], metrics, scores)
        
        for dataset in datasets:
            dataset_data = [dataset]
            for metric in metrics:
                for score in scores:
                    
                    if score in do_not_rank:
                        continue
                        
                    score_value = data[dataset][metric][score]
                    dataset_data.append(score_value)
            tt.add_table_line(path_dict['tex_table_path'], dataset_data)
            
        
        tt.close_score_table(path_dict['tex_table_path'], 'UEA Datasets')
    

def path_dictionary(json_path, score_name):
    csv_converted_json_path = Path(json_path.replace('json', 'csv'))
    csv_dir = Path(csv_converted_json_path.parent,
                   csv_converted_json_path.stem, score_name)
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = Path(csv_dir, csv_converted_json_path.stem + '.csv')
    tex_path = Path(csv_dir, f'pgfplots.tex')
    tex_table_path = Path(csv_dir, f'scores_table.tex')
    return {'csv_dir': csv_dir, 'csv_path': csv_path, 'tex_path': tex_path, 'tex_table_path': tex_table_path}

def csv_path_for(metric, path_dict):
    return Path(path_dict['csv_dir'],
                f'{metric}{path_dict["csv_path"].suffix}')


if __name__ == '__main__':
    json_store = './Benchmarks/json/'
    json_files = ['UEA_archive_2021-08-27.json', 'UCR_archive_2021-08-28.json']
    for json_file in json_files:
        generate_table(json_store + json_file, do_not_rank=['recall', 'runtime'])
        generate_average_diagram(json_store + json_file, 'ranking',
                                 do_not_rank=['recall'])
        generate_average_diagram(json_store + json_file, 'accuracy')
        generate_average_diagram(json_store + json_file, 'f1-score')
        generate_average_diagram(json_store + json_file, 'auroc')
