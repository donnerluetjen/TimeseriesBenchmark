import progress as p
import json
from dataset_details import datasets_details_json_path


def add_confusion_values(input_json, output_json):
    # load dataset details
    with open(datasets_details_json_path) as dd_file:
        dataset_details = json.load(dd_file)

    with open(input_json, 'r') as json_file:
        data = json.load(json_file)
        # retrieve the keys
        datasets = list(data.keys())
        dataset_keys = list(data[datasets[0]].keys())
        dataset_keys.remove('properties')
        metrics = dataset_keys
        metric_keys = list(data[datasets[0]][metrics[0]].keys())
        metric_keys.remove('arguments')
        scores = metric_keys

        for dataset in datasets:
            for metric in metrics:
                current_scores = data[dataset][metric]
                accuracy = current_scores['accuracy']
                recall = current_scores['recall']
                f1 = current_scores['f1-score']
                auroc = current_scores['auroc']
                total = dataset_details[dataset]['num_of_test_instances']

                # derive confusion values
                derived_precision = (f1 * recall) / (2 * recall - f1)
                # FixMe: with accuracy = 1 tp would be 0 ??? if precision = 1 and recall = 1 -> division by zero !!!
                tp = total * (1 - accuracy) / (1 / derived_precision + 1 / recall - 2)
                tn = accuracy * total - tp
                fp = tp / derived_precision - tp
                fn = tp / recall - tp
                specificity = tn / (fp + tn)
                tpr = recall
                fpr = 1 - specificity
                derived_accuracy = (tp + tn) / (tp + fp + tn + fn)
                derived_recall = tp / (tp + fn)
                derived_f1_score = (2 * derived_precision * derived_recall) / (derived_precision + derived_recall)
                derived_auroc = (fpr * tpr / 2) + (specificity * (1 - tpr) / 2) + (specificity * tpr)

                # store in data
                data[dataset][metric]['derived-accuracy'] = derived_accuracy
                data[dataset][metric]['derived-recall'] = derived_recall
                data[dataset][metric]['derived-f1-score'] = derived_f1_score
                data[dataset][metric]['derived-auroc'] = derived_auroc
                data[dataset][metric]['precision'] = derived_precision
                data[dataset][metric]['specificity'] = specificity
                data[dataset][metric]['tp'] = tp
                data[dataset][metric]['tn'] = tn
                data[dataset][metric]['fp'] = fp
                data[dataset][metric]['fn'] = fn

    with open(output_json, 'w') as new_data:
        json.dump(data, new_data, indent=6)
        new_data.flush()


if __name__ == '__main__':
    json_store = './Benchmarks/json/'
    json_files_dict = {
        '1.0': ['UEA_archive_wws--1.json', 'UCR_archive_wws--1.json'],
        '0.3': ['UEA_archive_wws-0-3.json', 'UCR_archive_wws-0-3.json'],
        '0.1': ['UEA_archive_wws-0-1.json', 'UCR_archive_wws-0-1.json']
    }
    wws_list = ['1.0', '0.3']

    for wws in wws_list:
        for json_file in json_files_dict[wws]:
            json_confusion_added_file = json_file.replace('.', '_plus-derived.')

            add_confusion_values(json_store + json_file,
                                 json_store + json_confusion_added_file)
