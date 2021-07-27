__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

import json
import csv


def transformFloat(value):
    return str(value).replace('.', ',')

def json2csv(json_path):
    csv_path = json_path.replace('.json', '.csv')
    with open(json_path) as json_file:
        data = json.load(json_file)

    with open(csv_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        datasets = list(data.keys())
        metrics = list(data[datasets[0]].keys())
        analytics = list(data[datasets[0]][metrics[0]].keys())
        noOfDatasets = len(datasets)
        noOfMetrics = len(metrics)
        noOfAnalytics = len(analytics)

        header_1 = metrics
        header_1 = ['Datasets / Metrics']
        for metric in metrics:
            header_1.append(metric)
            for comma in range(noOfAnalytics - 1):
                header_1.append('')
        csv_writer.writerow(header_1)

        header_2 = ['']
        for m in range(noOfMetrics):
            for analytic in analytics:
                header_2.append(analytic)
        csv_writer.writerow(header_2)
        for dataset in datasets:
            dataset_row = [dataset]
            for metric in metrics:
                for analytic in analytics:
                    dataset_row.append(
                        transformFloat(data[dataset][metric][analytic]))
            csv_writer.writerow(dataset_row)

if __name__ == '__main__':
    json_path = './One_NN.json'
    json2csv(json_path)