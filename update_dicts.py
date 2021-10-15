from pathlib import Path

import file_ops as fo
from dataset_details import datasets_details_json_path
import progress as p
import json


def update_agdtw_key(json_path):
    new_key_name = 'bagdtw'
    with open(json_path) as json_file:
        data = json.load(json_file)
    for dataset in data:
        if new_key_name in data[dataset].keys():
            raise ValueError("New key name exists already. Aborting ...")
        for metric in data[dataset]:
            if metric == 'agdtw':
                data[dataset][new_key_name] = data[dataset].pop(metric)
                break
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=6)
        json_file.flush()

def sort_keys(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)
    for dataset in data:
        sorted_keys = sorted(data[dataset].keys())
        sorted_keys.insert(0, sorted_keys.pop(sorted_keys.index('properties')))
        data[dataset] = {key: data[dataset][key] for key in sorted_keys}

    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=6)
        json_file.flush()


if __name__ == '__main__':

    json_store = './Benchmarks/json/'
    json_files_dict = {
        '1.0': ['UEA_archive_wws--1.json', 'UCR_archive_wws--1.json'],
        '0.3': ['UEA_archive_wws-0-3.json', 'UCR_archive_wws-0-3.json'],
        '0.1': ['UEA_archive_wws-0-1.json', 'UCR_archive_wws-0-1.json'],
        'test': ['UEA_archive_wws--1_copy.json']
    }
    wws_list = ['1.0', '0.3']

    for wws in wws_list:
        for json_file in json_files_dict[wws]:
            update_agdtw_key(json_store + json_file)
            sort_keys(json_store + json_file)
