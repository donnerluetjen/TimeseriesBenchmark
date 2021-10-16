__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

import time


class TexFile:
    EOL = '\\\\'
    CR = '\n'

    def __init__(self, tex_path='abstract_table.tex',
                 tex_object='dummy', caption='abstract file', label='abstract-file'):
        self.tex_path = tex_path
        self.tex_object = tex_object
        self.caption = caption
        self.label = label
        self.file_lines = self.timestamp()

    def compile_file_lines(self):
        pass

    def __del__(self):
        self.compile_file_lines()
        with open(self.tex_path, 'w') as tex_object:
            tex_object.write(self.CR.join(self.file_lines))

    def timestamp(self):
        class_name = self.__class__.__name__
        return [f'% This file is created by the python {class_name} class at {time.strftime("%Y-%m-%d %H:%M:%S")}.',
                '',
                ''
                ]
