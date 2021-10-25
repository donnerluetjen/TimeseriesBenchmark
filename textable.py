__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from texfile import TexFile


class TexTable(TexFile):
    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter=None,
                 caption='abstract table', label='abstract-table', sources=None):
        self.table_columns_formatter = table_columns_formatter
        self.payload_lines = []
        super().__init__(tex_path, 'longtable', sources, caption, label)
        if table_columns_formatter is None:
            raise ValueError('List of column formatters cannot be empty')
    
    def compile_file_lines(self):
        self.compile_header()
        self.compile_payload()
        self.compile_footer()

    def compile_header(self):
        table_columns_formatter = ''.join(self.table_columns_formatter)
        table_column_count = len([cf for cf in self.table_columns_formatter if cf != '|'])

        self.file_lines.append('{\\tiny')
        self.file_lines.append(f'\t\\begin{{{self.tex_object}}}{{{table_columns_formatter}}}')
        self.file_lines.append('')
        self.file_lines.extend(self.sub_header())
        self.file_lines.append(f'\t\t\\endfirsthead')
        # endhead
        self.file_lines.append('')
        column_content = '\\bfseries \\tablename \\thetable{}, .. continued from previous page'
        self.file_lines.append(f'\t\t\\multicolumn{{{table_column_count}}}{{c}}{{{column_content}}} {self.EOL}')
        self.file_lines.append(f'\t\t\\multicolumn{{{table_column_count}}}{{c}}{{}} {self.EOL}')
        self.file_lines.extend(self.sub_header())
        self.file_lines.append(f'\t\t\\endhead')
        # endfoot
        self.file_lines.append('')
        column_content = '\\bfseries  .. continued on next page'
        self.file_lines.append(f'\t\t\\multicolumn{{{table_column_count}}}{{c}}{{}} {self.EOL}')
        self.file_lines.append(f'\t\t\\multicolumn{{{table_column_count}}}{{c}}{{{column_content}}} {self.EOL}')
        self.file_lines.append(f'\t\t\\endfoot')
        # endlastfoot
        self.file_lines.append('')
        self.file_lines.append(f'\t\t\\multicolumn{{{table_column_count}}}{{c}}{{}} {self.EOL}')
        self.file_lines.append(f'\t\t\\endlastfoot')
        self.file_lines.append('')

    def sub_header(self):
        header = ['\t\t\\hline']
        header.append(f'\t\t\\multicolumn{{{3}}}{{c|}}{{Abstract Table}} {self.EOL}')
        header.append('\t\t\\hline')
        return header

    def compile_payload(self):
        self.file_lines.extend(self.payload_lines)
    
    def compile_footer(self):
        self.file_lines.append(f'\t\t\\hline')
        self.file_lines.append(f'\t\t\\caption{{{self.caption}}}')
        self.file_lines.append(f'\t\t\\label{{tab:{self.label}}}')
        self.file_lines.append(f'\t\\end{{longtable}}')
        self.file_lines.append('}')

    def add_line(self, data=None, bold=None):
        """
        :param data: list of data to be added
        :param bold: list that indicate which data to print bold
        :return: nothing
        """
        if data is None:
            raise ValueError('Data cannot be None.')
        formatted_data = self.format_data(data, bold)
        self.payload_lines.append(f'\t\t{" & ".join(formatted_data)} {self.EOL}')

    def format_data(self, data, bold=None):
        if bold is None:
            bold = [False for _ in data]
        result = []
        index_offset = 0
        for index, datum in enumerate(data):
            if isinstance(datum, str):
                result.append(datum if not bold[index] else f'\\textbf{{{datum}}}')
                index_offset += 1
            else:
                number_data = f'{self.float_format_pattern() % datum}'
                result.append(f'${number_data}$' if not bold[index] else f'$\\boldsymbol{{{number_data}}}$')
        return result

    def float_format_pattern(self):
        return "%.4f"

    def replace_keywords_capitalized(self, prop):
        # replace num_of_ and _count with # and always put at beginning
        # capitalize the rest
        count_prop = False
        # split string
        prop_parts = prop.split('_')
        for removable in self.replacements()['keywords']:
            if prop_parts.count(removable):
                prop_parts.remove(removable)
                count_prop = True
        if count_prop:
            prop_parts.insert(0, self.replacements()['replacement'])
        return ' '.join([pp.capitalize() for pp in prop_parts])

    def replacements(self):
        return {'keywords': [], 'replacement': ''}


class ScoreTexTable(TexTable):
    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter=None,
                 caption='abstract table', label='abstract-table',
                 metrics=None, scores=None, sources=None):
        """

        :param tex_path: string containing the tex file path
        :param table_columns_formatter: string containing the tex columns format
        :param caption: string containing the table caption
        :param label: string containing the table label, will be expanded to tab:<label>
        :param metrics: list containing the strings with metric names
        :param scores: list containing strings with score names
        """
        self.metrics = ['placeholder', 'metric'] if metrics is None else metrics
        self.scores = ['initialize', 'header', 'columns'] if scores is None else scores
        super().__init__(tex_path, table_columns_formatter, caption, label, sources)

    def sub_header(self):
        len_metrics = len(self.metrics)
        len_scores = len(self.scores)


        sub_header = ['\t\t\\hline']
        sub_header.append(f'\t\t& \\multicolumn{{{len_metrics * len_scores}}}{{c|}}{{Algorithms}} {self.EOL}')

        metrics_header = '\t\t'
        for metric in self.metrics:
            metrics_header += f'& \\multicolumn{{{len_scores}}}{{c|}}{{{self.header_translation(metric)}}} '

        sub_header.append(f'{metrics_header}{self.EOL}')

        capitalized_scores = [score.capitalize() for score in self.scores]

        sub_header.append(f'\t\tDatasets & {" & ".join(capitalized_scores * len_metrics)} {self.EOL}')
        sub_header.append('\t\t\\hline')
        return sub_header

    def header_translation(self, header=''):
        header_translations = {'dagdtw': 'DAGDTW (sect. \\ref{sct:dagdtw})',
                               'bagdtw': 'BAGDTW (sect. \\ref{sct:bagdtw})',
                               'dtw': 'DTW \\cite{bellman1959adaptive}',
                               'sdtw': 'SDTW \\cite{cuturi2017soft}',
                               'ddtw': 'DDTW \\cite{keogh2001derivative}',
                               'wdtw': 'WDTW \\cite{jeong2011weighted}',
                               'wddtw': 'WWDTW \\cite{jeong2011weighted}',
                               'agdtw_manhattan': 'Manhattan (sect. \\ref{sct:manhattan})',
                               'agdtw_euclidean': 'Manhattan (sect. \\ref{sct:manhattan})',
                               'agdtw_chebishev': 'Manhattan (sect. \\ref{sct:manhattan})',
                               'agdtw_minkowski': 'Manhattan (sect. \\ref{sct:manhattan})'}
        return header_translations[header]


class DetailsTexTable(TexTable):

    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter=None,
                 caption='abstract table', label='tab:abstract-table',
                 properties=None, sources=None):
        """

        :param tex_path: string containing the tex file path
        :param table_columns_formatter: string containing the tex columns format
        :param caption: string containing the table caption
        :param label: string containing the table label, will be expanded to tab:<label>
        :param properties: list containing strings with property names
        """
        self.properties = ['placeholder', 'properties'] if properties is None else properties
        super().__init__(tex_path, table_columns_formatter, caption, label, sources)

    def sub_header(self):
        len_names = 2  # Short Name and Name
        len_properties = len(self.properties) - len_names

        header = ['\t\t\\hline']
        names_header = f'\\multicolumn{{{len_names}}}{{|c}}{{Datasets}}'
        properties_header = f'\\multicolumn{{{len_properties}}}{{|c|}}{{Properties}}'
        header.append(f'\t\t{names_header} & {properties_header} {self.EOL}')

        props = [self.replace_keywords_capitalized(prop) for prop in self.properties]

        header.append(f'\t\t{" & ".join(props)} {self.EOL}')
        header.append('\t\t\\hline')
        return header

    def replacements(self):
        return {'keywords': ['num', 'of', 'count'], 'replacement': '\\#'}

    def format_details(self, data):
        result = []
        for index, datum in enumerate(data):
            str_datum = str(datum).replace('%', '\\%')
            if index > 1:
                str_datum = f'${str_datum}$'
            result.append(str_datum)
        return result


class ImbalanceTexTable(DetailsTexTable):

    def format_details(self, data):
        connector = ' - '
        number_formatted_data_strings_list = self.format_ratios(data[2])
        return data[:2] + [connector.join(number_formatted_data_strings_list)]

    def format_ratios(self, data):
        return [f'{x * 100:.0f}\\%' for x in data]
