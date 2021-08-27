__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2020 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from pathlib import Path


def open_pgfplots_file(tex_path, title="", x_label='x', y_label='y',
                       data_path=None):
    tex_path = Path(tex_path)
    with open(tex_path, 'w') as pgf_file:
        pgf_file.write('\\begin{tikzpicture}\n')
        pgf_file.write('    \\begin{axis}[\n')
        pgf_file.write(f'        title = {title},\n')
        pgf_file.write('        xmode = log,\n')
        pgf_file.write(f'        xlabel = {{{x_label}}},\n')
        pgf_file.write(f'        ylabel = {{{y_label}}},\n')
        pgf_file.write('        grid = both,\n')
        pgf_file.write(
            '   	    grid style={line width=.2pt, draw=gray!10},\n')
        pgf_file.write('        major grid style='
                       '{line width=.2pt,draw=gray!50},\n')
        pgf_file.write('        minor tick num=5,\n')
        pgf_file.write('        legend style={\n')
        pgf_file.write('		    font={\\small},\n')
        pgf_file.write('        },\n')
        pgf_file.write('        legend cell align={left},\n')
        pgf_file.write('        legend pos = south east,\n')
        pgf_file.write(
            '        clip=false, % avoid clipping at edge of diagram\n')
        pgf_file.write(
            '        nodes near coords, % print the value near node\n')
        pgf_file.write('    ]\n')


def open_single_score_pgfplots_file(tex_path, title="", x_label='x',
                                    y_label='y',
                                    data_path=None):
    tex_path = Path(tex_path)
    with open(tex_path, 'w') as pgf_file:
        pgf_file.write(
            f'\\pgfplotstableread[col sep=comma] {{../'
            f'{data_path}}}\datatable\n')
        pgf_file.write('\\begin{tikzpicture}\n')
        pgf_file.write('    \\begin{axis}[\n')
        pgf_file.write(f'        title = {title},\n')
        pgf_file.write(f'        xtick = data,\n')
        pgf_file.write(
            f'        xticklabels from table={{\\datatable}}{{dataset}},\n')
        pgf_file.write(f'        xtick = data, %,\n')
        pgf_file.write(
            f'        x tick label style = {{rotate = 45, anchor = east}},\n')
        pgf_file.write(f'        xlabel = {{{x_label}}},\n')
        pgf_file.write(f'        ylabel = {{{y_label}}},\n')
        pgf_file.write('        grid = both,\n')
        pgf_file.write(
            '   	    grid style={line width=.2pt, draw=gray!10},\n')
        pgf_file.write('        major grid style='
                       '{line width=.2pt,draw=gray!50},\n')
        pgf_file.write('        minor tick num=5,\n')
        pgf_file.write('        legend style={\n')
        pgf_file.write('		    anchor = south,\n')
        pgf_file.write(
            '            at={(.52, .02)}, % x, y positions between 0 and 1 '
            'of diagram extension,\n')
        pgf_file.write('		    font={\\small},\n')
        pgf_file.write('        },')
        pgf_file.write('    ]\n')


def close_pgfplots_file(tex_path):
    with open(tex_path, 'a') as pgf_file:
        pgf_file.write('    \\end{axis}\n')
        pgf_file.write('\\end{tikzpicture}\n')


def addplot_line_to_pgfplots_file_for(tex_path, data_path, x_col=0, y_col=1):
    marks_only = '[only marks]'
    marks_only = ''
    with open(tex_path, 'a') as pgf_file:
        pgf_file.write(
            f'        \\addplot+ {marks_only}'
            f' table['
            f' col sep = comma,'
            f' x index = {{{x_col}}},'
            f' y index = {{{y_col}}}'
            f']'
            f'{{{data_path}}};\n')


def addplot_line_to_single_score_pgfplots_file_for(tex_path, data_path,
                                                   x_col=0, y_col=1):
    marks_only = '[only marks]'
    marks_only = ''
    with open(tex_path, 'a') as pgf_file:
        pgf_file.write(
            f'        \\addplot+ {marks_only}'
            f' table['
            f' col sep = comma,'
            f' x expr=\\coordindex,'
            f' y index = {{{y_col}}}'
            f']'
            f'{{{data_path}}};\n')


def add_legend_to_pgfplots_file(tex_path, legend):
    with open(tex_path, 'a') as pgf_file:
        pgf_file.write('        \legend{\n')
        for entry in legend:
            entry = entry.replace("_manhattan", "")
            pgf_file.write(f'           {entry},\n')
        pgf_file.write('        }\n')
