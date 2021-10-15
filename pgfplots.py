__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from pathlib import Path
import time
import math


class TexPlots:
    def __init__(self, tex_path='', caption='', x_label='x', y_label='y'):
        self.tex_path = Path(tex_path)
        self.caption = caption
        self.x_label = x_label
        self.y_label = y_label
        self.marks_only = ''  # or '[only marks]'
        self.data = {}
        self.plot_shifts = {}
        self.inline_tables = []
        self.inline_plots = []
        self.inline_legends = []

    def __del__(self):
        self.set_xshift()
        self.create_inline_table_list()
        self.create_inline_plot_list()
        self.create_inline_legend()
        with open(self.tex_path, 'w') as pgf_file:
            pgf_file.write(f'% This the {"/".join(self.tex_path.parts[-2:])} file.\n')
            pgf_file.write(f'% It was created by the python TexPlots class at {self.timestamp()}\n\n')
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

    def create_inline_table_list(self):
        for data_name in self.data.keys():
            inline_table = ['\t\\pgfplotstableread[col sep=comma]{%']
            for data_row in self.data[data_name]:
                inline_table.append('\t\t' + ', '.join(map(str, data_row)))
            inline_table.append(f'\t}}\\{data_name}')
            self.inline_tables.append(inline_table)

    def create_inline_plot_list(self):
        for data_name in self.data.keys():
            xshift = self.plot_shifts[data_name]
            inline_plot = f'\t\t\\addplot+ [every node/.append style={{xshift={xshift}pt}}] '
            inline_plot += f'{self.marks_only} table[ x index = {{0}}, y index = {{1}}]{{\\{data_name}}};'
            self.inline_plots.append([inline_plot])

    def create_inline_legend(self):
        for data_name in self.data.keys():
            legend = [f'\t\t\\addlegendentry{{{self.header_translation(data_name)}}}']
            self.inline_legends.append(legend)

    def add_data(self, data_name, data=None):
        if data is not None:
            self.data[data_name] = data

    def set_xshift(self):
        min_y_distance = .02
        min_x_distance = .5
        shift_factor = 30
        for data_to_shift in self.data:
            shift = 0
            self.plot_shifts[data_to_shift] = shift  # initialise xshift to 0
            for comparing_data in self.data:
                if comparing_data == data_to_shift:
                    continue  # ignore same entry

                # for easier reading
                data_to_shift_y = self.data[data_to_shift][0][1]
                comparing_data_y = self.data[comparing_data][0][1]

                if abs(comparing_data_y - data_to_shift_y) <= min_y_distance:
                    # for linear comparison
                    data_to_shift_x = math.log10(self.data[data_to_shift][0][0])
                    comparing_data_x = math.log10(self.data[comparing_data][0][0])
                    distance = data_to_shift_x - comparing_data_x

                    shift = int(max((min_x_distance - abs(distance)) / 2, 0) * shift_factor)
                    if shift:  # only if <> 0
                        self.plot_shifts[data_to_shift] = -shift if distance < 0 else shift

    def header_translation(self, header=''):
        header_translations = {'dagdtw': 'DAGDTW (sect. \\ref{sct:dagdtw})',
                               'agdtw': 'BAGDTW (sect. \\ref{sct:bagdtw})',
                               'dtw': 'DTW \\cite{bellman1959adaptive}',
                               'sdtw': 'SDTW \\cite{cuturi2017soft}',
                               'ddtw': 'DDTW \\cite{keogh2001derivative}',
                               'wdtw': 'WDTW \\cite{jeong2011weighted}',
                               'wddtw': 'WWDTW \\cite{jeong2011weighted}'}
        return header_translations[header]

    def timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")
