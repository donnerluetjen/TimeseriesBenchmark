__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from formats_and_translations import header_translation, float_format_pattern, format_ratios
from texfile import TexFile


class TexTable(TexFile):
    """
        This class provides the basic functionality to write a tex file
        describing a table
    """
    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter=None,
                 caption='abstract table', label='abstract-table', sources=None):
        """
        :param tex_path: string containing the tex file path
        :param table_columns_formatter: string containing the tex columns format
        :param caption: string containing the table caption
        :param label: string containing the table label, will be expanded to tab:<label>
        :param sources: list containing files with source data
        """
        self.table_columns_formatter = table_columns_formatter
        self.payload_lines = []
        super().__init__(tex_path, 'table', sources, caption, label)
        if table_columns_formatter is None:
            raise ValueError('List of column formatters cannot be empty')
    
    def compile_file_lines(self):
        """
        compiles the tex file
        :return: nothing
        """
        self.compile_header()
        self.compile_payload()
        self.compile_footer()

    def compile_header(self):
        """
        stores the header part of the table structure
        :return: nothing
        """
        table_columns_formatter = ''.join(self.table_columns_formatter)
        table_column_count = len([cf for cf in self.table_columns_formatter if cf != '|'])

        self.file_lines.append('{\\tiny')
        self.file_lines.append(f'\t\\begin{{{self.tex_object}}}')
        self.file_lines.append(f'\t\t\\begin{{tabular}}{{{table_columns_formatter}}}')
        self.file_lines.append('')
        self.file_lines.extend(self.sub_header())
        self.file_lines.append('')

    def sub_header(self):
        """
        stores details for the column headers
        :return: nothing
        """
        header = ['\t\t\\hline']
        header.append(f'\t\t\t\\multicolumn{{{3}}}{{c|}}{{Abstract Table}} {self.EOL}')
        header.append('\t\t\t\\hline')
        return header

    def compile_payload(self):
        """
        stores the data
        :return: nothing
        """
        self.file_lines.extend(self.payload_lines)

    def compile_footer(self):
        """
        stores the footer structure for the table
        :return: nothing
        """
        self.file_lines.append(f'\t\t\t\\hline')
        self.file_lines.append(f'\t\t\\end{{tabular}}')
        self.file_lines.append(f'\t\t\\caption{{{self.caption}}}')
        self.file_lines.append(f'\t\t\\label{{tab:{self.label}}}')
        self.file_lines.append(f'\t\\end{{{self.tex_object}}}')
        self.file_lines.append('}')

    def add_line(self, data=None, bold=None):
        """
        :param data: list of data to be added
        :param bold: list that indicates which data to print bold
        :return: nothing
        """
        if data is None:
            raise ValueError('Data cannot be None.')
        formatted_data = self.format_data(data, bold)
        self.payload_lines.append(f'\t\t\t{" & ".join(formatted_data)} {self.EOL}')

    def format_data(self, data, bold=None):
        """
        generates the data entries for the tex file and
        respects bold requirement
        :param data: a list of data
        :param bold: a list of boolean,
                     true indicates corresponding data should be in bold
        :return: a string containing the generated data line
        """
        if bold is None:
            bold = [False for _ in data]
        result = []
        index_offset = 0
        for index, datum in enumerate(data):
            if isinstance(datum, str):
                result.append(datum if not bold[index] else f'\\textbf{{{datum}}}')
                index_offset += 1
            else:
                number_data = f'{float_format_pattern() % datum}'
                result.append(f'${number_data}$' if not bold[index] else f'$\\boldsymbol{{{number_data}}}$')
        return result

    def replace_keywords_capitalized(self, prop):
        """
        replace num_of_ and _count with # and always put at beginning and
        capitalize the rest
        :param prop: a string holding a property name
        :return: the formatted string
        """
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
        """
        returning a replacement string for a given keyword
        :return: the replacement string
        """
        return {'keywords': [], 'replacement': ''}


class LongTexTable(TexTable):
    """
        This class provides the basic functionality to write a tex file
        describing a longtable
    """
    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter=None,
                 caption='abstract table', label='abstract-table', sources=None):
        """
        :param tex_path: string containing the tex file path
        :param table_columns_formatter: string containing the tex columns format
        :param caption: string containing the table caption
        :param label: string containing the table label, will be expanded to tab:<label>
        :param sources: list containing files with source data
        """
        super().__init__(tex_path, table_columns_formatter, caption, label, sources)
        self.tex_object = 'longtable'

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


class ScoreTexTable(LongTexTable):
    """
        This class is a specialization of the LongTexTable class
    """
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
        :param sources: list containing files with source data
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
            metrics_header += f'& \\multicolumn{{{len_scores}}}{{c|}}{{{header_translation(metric)}}} '

        sub_header.append(f'{metrics_header}{self.EOL}')

        capitalized_scores = [score.capitalize() for score in self.scores]

        sub_header.append(f'\t\tDatasets & {" & ".join(capitalized_scores * len_metrics)} {self.EOL}')
        sub_header.append('\t\t\\hline')
        return sub_header


class CorrelationTexTable(ScoreTexTable):
    """
        This class is a specialization of the ScoreTexTable class
    """
    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter=None,
                 caption='abstract table', label='abstract-table',
                 metrics=None, scores=None, correlation_property='', sources=None):
        """
        :param tex_path: string containing the tex file path
        :param table_columns_formatter: string containing the tex columns format
        :param caption: string containing the table caption
        :param label: string containing the table label, will be expanded to tab:<label>
        :param metrics: list containing the strings with metric names
        :param scores: list containing strings with score names
        :correlation_property: name of the property correlation is logged for
        :param sources: list containing files with source data
        """
        if correlation_property == '':
            raise ValueError('Correlation Property cannot be empty')
        else:
            self.correlation_property = correlation_property
        super().__init__(tex_path, table_columns_formatter, caption, label, metrics, scores, sources)

    def sub_header(self):
        len_metrics = len(self.metrics)
        len_scores = len(self.scores)


        sub_header = ['\t\t\\hline']
        sub_header.append(f'\t\t& & \\multicolumn{{{len_metrics * len_scores}}}{{c|}}{{Algorithms}} {self.EOL}')

        metrics_header = '\t\t& & ' + ' & '.join([header_translation(metric) for metric in self.metrics])

        sub_header.append(f'{metrics_header}{self.EOL}')

        capitalized_scores = [score.capitalize() for score in self.scores]

        sub_header.append(f'\t\t{self.correlation_property} & \# & {" & ".join(capitalized_scores * len_metrics)} {self.EOL}')
        sub_header.append('\t\t\\hline')
        return sub_header


class NormTexTable(LongTexTable):
    """
        This class is a specialization of the LongTexTable class
    """
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
        :param sources: list containing files with source data
        """
        self.metrics = ['placeholder', 'metric'] if metrics is None else metrics
        self.scores = ['initialize', 'header', 'columns'] if scores is None else scores
        super().__init__(tex_path, table_columns_formatter, caption, label, sources)

    def sub_header(self):
        len_metrics = len(self.metrics)
        len_scores = len(self.scores)


        sub_header = ['\t\t\t\\hline']
        sub_header.append(f'\t\t\t& \\multicolumn{{{len_metrics * len_scores}}}{{c|}}{{Algorithms}} {self.EOL}')

        metrics_header = '\t\t\t'
        for metric in self.metrics:
            metrics_header += f'& \\multicolumn{{{len_scores}}}{{c|}}{{{header_translation(metric)}}} '

        sub_header.append(f'{metrics_header}{self.EOL}')

        capitalized_scores = [score.capitalize() for score in self.scores]

        sub_header.append(f'\t\t\tDatasets & {" & ".join(capitalized_scores * len_metrics)} {self.EOL}')
        sub_header.append('\t\t\t\\hline')
        return sub_header


class DetailsTexTable(LongTexTable):
    """
        This class is a specialization of the LongTexTable class
        for showing datastes details
    """
    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter=None,
                 caption='abstract table', label='tab:abstract-table',
                 properties=None, sources=None):
        """
        :param tex_path: string containing the tex file path
        :param table_columns_formatter: string containing the tex columns format
        :param caption: string containing the table caption
        :param label: string containing the table label, will be expanded to tab:<label>
        :param properties: list containing strings with property names
        :param sources: list containing files with source data
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
    """
        This class is a specialization of the DetailsTexTable class for showing
        imbalance ratios
    """

    def format_details(self, data):
        connector = ' - '
        number_formatted_data_strings_list = format_ratios(data[2])
        return data[:2] + [connector.join(number_formatted_data_strings_list)]
