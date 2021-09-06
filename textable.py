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
        tex_table_file.write('\\tiny\n')
        tex_table_file.write('\\center\n')
        # construct the columns
        scores_cols = 'r' * len(scores)
        metrics_cols = '|'.join([scores_cols for i in range(len(metrics))])
        tex_table_file.write(f'\t\\begin{{tabular}}{{l|{metrics_cols}}}\n')
        tex_table_file.write(f'\t\t& \\multicolumn{{{algorithm_columns}}}{{c}}{{Algorithms}} {eol}\n')
        metrics_header = '\t\t\t'
        for metric in metrics:
            metrics_header += f'& \\multicolumn{{{len(scores)}}}{{c}}{{{metric}}} '
        tex_table_file.write(f'{metrics_header}{eol}\n')
        short_scores = []
        for score in scores:
            short_scores.append(label_formatted(score))
        tex_table_file.write(f'\t\t\tDatasets & {" & ".join(short_scores * len(metrics))} {eol}\n')
        tex_table_file.write('\t\t\\hline\n')


def close_score_table(tex_path, caption='', label=''):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write('\t\t\\hline\n')
        tex_table_file.write('\t\\end{tabular}\n')
        tex_table_file.write('\t\\label{{tab:scores_details}}\n')
        tex_table_file.write(f'\t\\caption{{{caption}}}\n')
        tex_table_file.write(f'\t\\label{{tab:{label}}}\n')
        tex_table_file.write('\\end{table}\n')


def add_table_line(tex_path, data=[], highscores=[]):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write(f'\t\t{" & ".join(data_formatted(data, highscores))} {eol}\n')


def data_formatted(data, highscores=[]):
    pattern = "%.4f"
    result = [data.pop(0)]
    for index, datum in enumerate(data):
        if datum == highscores[index % len(highscores)]:
            result.append(f'$\\boldsymbol{{{pattern % datum}}}$')
        else:
            result.append(f'${pattern % datum}$')     
    return result

def label_formatted(label=''):
    return label[:5]
