import json
import csv
from pathlib import Path


def writeJson(json_file_path, property_dict):
    with open(json_file_path, "w") as json_file:
        json.dump(property_dict, json_file, indent=6)
        json_file.flush()


def path_dictionary(json_path):
    tex_converted_json_path = Path(json_path.replace('json', 'tex'))
    archive = tex_converted_json_path.stem[0:3]
    tex_root = Path(tex_converted_json_path.parent)
    tex_corr = Path(tex_root, 'Correlations')
    tex_corr.mkdir(parents=True, exist_ok=True)
    tex_dir = Path(tex_converted_json_path.parent, tex_converted_json_path.stem)
    tex_dir.mkdir(parents=True, exist_ok=True)
    return {'tex_dir': tex_dir, 'archive': archive, 'tex_root': tex_root, 'tex_corr': tex_corr}


def csv_path_for(metric, path_dict):
    return Path(path_dict['csv_dir'],
                f'{metric}{path_dict["csv_path"].suffix}')
