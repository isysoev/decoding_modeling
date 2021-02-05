# 11/8: managing the imports
# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# 11/8: For directory help:
# https://superuser.com/questions/717105/how-to-show-full-path-of-a-file-including-the-full-filename-in-mac-osx-terminal/1533160

import sys
import os
from os.path import join

def import_files():
    abs_code_path = '//'

    files_to_import = [
        '',
        'file_gen',
        'segmentation',
        'word_tools'
    ]

    for path in files_to_import:
        this_path = join(abs_code_path, path)
        sys.path.insert(1, this_path)