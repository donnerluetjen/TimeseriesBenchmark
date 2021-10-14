__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from pathlib import Path
import time

class TexPlots:
    def __init__(self, tex_path='', caption='', x_label='x', y_label='y'):
        self.tex_path = Path(tex_path)
        self.caption = caption
        self.x_label = x_label
        self.y_label = y_label
        self.marks_only = ''  # or '[only marks]'
        self.inline_tables = []
        self.inline_plots = []
        self.inline_legends = []

    def __del__(self):
        with open(self.tex_path, 'w') as pgf_file:
            pgf_file.write('% This file is created by the python TexPlots class.')
            pgf_file.write(f' It was created at {self.timestamp()}\n\n')
            pgf_file.write('\\begin{tikzpicture}\n')
            # generate inline tables
            pgf_file.write('\n'.join(['\n'.join(s) for s in self.inline_tables]) + '\n')
            pgf_file.write('\t\\begin{axis}[\n')
            pgf_file.write('\t\ttable/col sep = comma,\n')
            pgf_file.write('\t\txmode = log,\n')
            pgf_file.write(f'\t\txlabel = {{{self.x_label}}},\n')
            pgf_file.write(f'\t\tylabel = {{{self.y_label}}},\n')
            pgf_file.write('\t\tgrid = both,\n')
            pgf_file.write('\t\tgrid style={line width=.2pt, draw=gray!10},\n')
            pgf_file.write('\t\tmajor grid style={line width=.2pt,draw=gray!50},\n')
            pgf_file.write('\t\tminor tick num=5,\n')
            pgf_file.write('\t\tlegend cell align={left},\n')
            pgf_file.write('\t\tlegend pos = south east,\n')
            pgf_file.write('\t\tlegend style={nodes={scale=0.7, transform shape}},\n')
            pgf_file.write('\t\tclip=false, % avoid clipping at edge of diagram\n')
            pgf_file.write('\t\tnodes near coords, % print the value near node\n')
            pgf_file.write('\t]\n')
            # generate inline plots
            pgf_file.write('\n'.join(['\n'.join(s) for s in self.inline_plots]) + '\n')
            # generate inline legends
            pgf_file.write('\n'.join(['\n'.join(s) for s in self.inline_legends]) + '\n')
            pgf_file.write('\t\\end{axis}\n')
            pgf_file.write('\\end{tikzpicture}\n')

    def add_data(self, data_name, data=None):
        if data is not None:
            # write table entry
            inline_table = ['\t\\pgfplotstableread[col sep=comma]{%']
            for data_row in data:
                inline_table.append('\t\t' + ', '.join(map(str, data_row)))
            inline_table.append(f'\t}}\\{data_name}')
            self.inline_tables.append(inline_table)
            # generate line for plot
            self.plot_line(data_name)

    def plot_line(self, plot_entry):
        inline_plot = [f'\t\t\\addplot+ {self.marks_only} table[ x index = {{0}}, y index = {{1}}]{{\\{plot_entry}}};']
        self.inline_plots.append(inline_plot)
        legend = [f'\t\t\\addlegendentry{{{plot_entry}}}']
        self.inline_legends.append(legend)

    def timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")
