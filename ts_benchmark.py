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

from memory_monitor import get_max_memory_usage
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
                self.result_dict[dataset][metric][
                    'arguments'] = self.metric_arguments
                self.predict()
                self.score()
                self.result_dict[dataset][metric][
                    'accuracy'] = self.accuracy_score
                self.result_dict[dataset][metric]['recall'] = self.recall_score
                self.result_dict[dataset][metric]['f1-score'] = self.f1_score
                self.result_dict[dataset][metric]['auroc'] = self.auroc_score
                self.result_dict[dataset][metric]['runtime'] = self.runtime
                self.writeJson()

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

    def dagdtw(self):
        return self.sagdtw_manhattan()

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

    def agdtw(self):
        return self.agdtw_manhattan()

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
        kwargs = {'w': self.window}
        self.prepareClassifier(metric, **kwargs)

    def ddtw(self):
        metric = 'ddtw'
        kwargs = {'w': self.window}
        self.prepareClassifier(metric, **kwargs)

    def wdtw(self):
        metric = 'wdtw'
        kwargs = {'g': 1}
        self.prepareClassifier(metric, **kwargs)

    def wddtw(self):
        metric = 'wddtw'
        kwargs = {'g': 1}
        self.prepareClassifier(metric, **kwargs)

    def sdtw(self):
        metric = 'sdtw'
        kwargs = {'gamma': 1.0}
        self.prepareClassifier(metric, **kwargs)


if __name__ == '__main__':
    bm = TimeseriesBenchmark(window=0.3, njobs=-1, normalized=True)
    datasets = [
        # datasets from UEA archive (multivariate)
        # "ArticularyWordRecognition",
        # "AtrialFibrillation",
        # "BasicMotions",
        # "Cricket", # needs prediction except for dagdtw
        # "Epilepsy",
        # "EyesOpenShut",
        # "FingerMovements",
        # "HandMovementDirection",
        # "Libras",
        # "NATOPS",
        # "RacketSports",
        # "SelfRegulationSCP1",
        # "SelfRegulationSCP2",
        # "StandWalkJump",
        # "UWaveGestureLibrary",

        # datasets from UCR archive (univariate)
        # "ACSF1",
        # "ArrowHead",
        # "Beef",
        # "BeetleFly",
        # "BirdChicken",
        # "BME",
        # "Car",
        # "CBF",
        # "Chinatown",
        # "Coffee",
        # "Computers",
        # "CricketX",
        # "CricketY",
        # "CricketZ",
        # "EOGHorizontalSignal",
        # "EOGVerticalSignal",
        # "FaceAll",
        # "Fish",
        # "FreezerRegularTrain",
        # "FreezerSmallTrain",
        # # "Fungi",
        # "GunPoint",
        # "GunPointAgeSpan",
        # "GunPointMaleVersusFemale",
        # "GunPointOldVersusYoung",
        # "Ham",
        # "Haptics",
        # "ItalyPowerDemand",
        # "LargeKitchenAppliances",
        # "Meat",
        # "MoteStrain",
        # "PowerCons",
        # "RefrigerationDevices",
        # "Rock",
        # "ScreenType",
        # "SemgHandGenderCh2",
        # "SemgHandMovementCh2",
        # "SemgHandSubjectCh2",
        # "ShapeletSim",
        # "ShapesAll",
        # "SmallKitchenAppliances",
        # "SmoothSubspace",
        # "SonyAIBORobotSurface2",
        # "SwedishLeaf",
        # "SyntheticControl",
        # "ToeSegmentation1",
        # "ToeSegmentation2",
        # "Trace",
        # "TwoLeadECG",
        # "TwoPatterns",
        # "UMD",
        # "UWaveGestureLibraryAll",
        # "UWaveGestureLibraryX",
        # "UWaveGestureLibraryY",
        # "UWaveGestureLibraryZ",
        "Wine",
        "WormsTwoClass",
        # "Yoga"
    ]
    # 'CharacterTrajectories', 'JapaneseVowels','SpokenArabicDigits',
    # 'GesturePebbleZ2'
    # variable length datasets are not supported by sktime

    metrics = [
                'dagdtw',
                'agdtw', 'dtw',
                'sdtw', 'ddtw',
                'wdtw', 'wddtw'
    ]

    bm.run_benchmark_over(datasets, metrics)
    # bm.writeJson()
