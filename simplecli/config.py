__author__ = 'clarkmatthew'

import os
from simplecli.baseenv import BaseEnv
from namespace import Namespace
import json
from pprint import pformat
import difflib


class Config(Namespace):

    '''
    Intention of this class is to provide utilities around reading and writing
    CLI environment related configuration.
    '''
    def __init__(self,
                 name=None,
                 config_file_path=None,
                 default_dict=None):
        assert isinstance(env, BaseEnv), 'Must provide simplecli.BaseEnv ' \
                                         'type as env'
        #Create instance attributes from provided dict...
        super(Config, self).__init__(newdict=default_dict)
        self.env = env
        self.name = getattr(self, 'name', name)
        if not self.name:
            raise AttributeError('Need to specify config name, or provide '
                                 'name in default dict')
        _config_file_name = str(self.name) + ".conf"
        self._config_file_path = os.join(self.env.config_path,
                                         _config_file_name)


    def _update_from_file(self, file_path=None):
        newdict = self._get_dict_from_file(file_path=file_path)
        self.__dict__.update(newdict)

    def _get_dict_from_file(self, file_path=None):
        newdict = None
        file_path = file_path or self._config_file_path
        conf_file = file(file_path, "r+")
        with conf_file:
            data = file.read()
        if data:
            try:
                newdict = json.loads(data)
            except ValueError:
                print self.env.default_error, 'Failed to load json config ' \
                                              'from: "{0}"'.format(self._config_file)
                raise
        return newdict

    def _diff(self, dict=None, file_path=None):
        filedict = self._get_dict_from_file(file_path=file_path)
        file_dict = pformat(vars(filedict)).splitlines()
        self_dict = pformat(vars(self)).splitlines()
        diff = difflib.Differ()
        diff.compare(self_dict, filedict)
        return '\n'.join(diff)

    def _get_formatted_conf(self):
        return pformat(vars(self))

    def _save(self, path=None):
        path = path or self._config_file_path
        savefile = file(path,"w")
        with savefile:
            savefile.write(pformat(vars(self)))









