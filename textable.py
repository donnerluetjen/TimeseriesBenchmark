__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2020 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from pathlib import Path
from formatting import timestamp

eol = '\\\\'


############################# 
#                           #
#    score table methods    #
#                           #
#############################

def open_score_table(tex_path, metrics=[], scores=[]):
    tex_path = Path(tex_path)
    algorithm_columns = len(metrics) * len(scores)
    with open(tex_path, 'w') as tex_table_file:
        tex_table_file.write(f'% {timestamp()}\n')
        tex_table_file.write('{{\\tiny\n')
        # construct the columns
        scores_cols = 'c' * len(scores)
        metrics_cols = '|'.join([scores_cols for i in range(len(metrics))])
        tex_table_file.write(f'\t\\begin{{longtable}}{{|l|{metrics_cols}|}}\n')
        table_head = score_table_header(metrics, scores)
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
        tex_table_file.write(f'\t\t\\endlastfoot\n')
        tex_table_file.write('\n')


def add_score_table_line(tex_path, data=[], highscores=[]):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write(f'\t\t{" & ".join(score_data_formatted(data, highscores))} {eol}\n')


def close_score_table(tex_path, caption='', label=''):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write(f'\t\t\\hline\n')
        tex_table_file.write(f'\t\t\\caption{{{caption}}}\n')
        tex_table_file.write(f'\t\t\\label{{tab:{label}}}\n')
        tex_table_file.write(f'\t\\end{{longtable}}\n')
        tex_table_file.write('}}\n')


def score_table_header(metrics=[], scores=[]):
    header = '\t\t\hline\n'
    header += f'\t\t& \\multicolumn{{{len(metrics) * len(scores)}}}{{c|}}{{Algorithms}} {eol}\n'
    
    metrics_header = '\t\t'
    for metric in metrics:
        metrics_header += f'& \\multicolumn{{{len(scores)}}}{{c|}}{{{metric}}} '
    
    header += f'{metrics_header}{eol}\n'
    
    short_scores = []
    for score in scores:
        short_scores.append(label_formatted(score))
        
    header += f'\t\tDatasets & {" & ".join(short_scores * len(metrics))} {eol}\n'
    header += '\t\t\\hline\n'
    return header


def score_data_formatted(data, highscores=[]):
    pattern = "%.4f"
    result = [data.pop(0)]
    for index, datum in enumerate(data):
        if datum == highscores[index % len(highscores)]:
            result.append(f'$\\boldsymbol{{{pattern % datum}}}$')
        else:
            result.append(f'${pattern % datum}$')     
    return result


############################# 
#                           #
#    details table methods  #
#                           #
#############################
    
def open_details_table(tex_path, properties=[]):
    tex_path = Path(tex_path)
    property_columns = len(properties)
    with open(tex_path, 'w') as tex_table_file:
        tex_table_file.write(f'% {timestamp()}\n')
        tex_table_file.write('{{\\tiny\n')
        # construct the columns
        names = properties[:2]
        del properties[:2]
        property_cols_count = len(properties)
        name_cols_count = len(names)
        all_cols_count = name_cols_count + property_cols_count
        properties_cols = f'|{"r" * property_cols_count}|'
        tex_table_file.write(f'\t\\begin{{longtable}}{{|ll{properties_cols}}}\n')
        table_head = details_table_header(names, properties)
        # endfirsthead
        tex_table_file.write('\n')
        tex_table_file.write(table_head)
        tex_table_file.write(f'\t\t\\endfirsthead\n')
        #endhead
        tex_table_file.write('\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{all_cols_count}}}{{c}}{{\\bfseries \\tablename \\thetable{{}}, .. continued from previous page}} {eol}\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{all_cols_count}}}{{c}}{{}} {eol}\n')
        tex_table_file.write(table_head)
        tex_table_file.write(f'\t\t\\endhead\n')
        # endfoot
        tex_table_file.write('\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{all_cols_count}}}{{c}}{{}} {eol}\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{all_cols_count}}}{{c}}{{\\bfseries  .. continued on next page}} {eol}\n')
        tex_table_file.write(f'\t\t\\endfoot\n')
        # endlastfoot
        tex_table_file.write('\n')
        tex_table_file.write(f'\t\t\\multicolumn{{{all_cols_count}}}{{c}}{{}} {eol}\n')
        tex_table_file.write(f'\t\t\\endlastfoot\n')
        tex_table_file.write('\n')


def add_details_table_line(tex_path, data=[]):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write(f'\t\t {" & ".join(details_data_formatted(data))} {eol}\n')


def close_details_table(tex_path, caption='', label=''):
    with open(tex_path, 'a') as tex_table_file:
        tex_table_file.write(f'\t\t\\hline\n')
        tex_table_file.write(f'\t\t\\caption{{{caption}}}\n')
        tex_table_file.write(f'\t\t\\label{{tab:{label}}}\n')
        tex_table_file.write(f'\t\\end{{longtable}}\n')
        tex_table_file.write('}}\n')


def details_table_header(names=[], properties=[]):
    header = '\t\t\\hline\n'
    header += f'\t\t\\multicolumn{{{len(names)}}}{{|c}}{{Datasets}} & \\multicolumn{{{len(properties)}}}{{|c|}}{{' \
             f'Properties}} {eol}\n'
    properties_header = f'\t\t{replace_keywords_capitalize(names[0])} & {replace_keywords_capitalize(names[1])} '
    for property in properties:
        properties_header += f'& {replace_keywords_capitalize(property)} '

    header += f'{properties_header}{eol}\n'
    header += '\t\t\\hline\n'
    return header


def replace_keywords_capitalize(property):
    # replace num_of_ and _count with # and always put at beginning
    # capitalize the rest
    keywords = ['num', 'of', 'count']
    count_prop = False
    # split string
    property_parts = property.split('_')
    for removable in keywords:
        if property_parts.count(removable):
            property_parts.remove(removable)
            count_prop = True
    if count_prop:
        property_parts.insert(0, '\\#')
    return ' '.join([pp.capitalize() for pp in property_parts])


def details_data_formatted(data):
    result = []
    for datum in data:
        str_datum = str(datum).replace('%', '\\%')
        result.append(str_datum)
    return result

def label_formatted(label=''):
    return label[:6]
