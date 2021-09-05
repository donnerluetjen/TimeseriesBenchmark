__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2020 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from pathlib import Path

eol = '\\\\'

def open_score_table(tex_path, metrics=[], scores=[]):
    tex_path = Path(tex_path)
    algorithm_columns = len(metrics) * len(scores)
    with open(tex_path, 'w') as tex_table_file:
        tex_table_file.write('\\begin{table}[h]\n')
        tex_table_file.write(f'\t\\begin{{tabular}}{{l{"c"*algorithm_columns}}}\n')
        tex_table_file.write(f'\t\tDatasets & \\multicolumn{{{algorithm_columns}}}{{|c|}}{{Algorithms}} {eol}\n')
        metrics_header = '\t\t\t'
        for metric in metrics:
            metrics_header += f'& \\multicolumn{{len(scores)}}{{|c|}}{{{metric}}} '
        tex_table_file.write(f'{metrics_header}{eol}\n')
        tex_table_file.write(f'\t\t\t& {" & ".join(scores * len(metrics))} {eol}\n')
        tex_table_file.write('\t\t\\hline\n')


def close_score_table(tex_path, caption=''):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write('\t\t\\hline\n')
        tex_table_file.write('\t\\endtabular\n')
        tex_table_file.write('\t\\label{{tab:scores_details}}\n')
        tex_table_file.write(f'\t\\caption{{{caption}}}\n')
        tex_table_file.write('\\end{table}\n')


def add_table_line(tex_path, data=[]):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write(f'\t\t{" & ".join(data_formatted(data))} {eol}\n')


def data_formatted(data):
    pattern = "%.4f"
    return [data[0]] + [pattern % i for i in data[1:]]