__author__ = 'clarkmatthew'

import os
import sys
import imp
import json
from namespace import Namespace
from pprint import pformat
from config import Config

class BaseEnv(Config):
    """
    The intention of this class is to hold environment variables which might be
    global to the tool, it's menus, and the command executed within.
    """
    def __init__(self,
                 config_path=None,
                 cli_config_file=None,
                 name='simplecli'):
        self.name = name
        self._config_blocks= Namespace()
        self.config_path = config_path or os.path.expanduser('~/.simplecli')
        self.config_file_path = cli_config_file or \
                                os.path.join(self.config_path,
                                            'simplecli.config')
        self.default_username = None
        self.default_password = None
        self.user_name = None
        self.debug = True
        self.history_file = os.path.join(self.config_path, 'history')
        self.page_break = True
        self.plugin_dir = None
        self.menu_instances = []
        self.default_input = sys.stdin # ie stdin
        self.default_output = sys.stdout # ie stdout or stderr
        self.default_error = sys.stderr #ie stderr
        self.prompt_method = None # define this method as a global way to
                               #  construct menu prompts
        self.path_delimeter = ">" # Used for constructing the default prompt
                              #  and displayed path string(s)

        self.load_config()
        self.load_plugin_menus()


    def get_config_block(self, block_name):
        return getattr(self._config_blocks, block_name, None)

    def add_config_block(self, block_name, configblock=None, force=False):
        assert block_name, 'block_name was not populated'
        block = getattr(self._config_blocks, block_name, None)
        if block and not force:
            raise AttributeError('Base env already has config section:"{0}", '
                                 'use force to replace this section'
                                 .format(block_name))
        if configblock:
            if isinstance(configblock ,dict):
                configblock = Namespace(newdict=configblock)
        else:
            configblock = Namespace()
        setattr(self._config_blocks, block_name, configblock)

    def save_config_block(self, config_block=None, path=None):
        config_block = config_block or self
        if not isinstance(config_block, Config):
            config_block = self.get_config_block(config_block)
            if not config_block:
                raise AttributeError('Save Failed. No Config block named:"{0}"'
                                     .format(config_block))
        path = path or self._config_file_path
        savefile = file(path,"w")
        with savefile:
            savefile.write(pformat(vars(self)))


    def save_all(self):
        for conf in vars(self._config_blocks):
            conf._save()

    def load_plugin_menus(self):
        self.plugin_menus = []
        plugin_dir = self.plugin_dir or os.path.curdir
        for file in os.listdir(plugin_dir):
            if (os.path.isfile(file) and file.startswith('menu')
                and file.endswith('.py')):
                full_path = os.path.join(plugin_dir, file)
                p_name = os.path.basename(file).rstrip('.py')
                plugmod = imp.load_source(p_name, full_path)
                menuclass = getattr(plugmod, 'menu_class', None)
                if not menuclass:
                    raise AttributeError('"{0}". Plugin conf does not have '
                                         'a "menu_class" attribute. See plugin'
                                         'example for info.'
                                         .format(full_path))
                plugin = menuclass(env=self)
                existing_menu = self.get_menu_by_class(plugin.__class__)
                if existing_menu:
                    raise RuntimeError('Duplicate Menu Classes found while'
                                       'loading plugins: class:"{0}", '
                                       'menu:"{1}", plugin:"{2}", file:"{3}"'
                                       .format(plugin.__class__,
                                               existing_menu.name,
                                               plugin.name,
                                               full_path))
                parent_menus =  getattr(plugmod, 'parent_menus', None)
                if parent_menus:
                    plugin._parents = parent_menus
                self.plugin_menus.append(plugin)

    def get_menu_by_class(self, menuclass, list=None):
        #clean up class from module prefix
        #menuclass = str(menuclass).split('.').pop()
        list = list or self.menu_instances
        for item in self.plugin_menus:
            if item.__class__ == menuclass:
                return item
        return None

    def get_formatted_conf(self, blocks=None):
        ret_buf = ""
        blocks = blocks or [self]
        if not isinstance(blocks, list):
            if str(blocks).upper() == 'ALL':
                blocks = vars(self._config_blocks)
            else:
                blocks = [blocks]
        for block in blocks:
            if not isinstance(block, Config):
                block = self.get_config_block(block)
                if not block:
                    raise ValueError('Could not find config for:' + str(block))
            ret_buf += pformat(vars(block))
        return ret_buf

    def get_config_diff(self, blocks=None):
        ret_buf = ""
        blocks = blocks or [self]
        if not isinstance(blocks, list):
            if str(blocks).upper() == 'ALL':
                blocks = vars(self._config_blocks)
            else:
                blocks = [blocks]
        for block in blocks:
            if not isinstance(block, Config):
                block = self.get_config_block(block)
                if not block:
                    raise ValueError('Could not find config for:' + str(block))
            ret_buf += "*************** {0} ***************".format(block.name)
            ret_buf += pformat(vars(block))
        return ret_buf


    def get_menu_by_name(self, name, list=None):
        list = list or self.menu_instances
        for menu in list:
            if menu.name == name:
                return menu
        return None

    def _get_plugins_for_parent(self, parent):
        plugins = []
        try:
            parent_class = parent.__class__.__name__
        except Exception as PE:
            print sys.stderr, ('Failed to get class for parent menu:"{0}", '
                              'err:"{1}"'.format(str(parent),str(PE)))
            parent_class = None
        parent_name = parent.name
        for menu in self.plugin_menus:
            for line in menu._parents:
                line = str(line)
                try:
                    parent_type, name = line.split(':')
                    if parent_type.lower() == 'class':
                        if name == parent_class:
                            plugins.append(menu)
                    elif parent_type.lower() == 'name':
                        if name == parent_name:
                            plugins.append(menu)
                    else:
                        raise ValueError()
                except ValueError as VE:
                    print sys.stderr, ('parent menus for plugins must be in '
                                       'the form of "type:value", where type '
                                       'can be either the string '
                                       '"class" or "name". Errored line:{0}'
                                       .format(line))
        return plugins














