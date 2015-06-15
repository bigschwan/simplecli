__author__ = 'clarkmatthew'

import difflib
import os
import sys
import imp
from namespace import Namespace
from simplecli import get_dict_from_file
from config import Config
from shutil import copyfile
import json


class BaseEnv():
    """
    The intention of this class is to hold environment variables which might be
    global to the tool, it's menus, and the command executed within.
    """
    def __init__(self,
                 base_dir=None,
                 name='simplecli'):
        self.name = name
        self._config_namespaces = Namespace()
        self.menu_instances = []
        self.base_dir = base_dir or os.path.expanduser('~/.simplecli')
        if os.path.exists(self.base_dir):
            if not os.path.isdir(self.base_dir):
                raise ValueError('base dir provided is not a dir:"{0}'
                                 .format(self.base_dir))
        else:
            os.makedirs(self.base_dir)
        self.simplecli_config_file = os.path.join(self.base_dir,
                                                  str(name) + '.config')
        self.simplecli_config = None
        self.init_simplecli_config()
        self._setup_stdio()
        self._load_plugin_menus()


    def _setup_stdio(self):
        def _get_stdio(name):
            if hasattr(sys, name):
                return getattr(sys, name)
            else:
                return open(name, 'wa')
        if self.simplecli_config.default_input:
            self.default_input = _get_stdio(
                self.simplecli_config.default_input)
        else:
            self.default_input = sys.stdin
        if self.simplecli_config.default_output:
            self.default_output = _get_stdio(
                self.simplecli_config.default_output)
        else:
            self.default_output = sys.stdout
        if self.simplecli_config.default_error:
            self.default_error = _get_stdio(
                self.simplecli_config.default_error)
        else:
            self.default_error = sys.stderr



    def init_simplecli_config(self):
        simplecli = Config(config_file_path=self.simplecli_config_file,
                           name='simplecli')
        simplecli.debug = False
        simplecli.history_file = os.path.join(self.base_dir, 'history')
        simplecli.page_break = True
        simplecli.plugin_dir = None

        simplecli.default_input = 'stdin' # ie stdin
        simplecli.default_output = 'stdout' # ie stdout or stderr
        simplecli.default_error = 'stderr' # ie stderr
        simplecli.prompt_method = None # define this method as a global way to
                                       # construct menu prompts
        simplecli.path_delimeter = ">" # Used for constructing the default
                                       # prompt and displayed path string(s)
        simplecli._update_from_file(markers=['main'])
        self.add_config_to_namespace(namespace_name='main',
                                     config=simplecli,
                                     create=True)
        # Assign to local var for easy access as well
        self.simplecli_config = simplecli

    def add_namespace(self, name):
        '''
        Adds a blank configuration namespace using 'name' to the
        local _config_namespaces list.
        Raises ValueError if the name already exists
        Returns the new namespace object
        '''
        if getattr(self._config_namespaces, name, None):
            raise ValueError('Config Namespace already exists for:"{0}"'
                             .format(name))
        newnamespace = Namespace()
        setattr(self._config_namespaces, name, newnamespace)
        return newnamespace

    def get_namespace(self, name, create=False):
        '''
        Will retrieve an existing namespace object of 'name' if found.
        If not found and 'create == True' then a new namespace obj will be
        created, added to self._config_namespaces and returned.
        '''
        if not isinstance(name, basestring):
            raise ValueError('Bad value passed for "name" to get_namespace, got:"{0}/{1}"'
                             .format(name, type(name)))
        namespace = getattr(self._config_namespaces, name, None)
        if not namespace and create:
            namespace = self.add_namespace(name)
        return namespace

    def get_config_from_namespace(self, config_name, namespace_name):
        '''
        Attempts to get a config object from the specified namespace
        :param config_name: string, name of Config to fetch
        :param namespace_name: string, name of namespace to fetch config from
        returns Config obj
        '''
        assert isinstance(namespace_name, str), 'Expected String for ' \
                                                'namespace name'
        context = self.get_namespace(namespace_name)
        if not context:
            raise ValueError('Namespace does not exist:' +str(namespace_name))
        return getattr(context, config_name, None)

    def add_config_to_namespace(self,
                              namespace_name,
                              config, 
                              force=False,
                              create=False):
        '''
        Attempts to add a config object to the specified namespace
        :param namespace_name: string, name of namespace to fetch config from
        :param config: Config() obj to add to namespace named 'namespace_name'
        :param force: boolean, will replace existing config block in namespace
        :param create: bollean, will create namespace if it does not exist
        '''
        assert  isinstance(namespace_name, str)
        context = self.get_namespace(namespace_name, create=create)
        assert config.name, 'block_name was not populated'
        if getattr(context, config.name, None) and not force:
            raise AttributeError('Base env already has config at context:'
                                 '"{0}", name:"{1}" use force to replace '
                                 'this section'.format(namespace_name,
                                                       config.name))
        setattr(context, config.name, config)

    def save_config(self, path=None):
        path = path or self.simplecli_config_file
        backup_path = path + '.bak'
        config_json = self._config_namespaces._to_json()
        if os.path.isfile(path):
            copyfile(path, backup_path)
        save_file = file(path, "w")
        with save_file:
            save_file.write(config_json)
            save_file.flush()

    def _load_plugin_menus(self):
        '''
        Loads plugin menus found either in the provided plugin directory
        or the current working dir. Will attempt to load files starting
        with 'menu'. See plugin examples for more info.
        '''
        self.plugin_menus = []
        plugin_dir = self.simplecli_config.plugin_dir or os.path.curdir
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
        '''
        Returns a loaded menu instance matching the provided class.
        '''
        list = list or self.menu_instances
        for item in self.menu_instances:
            if item.__class__ == menuclass:
                return item
        return None

    def get_formatted_conf(self, block=None):
        '''
        Returns a json representation of the current configuration.
        '''
        ret_buf = ""
        if not block:
            namespace = self._config_namespaces
        else:
            namespace = self.get_namespace(block, create=False)
        if namespace:
            ret_buf = namespace._to_json()
        return ret_buf

    def get_config_diff(self, file_path=None):
        '''
        Method to show current values vs those (saved) in a file.
        Will return a formatted string to show the difference
        '''
        #Create formatted string representation of dict values
        text1 = self._config_namespaces._to_json().splitlines()
        #Create formatted string representation of values in file
        file_path = file_path or self.simplecli_config_file
        file_dict = get_dict_from_file(file_path=file_path) or {}
        text2 = json.dumps(file_dict, sort_keys=True, indent=4).splitlines()
        diff = difflib.unified_diff(text2, text1, lineterm='')
        return '\n'.join(diff)

    def get_menu_by_name(self, name, list=None):
        list = list or self.menu_instances
        for menu in list:
            if menu.name == name:
                return menu
        return None

    def _get_plugins_for_parent(self, parent):
        '''
        convience method to find and return plugin menus to be loaded under
        the provided 'parent' menu.
        '''
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














