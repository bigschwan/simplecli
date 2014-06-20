__author__ = 'clarkmatthew'

import os
from simplecli.baseenv import BaseEnv


class Config():

    '''
    Intention of this class is to provide utilities around reading and writing
    CLI environment related configuration.
    '''
    def __init__(self, conf_path=None, env=None):
       self.env = env #should be of type baseenv for shared env vars in shell
       self.conf_path = None

    def _get_conf_path(self, conf_path=None):
        '''
        :param conf_path: string, full path to conf file.
        '''
        default = 'simplecli.conf'
        conf_path = conf_path or self.conf_path or \
                    getattr(self.env, 'conf_path', None)
        if conf_path:
            conf_path = os.path.expanduser(conf_path)
            if os.path.exists(conf_path):
                return conf_path
            else:
                self.eprint('Configuration file not found at:"{0}"'.
                            format(str(conf_path)))
                return None
        else:
            # Try local and then home dir for simplecli.conf file.
            conf_paths = [os.path.join(os.path.curdir, default),
                          os.path.join(os.path.expanduser('~'),default)]
            for conf_path in conf_paths:
                if os.path.exists(conf_path):
                    return conf_path
        return None


    def get_section(section):
        raise NotImplementedError()

    def get(section, value):
        raise NotImplementedError()
