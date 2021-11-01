__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from texfile import TexFile
import math
from formats_and_translations import header_translation


class TexPlots(TexFile):
    def __init__(self, tex_path='', x_label='x', y_label='y', sources=None, x_axis_log=False, y_axis_log=False):
        self.x_label = x_label
        self.y_label = y_label
        self.x_axis_log = x_axis_log
        self.y_axis_log = y_axis_log
        self.marks_only = ''  # or '[only marks]'
        self.data = {}
        self.plot_shifts = {}
        self.inline_tables = []
        self.inline_plots = []
        self.inline_legends = []
        super().__init__(tex_path, 'tikzpicture', sources)

    def compile_file_lines(self):
        self.set_x_shifts()
        self.compile_header()
        self.compile_inline_table_lines()
        self.compile_axis_header()
        self.compile_inline_plot_lines()
        self.compile_legend()
        self.compile_footer()

    def compile_header(self):
        self.file_lines.append('\\begin{tikzpicture}')

    def compile_axis_header(self):
        self.file_lines.append('\t\\begin{axis}[')
        self.file_lines.append('\t\ttable/col sep = comma,')
        if self.x_axis_log:
            self.file_lines.append('\t\txmode = log,')
        if self.y_axis_log:
            self.file_lines.append('\t\tymode = log,')
        self.file_lines.append(f'\t\txlabel = {{{self.x_label}}},')
        self.file_lines.append(f'\t\tylabel = {{{self.y_label}}},')
        self.file_lines.append('\t\tgrid = both,')
        self.file_lines.append('\t\tgrid style={line width=.2pt, draw=gray!10},')
        self.file_lines.append('\t\tmajor grid style={line width=.2pt,draw=gray!50},')
        self.file_lines.append('\t\tminor tick num=5,')
        self.file_lines.append('\t\tlegend cell align={left},')
        self.file_lines.append('\t\tlegend pos = south east,')
        self.file_lines.append('\t\tlegend style={nodes={scale=0.7, transform shape}},')
        self.file_lines.append('\t\tclip=false, % avoid clipping at edge of diagram')
        self.file_lines.append('\t\tnodes near coords, % print the value near node')
        self.file_lines.append('\t]')

    def compile_footer(self):
        self.file_lines.append('\t\\end{axis}')
        self.file_lines.append(f'\\end{{{self.tex_object}}}')

    def compatible_data_name(self, data_name):
        data_name_elements, *all_but_first_element = data_name.split('_')
        data_name_elements += ''.join([data_name_element.capitalize() for data_name_element in all_but_first_element])
        return data_name_elements

    def compile_inline_table_lines(self):
        for data_name in self.data.keys():
            self.file_lines.append('\t\\pgfplotstableread[col sep=comma]{%')
            for data_row in self.data[data_name]:
                self.file_lines.append('\t\t' + ', '.join(map(str, data_row)))
            self.file_lines.append(f'\t}}\\{self.compatible_data_name(data_name)}')

    def compile_inline_plot_lines(self):
        for data_name in self.data.keys():
            xshift = self.plot_shifts[data_name]
            inline_plot = f'\t\t\\addplot+ [every node/.append style={{xshift={xshift}pt}}] '
            inline_plot += f'{self.marks_only} table[ x index = {{0}}, ' \
                           f'y index = {{1}}]{{\\{self.compatible_data_name(data_name)}}};'
            self.file_lines.append(inline_plot)

    def compile_legend(self):
        for data_name in self.data.keys():
            self.file_lines.append(f'\t\t\\addlegendentry{{{header_translation(data_name)}}}')

    def add_data(self, data_name, data=None):
        if data is not None:
            self.data[data_name] = data

    def set_x_shifts(self):
        min_y_distance = .04
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

                if isinstance(self.data[data_to_shift][0][0], str):
                    continue
                if abs(comparing_data_y - data_to_shift_y) <= min_y_distance:
                    # for linear comparison
                    data_to_shift_x = math.log10(self.data[data_to_shift][0][0])
                    comparing_data_x = math.log10(self.data[comparing_data][0][0])
                    distance = data_to_shift_x - comparing_data_x

                    shift = int(max((min_x_distance - abs(distance)) / 2, 0) * shift_factor)
                    if shift:  # only if <> 0
                        self.plot_shifts[data_to_shift] = -shift if distance < 0 else shift


class TrendPlots(TexPlots):

    def compile_axis_header(self):
        super().compile_axis_header()
        self.file_lines.pop()  # remove closing bracket
        self.file_lines.append('\t\tpoint meta = explicit symbolic, % read printed value from separate column')
        self.file_lines.append('\t]')

    def compile_inline_plot_lines(self):
        omit_data_display_list = ['wdtw', 'wddtw', 'sdtw']
        for data_name in self.data.keys():
            xshift = self.plot_shifts[data_name]
            scale = 1
            xshift_offset = -10
            yshift = 0
            style = f'scale = {scale}, xshift = {xshift + xshift_offset}pt, yshift = {yshift}pt'
            inline_plot = f'\t\t\\addplot+ [every node/.append style={{{style}}}] '
            meta = f', meta = {{2}}' if data_name not in omit_data_display_list else ''
            inline_plot += f'{self.marks_only} table[ x index = {{0}}, y index = {{1}}{meta}]{{\\{data_name}}};'
            self.file_lines.append(inline_plot)


class CorrelationPlots(TexPlots):
    def __init__(self, tex_path='', x_label='x', y_label='y', xtick_labels=[], sources=None, x_axis_log=False, y_axis_log=False):
        self.xtick_labels = [] if not xtick_labels else xtick_labels
        super().__init__(tex_path, x_label, y_label, sources, x_axis_log, y_axis_log)

    def xticks(self):
        sample_list = self.data[list(self.data.keys())[0]]
        keys = [item[0] for item in sample_list]
        values = self.xtick_labels
        return dict(zip(keys, values))

    def yticks(self):
        values = self.data.keys()
        keys = range(1, len(values) + 1)
        result = dict(zip(keys, values))
        return result

    def compile_axis_header(self):
        self.file_lines.append('\t\\begin{axis}[')
        self.file_lines.append('\t\ttable/col sep = comma,')
        if self.x_axis_log:
            self.file_lines.append('\t\txmode = log,')
        if self.y_axis_log:
            self.file_lines.append('\t\tymode = log,')
        self.file_lines.append(f'\t\txlabel = {{{self.x_label}}},')
        self.file_lines.append(f'\t\tylabel = {{{self.y_label}}},')
        self.file_lines.append('\t\tgrid = both,')
        self.file_lines.append('\t\tgrid style={line width=.2pt, draw=gray!10},')
        self.file_lines.append('\t\tmajor grid style={line width=.2pt,draw=gray!50},')
        self.file_lines.append('\t\tminor tick num=5,')
        self.file_lines.append('\t\tytick = \\empty,')
        ytick_dict = self.yticks()
        ytick_keys = ytick_dict.keys()
        ytick_positions = [str(key) for key in ytick_keys]
        ytick_labels = [ytick_dict[key] for key in ytick_keys]
        self.file_lines.append(f'\t\textra y ticks = {{{", ".join(ytick_positions)}}},')
        self.file_lines.append(f'\t\textra y tick labels = {{{", ".join(ytick_labels)}}},')
        self.file_lines.append('\t\tclip=false, % avoid clipping at edge of diagram')
        # self.file_lines.append('\t\tnodes near coords, % print the value near node')
        self.file_lines.append('\t]')

    def compile_inline_plot_lines(self):
        omit_data_display_list = ['wdtw', 'wddtw', 'sdtw']
        for data_name in self.data.keys():
            xshift = self.plot_shifts[data_name]
            scale = 1
            xshift_offset = -10
            yshift = 0
            style = f'scale = {scale}, xshift = {xshift + xshift_offset}pt, yshift = {yshift}pt'
            inline_plot = f'\t\t\\addplot+ [every node/.append style={{{style}}}] '
            # meta = f', meta = {{2}}' if data_name not in omit_data_display_list else ''
            inline_plot += f'{self.marks_only} table[ x index = {{0}}, y index = {{1}}]{{\\{data_name}}};'
            self.file_lines.append(inline_plot)
            xtick_dict = self.xticks()
            xtick_values = list(xtick_dict.values())
            left = xtick_values[0]
            right = xtick_values[-1]
            data_name_index = list(self.yticks().values()).index(data_name)
            data_name_key = list(self.yticks().keys())[data_name_index]
            y = data_name_key
            help_line = f'\t\t\\draw[help lines, thick, dashed] ({left}, {y}) -- ({right}, {y});'
            self.file_lines.append(help_line)

    def compile_legend(self):
        pass


class CorrelationXStrPlots(CorrelationPlots):

    def set_x_shifts(self):
        for data_to_shift in self.data:
            self.plot_shifts[data_to_shift] = 0

    def xticks(self):
        values = self.xtick_labels
        keys = range(1, len(values) + 1)
        return dict(zip(keys, values))

    def compile_axis_header(self):
        self.file_lines.append('\t\\begin{axis}[')
        self.file_lines.append('\t\ttable/col sep = comma,')
        if self.x_axis_log:
            self.file_lines.append('\t\txmode = log,')
        if self.y_axis_log:
            self.file_lines.append('\t\tymode = log,')
        self.file_lines.append(f'\t\txlabel = {{{self.x_label}}},')
        self.file_lines.append(f'\t\tylabel = {{{self.y_label}}},')
        self.file_lines.append('\t\tgrid = both,')
        self.file_lines.append('\t\tgrid style={line width=.2pt, draw=gray!10},')
        self.file_lines.append('\t\tmajor grid style={line width=.2pt,draw=gray!50},')
        self.file_lines.append('\t\tminor tick num=5,')
        self.file_lines.append('\t\txtick = \\empty,')
        self.file_lines.append('\t\tytick = \\empty,')
        xtick_dict = self.xticks()
        xtick_keys = xtick_dict.keys()
        xtick_positions = [str(key) for key in xtick_keys]
        xtick_labels = [xtick_dict[key] for key in xtick_keys]
        self.file_lines.append(f'\t\textra x ticks = {{{", ".join(xtick_positions)}}},')
        self.file_lines.append(f'\t\textra x tick labels = {{{", ".join(xtick_labels)}}},')
        self.file_lines.append(f'\t\tx tick label style={{rotate=45,anchor=east}},')
        ytick_dict = self.yticks()
        ytick_keys = ytick_dict.keys()
        ytick_positions = [str(key) for key in ytick_keys]
        ytick_labels = [ytick_dict[key] for key in ytick_keys]
        self.file_lines.append(f'\t\textra y ticks = {{{", ".join(ytick_positions)}}},')
        self.file_lines.append(f'\t\textra y tick labels = {{{", ".join(ytick_labels)}}},')
        self.file_lines.append('\t\tclip=false, % avoid clipping at edge of diagram')
        # self.file_lines.append('\t\tnodes near coords, % print the value near node')
        self.file_lines.append('\t]')

    def compile_inline_plot_lines(self):
        omit_data_display_list = ['wdtw', 'wddtw', 'sdtw']
        for data_name in self.data.keys():
            xshift = self.plot_shifts[data_name]
            scale = 1
            xshift_offset = -10
            yshift = 0
            style = f'scale = {scale}, xshift = {xshift + xshift_offset}pt, yshift = {yshift}pt'
            inline_plot = f'\t\t\\addplot+ [every node/.append style={{{style}}}] '
            # meta = f', meta = {{2}}' if data_name not in omit_data_display_list else ''
            inline_plot += f'{self.marks_only} table[ x index = {{0}}, y index = {{1}}]{{\\{data_name}}};'
            self.file_lines.append(inline_plot)
            xtick_dict = self.xticks()
            xtick_keys = list(xtick_dict.keys())
            left = xtick_keys[0]
            right = xtick_keys[-1]
            data_name_index = list(self.yticks().values()).index(data_name)
            data_name_key = list(self.yticks().keys())[data_name_index]
            y = data_name_key
            help_line = f'\t\t\\draw[help lines, thick, dashed] ({left}, {y}) -- ({right}, {y});'
            self.file_lines.append(help_line)
