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

from pgfplots import addplot_line_to_pgfplots_file_for, open_pgfplots_file, close_pgfplots_file, \
    add_legend_to_pgfplots_file


def transformFloat(value):
    return str(value).replace('.', ',')

def generate_legend_dict(legend_array):
    result = {}

def ranking(accuracy, f1_score):
    result = sqrt(accuracy ** 2 + f1_score ** 2)
    # result = accuracy + f1_score
    return result


def json2csv(json_path):
    csv_path = Path(json_path.replace('json', 'csv'))
    csv_dir = Path(csv_path.parent, csv_path.stem)
    csv_dir.mkdir(exist_ok=True)
    tex_path = Path(csv_dir, 'pgfplots.tex')
    with open(json_path) as json_file:
        data = json.load(json_file)

        datasets = list(data.keys())
        metrics = list(data[datasets[0]].keys())

        header = ['metric', 'ranking', 'runtime']
        open_pgfplots_file(tex_path)
        add_legend_to_pgfplots_file(tex_path, datasets)
        for dataset in datasets:
            # replace filename with dataset score_name
            dataset_csv_path = Path(
                csv_dir,
                f'{dataset}{csv_path.suffix}'
            )
            addplot_line_to_pgfplots_file_for(tex_path, f'{dataset}.csv')

            with open(dataset_csv_path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(header)

                sorted_metrics = metrics
                sorted_metrics = sorted(metrics, key=lambda metric:
                data[dataset][metric]['runtime'])

                for metric in sorted_metrics:
                    dataset_row = [metric]
                    dataset_row.append(
                        ranking(data[dataset][metric]['accuracy'],
                                data[dataset][metric]['f1-score'])
                    )
                    dataset_row.append(data[dataset][metric]['runtime'])
                    csv_writer.writerow(dataset_row)
        close_pgfplots_file(tex_path)

        # generate data for average ranking
        ranking_csv_path = Path(
            csv_dir,
            f'ranking{csv_path.suffix}'
        )
        with open(ranking_csv_path, 'w') as ranking_file:
            ranking_writer = csv.writer(ranking_file)
            ranking_writer.writerow(['metric', 'average',
                                     'neg_error', 'pos_error'])
            for metric in metrics:
                sum_of_ranking = 0
                min_ranking = math.inf
                max_ranking = 0

                for dataset in datasets:
                    metrics_ranking = ranking(
                        data[dataset][metric]['accuracy'],
                        data[dataset][metric]['f1-score'])
                    sum_of_ranking += metrics_ranking
                    min_ranking = min(min_ranking, metrics_ranking)
                    max_ranking = max(max_ranking, metrics_ranking)
                average_ranking = sum_of_ranking / len(datasets)
                neg_error = average_ranking - min_ranking
                pos_error = max_ranking - average_ranking
                ranking_writer.writerow([metric.replace('_', '-'),
                                         average_ranking,
                                         neg_error, pos_error])


if __name__ == '__main__':
    json_store = './Benchmarks/json/'
    json_file = '2021-08-16__15-18-35.json'
    json2csv(json_store + json_file)
