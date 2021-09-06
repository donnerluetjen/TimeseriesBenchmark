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
    path_dict = path_dictionary(json_path)
    pgf_path = Path(path_dict['tex_dir'], f'{score_name}_pgfplots.tex')
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


def generate_table(json_path, table_name_specific='', split_table_metrics=[], do_not_rank=[]):
    path_dict = path_dictionary(json_path)
    dataset_archive = path_dict['archive']
    
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
                dataset_data = [dataset]
                
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
    json_store = './Benchmarks/json/'
    json_files = ['UEA_archive_2021-08-27.json', 'UCR_archive_2021-08-28.json']
    for json_file in json_files:
        generate_table(json_store + json_file, 'warping window = 1.0', ['agdtw', 'dagdtw', 'sdtw'], do_not_rank=['recall'])
        generate_average_diagram(json_store + json_file, 'ranking',
                                 do_not_rank=['recall'])
        generate_average_diagram(json_store + json_file, 'accuracy')
        generate_average_diagram(json_store + json_file, 'f1-score')
        generate_average_diagram(json_store + json_file, 'auroc')
