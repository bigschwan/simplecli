__author__ = 'clarkmatthew'

import os
import sys
import imp

class BaseEnv():
    """
    The intention of this class is to hold environment variables which might be
    global to the tool, it's menus, and the command executed within.
    """
    def __init__(self):
        self.default_username = None
        self.default_password = None
        self.default_sshkey = None
        self.credpath = None
        self.config_file = None
        self.access_key = None
        self.secret_key = None
        self.account_id = None
        self.account_name = None
        self.user_name = None
        self.debug=True
        self.plugin_dir = None
        self.menu_instances = []
        self.default_input = None # ie stdin
        self.default_output = None # ie stdout or stderr
        self.prompt_method = None # define this method as a global way to
                                  #  construct menu prompts
        self.path_delimeter = ">" # Used for constructing the default prompt
                                  #  and displayed path string(s)
        self.load_plugin_menus()

    def read_config(self, path):
        print 'not implemented yet'

    def set_config(self, key, value):
        print 'not implemented yet'

    def create_config(self, path):
        print 'not implemented yet'

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














