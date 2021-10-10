__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2020 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from pathlib import Path
import time


def init_pgfplots_file(tex_path, title="", x_label='x', y_label='y',
                       data_path=None):
    tex_path = Path(tex_path)
    with open(tex_path, 'w') as pgf_file:
        pgf_file.write(f'%{timestamp()}\n')
        pgf_file.write('\\begin{tikzpicture}\n')
        pgf_file.write('\t\\begin{axis}[\n')
        pgf_file.write('\t\ttable/col sep = comma,\n')
        pgf_file.write('\t\txmode = log,\n')
        pgf_file.write(f'\t\txlabel = {{{x_label}}},\n')
        pgf_file.write(f'\t\tylabel = {{{y_label}}},\n')
        pgf_file.write('\t\tgrid = both,\n')
        pgf_file.write('\t\tgrid style={line width=.2pt, draw=gray!10},\n')
        pgf_file.write('\t\tmajor grid style={line width=.2pt,draw=gray!50},\n')
        pgf_file.write('\t\tminor tick num=5,\n')
        pgf_file.write('\t\tlegend cell align={left},\n')
        pgf_file.write('\t\tlegend pos = south east,\n')
        pgf_file.write('legend style={nodes={scale=0.7, transform shape}},\n')
        pgf_file.write('\t\tclip=false, % avoid clipping at edge of diagram\n')
        pgf_file.write('\t\tnodes near coords, % print the value near node\n')
        pgf_file.write('\t]\n')
        pgf_file.write('\t\\end{axis}\n')
        pgf_file.write('\\end{tikzpicture}\n')


def add_table(tex_path, table_name, table_data=[[]]):
    add_inline_table(tex_path, table_name, table_data)
    add_inline_plot(tex_path, table_name)


def add_inline_table(tex_path, table_name, table_data=[[]]):
    # build inline table
    inline_table = '\t\\pgfplotstableread[col sep=comma]{%\n'
    for table_row in table_data:
        inline_table += '\t\t' + ', '.join(map(str, table_row)) + '\n'
    inline_table += f'\t}}\\{table_name}\n'
    
    add_inline_data(tex_path, 'table', inline_table)


def add_inline_plot(tex_path, table_name, x_col=0, y_col=1):
    marks_only = '[only marks]'
    marks_only = ''
    inline_plot = f'\t\t\\addplot+ {marks_only} table[ x index = {{{x_col}}}, y index = {{{y_col}}}]{{\\{table_name}}};\n'
    inline_plot += f'\t\t\\addlegendentry{{{table_name}}}\n'
    add_inline_data(tex_path, 'plot', inline_plot)
    

def add_inline_data(tex_path, insertion_key, data):
    with open(tex_path, 'r') as pgf_file:
        pgf_lines = pgf_file.readlines()
    
    insertion_index = find_insertion_index_for(insertion_key, pgf_lines)
    pgf_lines.insert(insertion_index, data)
    pgf_contents = ''.join(pgf_lines)
    
    with open(tex_path, 'w') as pgf_file:
        pgf_file.write(pgf_contents)


def find_insertion_index_for(key, string_list):
    insertion_points_to_find = {'table': 'begin{axis}[', 'plot': 'end{axis}'}
    insertion_list = [s for s in string_list if insertion_points_to_find[key] in s]
    insertion_index = string_list.index(insertion_list[0])
    return string_list.index(insertion_list[0])


def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")