__author__ = 'clarkmatthew'
__version__ = '0.0.1'

import os
import json

def get_dict_from_file(file_path):
        newdict = None
        if os.path.exists(file_path) and os.path.getsize(file_path):
            if not os.path.isfile(file_path):
                raise ValueError('config file exists at path and is not '
                                 'a file:' + str(file_path))
            conf_file = open(file_path, 'rb')
            with conf_file:
                data = conf_file.read()
            if data:
                try:
                    newdict = json.loads(data)
                except ValueError as ve:
                    ve.args = (['Failed to load json config from: "{0}". '
                                'ERR: "{1}"'.format(file_path, ve.message)])
                    raise
        return newdict