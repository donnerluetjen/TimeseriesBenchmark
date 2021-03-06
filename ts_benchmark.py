__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

import json
import resource
import time
import logging
import tracemalloc
import os
from datetime import datetime
from selected_datasets import datasets

import numpy as np
from sktime.classification.distance_based import KNeighborsTimeSeriesClassifier
from sktime.datasets import load_UCR_UEA_dataset
from sktime.utils.data_io import load_from_arff_to_dataframe
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

from sktime_dataset_analyses import dataset_properties, \
    z_normalize, \
    has_equal_length_in_all_time_series


class TimeseriesBenchmark:
    def __init__(self, window=-1, njobs=-1, normalized=False):
        self.normalized = normalized
        self.njobs = njobs
        self.window = window
        self.json_file_path = time.strftime('./Benchmarks/json/' + "%Y-%m-%d__%H-%M-%S" + '.json')
        self.accuracy_score = 0
        self.recall_score = 0
        self.f1_score = 0
        self.auroc_score = 0
        self.classifier = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.y_test_pred = None
        self.runtime = 0
        self.result_dict = {}
        self.metric_arguments = {}
        np.random.seed(1)  # required to get reproducible results
        # set filepath and suffix for arff files
        self.dataset_path = '/Users/Developer' \
                            '/.local/lib/python3.8/site-packages' \
                            '/sktime-0.5.0-py3.8-macosx-10.9-x86_64.egg' \
                            '/sktime/datasets/data'
        self.arff_file_suffix = '.arff'

    def loadDataset(self, dataset):
        # try:
        X, y = load_UCR_UEA_dataset(dataset, return_X_y=True)
        # except:
            # file_path = os.path.join(self.dataset_path, dataset,
            #                          dataset + self.arff_file_suffix)
            # X, y = load_from_arff_to_dataframe(file_path,
            #                                    return_separate_X_and_y=True)
        X_train_test = z_normalize(X) if self.normalized else X
        self.X_train, self.X_test, self.y_train, self.y_test = \
            train_test_split(X_train_test, y)

        print(f'{self.current_timestamp()}loaded dataset {dataset}')

    def current_timestamp(self):
        timestamp = datetime.now().strftime("%Y-%b-%d %H:%M:%S")
        return f'{timestamp}\t'

    def prepareClassifier(self, metric, **kwargs):
        self.metric_arguments = kwargs.copy()
        self.metric_arguments['njobs'] = self.njobs
        self.metric_arguments['z-normalized'] = self.normalized
        self.classifier = \
            KNeighborsTimeSeriesClassifier(n_jobs=self.njobs, n_neighbors=1,
                                           metric=metric, metric_params=kwargs)
        self.classifier.fit(self.X_train, self.y_train)

    def setMetric(self, metric):
        print(f'{self.current_timestamp()}      running metric {metric}')
        try:
            getattr(self, metric)()
        except AttributeError:
            logging.error(f"method {metric} is not implemented")

    def predict(self):
        start_time = time.perf_counter()
        self.y_test_pred = self.classifier.predict(self.X_test)
        self.runtime = time.perf_counter() - start_time
        print(f'{self.current_timestamp()}            run time was:        '
              f'{self.runtime}')

    def score_accuracy(self):
        self.accuracy_score = accuracy_score(self.y_test, self.y_test_pred)
        print(f'{self.current_timestamp()}            accuracy score is:   '
              f'{self.accuracy_score}')

    # in the following argument avaerage is set to 'macro' since we're dealing with fairly balanced datasets
    # from the scikit documentation:
    """
    average{‘micro’, ‘macro’, ‘samples’, ‘weighted’} or None, default=’macro’
    If None, the scores for each class are returned. Otherwise, this determines the type of averaging performed on the data: Note: multiclass ROC AUC currently only handles the ‘macro’ and ‘weighted’ averages.

    'micro':
    Calculate metrics globally by considering each element of the label indicator matrix as a label.

    'macro':
    Calculate metrics for each label, and find their unweighted mean. This does not take label imbalance into account.

    'weighted':
    Calculate metrics for each label, and find their average, weighted by support (the number of true instances for each label).

    'samples':
    Calculate metrics for each instance, and find their average.
    """
        
    def score_recall(self):
        self.recall_score = recall_score(self.y_test, self.y_test_pred,
                                         average='macro')
        print(f'{self.current_timestamp()}            recall score is:     '
              f'{self.recall_score}')

    def score_f1(self):
        self.f1_score = f1_score(self.y_test, self.y_test_pred,
                                 average='macro')
        print(f'{self.current_timestamp()}            f1 score is:         '
              f'{self.f1_score}')

    def score_auroc(self):
        if len(np.unique(self.y_train)) == 2:
            # https://scikit-learn.org/stable/modules/generated/sklearn
            # .metrics.roc_auc_score.html
            self.auroc_score = \
                roc_auc_score(self.y_test,
                              self.classifier.predict_proba(self.X_test)[:, 1],
                              average='macro')
        else:
            self.auroc_score = \
                roc_auc_score(self.y_test,
                              self.classifier.predict_proba(self.X_test),
                              average='macro', multi_class="ovo")
        print(f'{self.current_timestamp()}            auroc score is:      '
              f'{self.auroc_score}')

    def score(self):
        self.score_accuracy()
        self.score_recall()
        self.score_f1()
        self.score_auroc()

    def properties(self):
        return dataset_properties(self.X_train, self.y_train, self.X_test)

    def memory_footprint(self, usage):
        dividers = {
            'MB': 1024 * 1024,
            'KB': 1024,
            'B': 1
        }
        unit = 'MB'
        decimals = 5
        m_footprint = f"{usage / dividers[unit]:.{decimals}f} {unit}"
        print(f'            memory footprint is: {m_footprint}')
        return m_footprint

    def run_benchmark_over(self, datasets, metrics):
        for dataset in datasets:
            self.result_dict[dataset] = {}
            self.loadDataset(dataset)
            self.result_dict[dataset]['properties'] = self.properties()
            for metric in metrics:
                self.result_dict[dataset][metric] = {}
                self.setMetric(metric)
                self.result_dict[dataset][metric][
                    'arguments'] = self.metric_arguments
                self.predict()
                self.score()
                self.result_dict[dataset][metric]['accuracy'] = self.accuracy_score
                self.result_dict[dataset][metric]['recall'] = self.recall_score
                self.result_dict[dataset][metric]['f1-score'] = self.f1_score
                self.result_dict[dataset][metric]['auroc'] = self.auroc_score
                self.result_dict[dataset][metric]['runtime'] = self.runtime
                self.writeJson()

    def writeJson(self):
        with open(self.json_file_path, "w") as json_file:
            json.dump(self.result_dict, json_file, indent=6)
            json_file.flush()

    def dagdtw(self):
        return self.dagdtw_manhattan()

    def dagdtw_manhattan(self):
        metric = 'dagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 0}
        self.prepareClassifier(metric, **kwargs)

    def dagdtw_euclidean(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 1}
        self.prepareClassifier(metric, **kwargs)

    def dagdtw_chebyshev(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 2}
        self.prepareClassifier(metric, **kwargs)

    def dagdtw_minkowski(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 3}
        self.prepareClassifier(metric, **kwargs)

    def bagdtw(self):
        return self.bagdtw_manhattan()

    def bagdtw_manhattan(self):
        metric = 'bagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 0}
        self.prepareClassifier(metric, **kwargs)

    def bagdtw_euclidean(self):
        metric = 'bagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 1}
        self.prepareClassifier(metric, **kwargs)

    def bagdtw_chebyshev(self):
        metric = 'bagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 2}
        self.prepareClassifier(metric, **kwargs)

    def bagdtw_minkowski(self):
        metric = 'bagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 3}
        self.prepareClassifier(metric, **kwargs)

    def dtw(self):
        metric = 'dtw'
        kwargs = {'w': self.window}
        self.prepareClassifier(metric, **kwargs)

    def ddtw(self):
        metric = 'ddtw'
        kwargs = {'w': self.window}
        self.prepareClassifier(metric, **kwargs)

    def wdtw(self):
        metric = 'wdtw'
        kwargs = {'g': .7}
        self.prepareClassifier(metric, **kwargs)

    def wddtw(self):
        metric = 'wddtw'
        kwargs = {'g': .7}
        self.prepareClassifier(metric, **kwargs)

    def sdtw(self):
        metric = 'sdtw'
        kwargs = {'gamma': 1.0}
        self.prepareClassifier(metric, **kwargs)


if __name__ == '__main__':
    for wws in [-1, 0.3, 0.03]:
        bm = TimeseriesBenchmark(window=wws, njobs=-1, normalized=True)

        metrics = [
            'dagdtw',
            'bagdtw', 'dtw',
            'sdtw', 'ddtw',
            'wdtw', 'wddtw'
        ]

        bm.run_benchmark_over(datasets, metrics)
