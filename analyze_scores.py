__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2020 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

import json


def conditions_met(metric_dict):
    # check scores for condition
    condition_scores = ['accuracy', 'recall', 'f1-score']
    for condition_score in condition_scores:
        if metric_dict[condition_score] != 1.0:
            return False
    return True


def store_scores_one(dataset_name, metric_name, window_size, metric_dict,
                     target_dict):
    window_size_key = f'Warping Window Size = {window_size}'
    target_dict.setdefault(dataset_name, {})
    target_dict[dataset_name].setdefault(window_size_key, {})
    # remove unwanted entries
    metric_dict = {k: v for (k, v) in metric_dict.items() if
                   k not in ['arguments', 'runtime']}
    target_dict[dataset_name][window_size_key].setdefault(metric_name,
                                                          metric_dict)


if __name__ == '__main__':

    datasets_with_scores_one = {}

    json_store = './Benchmarks/json/'
    json_score_one_file = 'score_one.json'

    json_files_dict = {
        '1.0': ['UEA_archive_wws--1.json', 'UCR_archive_wws--1.json'],
        '0.3': ['UEA_archive_wws-0-3.json', 'UCR_archive_wws-0-3.json'],
        '0.1': ['UEA_archive_wws-0-1.json', 'UCR_archive_wws-0-1.json']
    }
    wws_list = ['1.0', '0.3', '0.1']

    for wws in wws_list:
        for json_file in json_files_dict[wws]:
            with open(json_store + json_file) as scores_file:
                dataset_scores = json.load(scores_file)

            for dataset in dataset_scores:
                metrics = sorted([metric for metric in dataset_scores[dataset]
                                  if metric != 'properties'])
                for metric in metrics:
                    metric_dict = dataset_scores[dataset][metric]
                    if conditions_met(metric_dict):
                        store_scores_one(dataset, metric, wws, metric_dict,
                                         datasets_with_scores_one)

    with open(json_store + json_score_one_file, 'w') as score_one_file:
        json.dump(datasets_with_scores_one, score_one_file, indent=6)
        score_one_file.flush()
