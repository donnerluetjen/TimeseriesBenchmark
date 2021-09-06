__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2020 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from pathlib import Path

eol = '\\\\'

def open_score_table(tex_path, metrics=[], scores=[], caption=''):
    tex_path = Path(tex_path)
    algorithm_columns = len(metrics) * len(scores)
    with open(tex_path, 'w') as tex_table_file:
        tex_table_file.write('{{\\tiny\n')
        # construct the columns
        scores_cols = 'r' * len(scores)
        metrics_cols = '|'.join([scores_cols for i in range(len(metrics))])
        tex_table_file.write(f'\t\\begin{{longtable}}{{l|{metrics_cols}}}\n')
        table_head = table_header(metrics, scores)
        # endfirsthead
        tex_table_file.write('\n')
        tex_table_file.write(table_head)
        tex_table_file.write(f'\t\t\\endfirsthead\n')
        #endhead
        tex_table_file.write('\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{algorithm_columns + 1}}}{{c}}{{\\bfseries \\tablename \\thetable{{}}, .. continued from previous page}} {eol}\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{algorithm_columns + 1}}}{{c}}{{}} {eol}\n')
        tex_table_file.write(table_head)
        tex_table_file.write(f'\t\t\\endhead\n')
        # endfoot
        tex_table_file.write('\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{algorithm_columns + 1}}}{{c}}{{}} {eol}\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{algorithm_columns + 1}}}{{c}}{{\\bfseries  .. continued on next page}} {eol}\n')
        tex_table_file.write(f'\t\t\\endfoot\n')
        # endlastfoot
        tex_table_file.write('\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{algorithm_columns + 1}}}{{c}}{{}} {eol}\n')
        tex_table_file.write(f'\t\t\\caption{{{caption}}}\n')
        tex_table_file.write(f'\t\t\\endlastfoot\n')
        tex_table_file.write('\n')


def close_score_table(tex_path, caption='', label=''):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write(f'\t\t\\hline\n')
        tex_table_file.write(f'\t\t\\label{{tab:{label}}}\n')
        tex_table_file.write(f'\t\\end{{longtable}}\n')
        tex_table_file.write('}}\n')


def add_table_line(tex_path, data=[], highscores=[]):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write(f'\t\t{" & ".join(data_formatted(data, highscores))} {eol}\n')


def table_header(metrics=[], scores=[]):
    header = f'\t\t& \\multicolumn{{{len(metrics) * len(scores)}}}{{c}}{{Algorithms}} {eol}\n'
    
    metrics_header = '\t\t'
    for metric in metrics:
        metrics_header += f'& \\multicolumn{{{len(scores)}}}{{c}}{{{metric}}} '
    
    header += f'{metrics_header}{eol}\n'
    
    short_scores = []
    for score in scores:
        short_scores.append(label_formatted(score))
        
    header += f'\t\tDatasets & {" & ".join(short_scores * len(metrics))} {eol}\n'
    header += '\t\t\\hline\n'
    return header


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
    return label[:6]
