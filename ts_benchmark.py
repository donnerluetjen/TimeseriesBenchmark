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

import numpy as np
from sktime.classification.distance_based import KNeighborsTimeSeriesClassifier
from sktime.datasets import load_UCR_UEA_dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

from memory_monitor import get_max_memory_usage
from sktime_dataset_analyses import dataset_properties, \
    has_equal_length_in_all_time_series


class TimeseriesBenchmark:
    def __init__(self, window=-1, njobs=-1):
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

    def loadDataset(self, dataset):
        X, y = load_UCR_UEA_dataset(dataset, return_X_y=True)
        self.X_train, self.X_test, self.y_train, self.y_test = \
            train_test_split(X, y)
        print(f'loaded dataset {dataset}')

    def prepareClassifier(self, metric, **kwargs):
        self.metric_arguments = kwargs.copy()
        self.metric_arguments['njobs'] = self.njobs
        self.classifier = \
            KNeighborsTimeSeriesClassifier(n_jobs=self.njobs, n_neighbors=1,
                                           metric=metric, metric_params=kwargs)
        self.classifier.fit(self.X_train, self.y_train)

    def setMetric(self, metric):
        print(f'      running metric {metric}')
        try:
            getattr(self, metric)()
        except AttributeError:
            logging.error(f"method {metric} is not implemented")

    def predict(self):
        start_time = time.perf_counter()
        self.y_test_pred = self.classifier.predict(self.X_test)
        self.runtime = time.perf_counter() - start_time

    def score_accuracy(self):
        self.accuracy_score = accuracy_score(self.y_test, self.y_test_pred)
        print(f'            accuracy score is:   {self.accuracy_score}')

    def score_recall(self):
        self.recall_score = recall_score(self.y_test, self.y_test_pred,
                                         average='macro')
        print(f'            reacll score is:     {self.recall_score}')

    def score_f1(self):
        self.f1_score = f1_score(self.y_test, self.y_test_pred,
                                 average='macro')
        print(f'            f1 score is:         {self.f1_score}')

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
        print(f'            auroc score is:      {self.auroc_score}')

    def score(self):
        self.score_accuracy()
        self.score_recall()
        self.score_f1()
        self.score_auroc()
        print(f'            run time was:        {self.runtime}')

    def get_accuracy_score(self):
        return self.accuracy_score

    def get_recall_score(self):
        return self.recall_score

    def get_f1_score(self):
        return self.f1_score

    def get_auroc_score(self):
        return self.auroc_score

    def properties(self):
        return dataset_properties(self.X_train, self.y_train)

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
                self.result_dict[dataset][metric]['arguments'] = self.metric_arguments
                memory_used = get_max_memory_usage(self.predict)
                self.score()
                self.result_dict[dataset][metric][
                    'accuracy'] = self.accuracy_score
                self.result_dict[dataset][metric]['recall'] = self.recall_score
                self.result_dict[dataset][metric]['f1-score'] = self.f1_score
                self.result_dict[dataset][metric]['auroc'] = self.auroc_score
                self.result_dict[dataset][metric]['runtime'] = self.runtime
                self.result_dict[dataset][metric][
                    'memory_footprint'] = self.memory_footprint(memory_used)
                # self.writeJson()

    def writeJson(self):
        with open(self.json_file_path, "w") as json_file:
            json.dump(self.result_dict, json_file, indent=6)
            json_file.flush()

    def agdtwbt_sigma_1_cumulative_similarity(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': 1, 'pseudo_distance': False,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_point66_cumulative_similarity(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': .66, 'pseudo_distance': False,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_point33_cumulative_similarity(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': .33, 'pseudo_distance': False,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_1_average_similarity(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': 1, 'pseudo_distance': False,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_point66_average_similarity(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': .66, 'pseudo_distance': False,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_point33_average_similarity(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': .33, 'pseudo_distance': False,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_1_cumulative_pseudodistance(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_point66_cumulative_pseudodistance(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': .66, 'pseudo_distance': True,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_point33_cumulative_pseudodistance(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': .33, 'pseudo_distance': True}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_1_average_pseudodistance(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_point66_average_pseudodistance(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': .66, 'pseudo_distance': True,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def agdtwbt_sigma_point33_average_pseudodistance(self):
        metric = 'agdtwbt'
        kwargs = {'sigma': .33, 'pseudo_distance': True,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_1_cumulative_similarity(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': False,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_point66_cumulative_similarity(self):
        metric = 'sagdtw'
        kwargs = {'sigma': .66, 'pseudo_distance': False,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_point33_cumulative_similarity(self):
        metric = 'sagdtw'
        kwargs = {'sigma': .33, 'pseudo_distance': False,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_1_average_similarity(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': False,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_point66_average_similarity(self):
        metric = 'sagdtw'
        kwargs = {'sigma': .66, 'pseudo_distance': False,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_point33_average_similarity(self):
        metric = 'sagdtw'
        kwargs = {'sigma': .33, 'pseudo_distance': False,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_1_cumulative_pseudodistance(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_point66_cumulative_pseudodistance(self):
        metric = 'sagdtw'
        kwargs = {'sigma': .66, 'pseudo_distance': True,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_point33_cumulative_pseudodistance(self):
        metric = 'sagdtw'
        kwargs = {'sigma': .33, 'pseudo_distance': True,
                  'average_aggregation': False}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_1_average_pseudodistance(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_point66_average_pseudodistance(self):
        metric = 'sagdtw'
        kwargs = {'sigma': .66, 'pseudo_distance': True,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_sigma_point33_average_pseudodistance(self):
        metric = 'sagdtw'
        kwargs = {'sigma': .33, 'pseudo_distance': True,
                  'average_aggregation': True}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_manhattan(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 0}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_euclidean(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 1}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_chebyshev(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 2}
        self.prepareClassifier(metric, **kwargs)

    def sagdtw_minkowski(self):
        metric = 'sagdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 3}
        self.prepareClassifier(metric, **kwargs)

    def agdtw_manhattan(self):
        metric = 'agdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 0}
        self.prepareClassifier(metric, **kwargs)

    def agdtw_euclidean(self):
        metric = 'agdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 1}
        self.prepareClassifier(metric, **kwargs)

    def agdtw_chebyshev(self):
        metric = 'agdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 2}
        self.prepareClassifier(metric, **kwargs)

    def agdtw_minkowski(self):
        metric = 'agdtw'
        kwargs = {'sigma': 1, 'pseudo_distance': True,
                  'average_aggregation': False, 'window': self.window,
                  'distance_composition': 3}
        self.prepareClassifier(metric, **kwargs)

    def dtw(self):
        metric = 'dtw'
        kwargs = {}
        self.prepareClassifier(metric, **kwargs)

    def ddtw(self):
        metric = 'ddtw'
        kwargs = {}
        self.prepareClassifier(metric, **kwargs)

    def wdtw(self):
        metric = 'wdtw'
        kwargs = {'g': 0.05}
        self.prepareClassifier(metric, **kwargs)

    def wddtw(self):
        metric = 'wddtw'
        kwargs = {'g': 0.05}
        self.prepareClassifier(metric, **kwargs)

    def sdtw(self):
        metric = 'sdtw'
        kwargs = {}
        self.prepareClassifier(metric, **kwargs)


if __name__ == '__main__':
    bm = TimeseriesBenchmark(window=0.1, njobs=-1)
    datasets = [
        "AtrialFibrillation",
        "BasicMotions", "FingerMovements",
        "HandMovementDirection", "Heartbeat", "SelfRegulationSCP1",
        "SelfRegulationSCP2"
    ]
    # 'CharacterTrajectories', 'JapaneseVowels','SpokenArabicDigits'
    # variable length datasets are not supported by sktime

    metrics = [
                # 'sagdtw_manhattan',
                # 'sagdtw_euclidean', 'sagdtw_chebyshev',
                # 'sagdtw_minkowski',
               'agdtw_manhattan', 'agdtw_euclidean', 'agdtw_chebyshev',
               'agdtw_minkowski',
               'dtw', 'sdtw', 'ddtw',
                'wdtw', 'wddtw'
    ]

    bm.run_benchmark_over(datasets, metrics)
    bm.writeJson()
