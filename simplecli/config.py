__author__ = 'clarkmatthew'

from collections import OrderedDict
import os
from namespace import Namespace
import json
from pprint import pformat
import difflib
import pickle


class Config(Namespace):

    '''
    Intention of this class is to provide utilities around reading and writing
    CLI environment related configuration.
    '''
    def __init__(self,
                 config_file_path,
                 name=None,
                 default_dict=None):
        #Create instance attributes from provided dict...
        super(Config, self).__init__(newdict=default_dict)
        self.name = name or getattr(self, 'name', None)
        if not self.name:
            raise AttributeError('Need to specify config name, or provide '
                                 'name in default dict')
        self.config_file_path = config_file_path
        self.name = name or os.path.basename(self.config_file_path).split('.')[0]
        self._update_from_file()

    def _update_from_pickle_file(self, file_path=None):
        file_path = file_path or self.config_file_path
        if os.path.exists(file_path) and os.path.getsize(file_path):
            if not os.path.isfile(file_path):
                raise ValueError('config file exists at path and is not '
                                 'a file:' + str(file_path))
            loadfile = open(file_path, 'rb')
            with loadfile:
                newobj = pickle.load(file=loadfile)
            self.__dict__.update(newobj.__dict__)


    def _update_from_file(self, file_path=None):
        file_path = file_path or self.config_file_path
        newdict = self._get_dict_from_file(file_path=file_path)
        if newdict:
            self.__dict__.update(newdict)

    def _get_dict_from_file(self, file_path=None):
        newdict = None
        file_path = file_path or self.config_file_path
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

    def _diff(self, file_path=None):
        '''
        Method to show current values vs those (saved) in a file.
        Will return a formatted string to show the difference
        '''
        #Create formatted string representation of dict values
        self_dict = OrderedDict(sorted(vars(self).items()))
        text1 = json.dumps(self_dict, indent=4).splitlines()
        #Create formatted string representation of values in file
        file_path = file_path or self.config_file_path
        file_dict = self._get_dict_from_file(file_path=file_path) or {}
        file_dict = OrderedDict(sorted(file_dict.items()))
        text2 = json.dumps(file_dict, indent=4).splitlines()
        diff = difflib.unified_diff(text1, text2, lineterm='')
        return '\n'.join(diff)

    def _get_formatted_conf(self):
        return pformat(vars(self))

    def _get_formatted_conf_from_file(self):
        if self.config_file_path:
            dict = self._get_dict_from_file(self.config_file_path)
            return pformat(dict)

    def _save_pickle(self, path=None):
        path = path or self.config_file_path
        savefile = open(path, 'wb')
        with savefile:
            pickle.dump(self, file=savefile, protocol=2)

    def _save(self, path=None):
        path = path or self.config_file_path
        config_json = json.dumps(vars(self), indent=4)
        savefile = file(path,"w")
        with savefile:
            savefile.write(config_json)
            savefile.flush()










