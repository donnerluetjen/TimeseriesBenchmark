__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2020 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from pathlib import Path
import time


class TexTable:
    
    EOL = '\\\\'
    
    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter='lll', caption='abstract table', label='tab:abstract-table'):
        """
            this method opens the tex file for writing and sets up the table head
            :param tex_path: string containing the path to the desired tex file
            :param table_column: string containing the tex formatting for the table columns (eg. '|ll|cccc|')
        """
        self.table_columns_formatter = table_columns_formatter
        self.tex_path = Path(tex_path)
        self.caption = caption
        self.label = label
        self.table_column_count = len(self.table_columns_formatter.replace('|', ''))
        
        with open(self.tex_path, 'w') as tex_table:
            tex_table.write('% This file is created by the python textable class.')
            tex_table.write(f' It was created at {self.timestamp()}\n')
            tex_table.write(f'\t\\begin{{longtable}}{{{table_columns_formatter}}}\n')
            tex_table.write('\n')
            tex_table.write(self.table_header())
            tex_table.write(f'\t\t\\endfirsthead\n')
            #endhead
            tex_table.write('\n')
            tex_table.write(f'\t\t\\multicolumn{{{self.table_column_count}}}{{c}}{{\\bfseries \\tablename \\thetable{{}}, .. continued from previous page}} {self.EOL}\n')
            tex_table.write(f'\t\t\\multicolumn{{{self.table_column_count}}}{{c}}{{}} {self.EOL}\n')
            tex_table.write(self.table_header())
            tex_table.write(f'\t\t\\endhead\n')
            # endfoot
            tex_table.write('\n')
            tex_table.write(f'\t\t\\multicolumn{{{self.table_column_count}}}{{c}}{{}} {self.EOL}\n')
            tex_table.write(f'\t\t\\multicolumn{{{self.table_column_count}}}{{c}}{{\\bfseries  .. continued on next page}} {self.EOL}\n')
            tex_table.write(f'\t\t\\endfoot\n')
            # endlastfoot
            tex_table.write('\n')
            tex_table.write(f'\t\t\\multicolumn{{{self.table_column_count}}}{{c}}{{}} {self.EOL}\n')
            tex_table.write(f'\t\t\\endlastfoot\n')
            tex_table.write('\n')
    
    def __del__(self):
        """
            this function opens the tex file for writing and writes the table ending
        """
        with open(self.tex_path, 'a') as tex_table:
            tex_table.write(f'\t\t\\hline\n')
            tex_table.write(f'\t\t\\caption{{{self.caption}}}\n')
            tex_table.write(f'\t\t\\label{{tab:{self.label}}}\n')
            tex_table.write(f'\t\\end{{longtable}}\n')
            tex_table.write('}}\n')
    
    def table_header(self):
        header = '\t\t\hline\n'
        header += f'\t\t\\multicolumn{{{self.table_column_count}}}{{c|}}{{Abstract Table}} {self.EOL}\n'
        header += '\t\t\\hline\n'
        return header

    def add_line(self, data=['An', 'abstract', 'table']):
        with open(self.tex_path, 'a') as tex_table:
            tex_table.write(f'\t\t{" & ".join(data)} {self.EOL}\n')

    def format_data(self, data, highscores=[]):
        result = []
        index_offset = 0
        for index, datum in enumerate(data):
            if isinstance(datum, str):
                result.append(datum)
                index_offset += 1
            else:
                if datum == highscores[(index - index_offset) % len(highscores)]:
                    result.append(f'$\\boldsymbol{{{self.float_format_pattern() % datum}}}$')
                else:
                    result.append(f'${self.float_format_pattern() % datum}$')
        return result

    def float_format_pattern(self):
        return "%.4f"

    def replace_keywords_capitalize(self, prop):
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

    def timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")


class ScoreTexTable(TexTable):
    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter='lcccccc',
                 caption='abstract table', label='tab:abstract-table',
                 metrics=['placeholder', 'metric'], scores=['initialize', 'header', 'columns']):
        self.metrics = metrics
        self.scores = scores
        super().__init__(tex_path, table_columns_formatter, caption, label)

    def table_header(self):
        len_metrics = len(self.metrics)
        len_scores = len(self.scores)

        header = '\t\t\hline\n'
        header += f'\t\t& \\multicolumn{{{len_metrics * len_scores}}}{{c|}}{{Algorithms}} {eol}\n'

        metrics_header = '\t\t'
        for metric in self.metrics:
            metrics_header += f'& \\multicolumn{{{len_scores}}}{{c|}}{{{metric}}} '

        header += f'{metrics_header}{eol}\n'

        capitalized_scores = [score.capitalize() for score in self.scores]

        header += f'\t\tDatasets & {" & ".join(capitalized_scores * len_metrics)} {eol}\n'
        header += '\t\t\\hline\n'
        return header


class DetailsTexTable(TexTable):

    def __init__(self, tex_path='abstract_table.tex', table_columns_formatter='lcccccc',
                 caption='abstract table', label='tab:abstract-table',
                 properties=['placeholder', 'properties']):
        self.properties = properties
        super().__init__(tex_path, table_columns_formatter, caption, label)

    def table_header(self):
        len_names = 2  # Short Name and Name
        len_properties = len(self.properties) - len_names

        header = '\t\t\hline\n'
        names_header = f'\\multicolumn{{{len_names}}}{{|c}}{{Datasets}}'
        properties_header = f'\\multicolumn{{{len_properties}}}{{|c|}}{{Properties}}'
        header += f'\t\t{names_header} & {properties_header} {self.EOL}\n'

        props = [self.replace_keywords_capitalize(prop) for prop in self.properties]

        header += f'\t\t{" & ".join(props)} {self.EOL}\n'
        header += '\t\t\\hline\n'
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
