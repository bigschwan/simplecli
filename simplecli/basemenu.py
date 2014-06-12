import os
import sys
from cmd import Cmd
from traceback import print_exc
from simplecli.baseenv import BaseEnv
from argparse import ArgumentError
from inspect import isclass

class BaseMenu(Cmd):
    # This must define for subclasses of BaseMenu
    name = None
    # _submenus is a list of BaseMenu types which will be accessible through
    # this menu's context
    _submenus = []
    # _summary is a brief single string summary used in help menus
    _summary = None
    #_description is buffer used for more detailed help menus
    _description = None
    #_info is the message printed when this menu is loaded
    _intro = None

    def __init__(self,
                 env,
                 path_from_home=None,
                 completekey='tab',
                 prompt_method=None,
                 path_delimeter=None,
                 stdin=None,
                 stdout=None,
                 stderr=None):
        # Note super does not work as Cmd() is an 'old style' class which
        # does not inherit from object(). Instead call init directly.
        # super(BaseMenu, self).__init__(completekey=completekey,
        #                                stdin=stdin,
        #                                stdout=stdout)
        Cmd.__init__(self, completekey=completekey, stdin=stdin, stdout=stdout)
        if not self.name:
            raise ValueError('Class must define "name"')
        if stderr is None:
            self.stderr = sys.stderr
        else:
            self.stderr = stderr
        assert isinstance(env, BaseEnv), "env variable must be of type BaseEnv"
        self.env = env
        self.prompt_method = prompt_method or env.prompt_method
        self.path_delimeter = path_delimeter or env.path_delimeter
        self.path_from_home = path_from_home or []
        if not self.path_from_home or self.path_from_home[-1] != self:
            self.path_from_home.append(self)
        self.path = (str(self.path_delimeter)
                     .join(str(x.name) for x in self.path_from_home))
        self._init_submenus()

    @property
    def prompt(self):
        if not self.prompt_method:
            return  str(self.path) + "#"
        else:
            return self.prompt_method()

    @property
    def summary(self):
        summary = self._summary or "LOADS {0} MENU".format(self.name)
        return str(summary)

    @property
    def description(self):
        description = self._description or "{0} MENU".format(self.name)
        return str(description)

    @property
    def intro(self):
        intro = self._intro or "*** {0} ***".format(self.name)
        return intro

    def _init_submenus(self, menus=None):
        menus = menus or self._submenus
        for menu in menus:
            try:
                if isinstance(menu, BaseMenu) or issubclass(menu, BaseMenu):
                    self._add_sub_menu(menu)
                else:
                    raise AttributeError('Init sub-menu error, item must be '
                                         'of type BaseMenu')
            except Exception as ME:
                if self.env.debug:
                    print_exc(file=self.stderr)
                mname = str(menu)
                self.eprint('Error loading submenu "{0}", err:{1}\n'
                            .format(mname,
                                    str(ME)))

    def get_names(self):
        names = dir(self.__class__)
        for key in self.__dict__:
            if not key in names:
                names.append(key)
        return names

    def _add_doc_string(value):
        def _doc(func):
            func.__doc__ = value
            return func
        return _doc

    def _add_sub_menu(self, menu, description=None):
        assert isinstance(menu, BaseMenu) or issubclass(menu, BaseMenu), \
            'Error adding sub menu, item is not BaseMenu type'
        method_name = 'do_' + menu.name
        newfunc = lambda args: self._load_menu(menu)
        setattr(self, method_name, newfunc)
        new_method = getattr(self, method_name)
        new_method.__doc__ = description or menu._summary or ""
        new_method.__submenu__ = True

    @_add_doc_string(Cmd.do_help.im_func.func_doc)
    def do_help(self, arg):
        Cmd.do_help(self, arg)
        if not arg:
            self.menu_summary(arg)

    def oprint(self, buf):
        self.stdout.write(str(buf).rstrip("\n") + "\n")
        self.stdout.flush()

    def eprint(self, buf):
        self.stderr.write(str(buf).rstrip("\n") + "\n")
        self.stderr.flush()

    def do_sample_cmd(self, args):
        """
        Sample command for test purposes

        Usage: sample_cmd x (optional: y)
        param x: arg to be printed to stdout
        param y: (optional) arg to be printed to stderr
        """
        if not args:
            raise ArgumentError(None,'No Arguments provided to sample_cmd')
        args = str(args).split()
        self.oprint('This is printed to stdout:' + str(args.pop(0)))
        if args:
            self.eprint('This is printed to stderr:' + str(args.pop(0)))

    def do_show_cli_env(self, args):
        """show current cli environment variables"""
        buf = ""
        if not self.env:
            buf = "\tNo env found?"
        else:
            for key in self.env.__dict__:
                buf += "\t{0} -->  {1} \n".format(key, self.env.__dict__[key])
        self.oprint(buf)

    def do_home(self, args):
        """Return to the home menu of the cli"""
        if self == self.path_from_home[0]:
            self.oprint('Currently at home menu')
        else:
            self._load_menu(self.path_from_home[0],
                            path_from_home=self.path_from_home[:1])

    def onecmd(self, line):
        try:
            return Cmd.onecmd(self, line)
        except Exception as FE:
            if self.env.debug:
                print_exc(file=self.stderr)
            self.eprint('Error while executing line: "{0}", err:{1}\n'
                            .format(line, str(FE)))


    def do_back(self, args):
        """Go Back one level in menu tree"""
        if len(self.path_from_home) > 1:
            self.path_from_home.pop()
            self._load_menu(self.path_from_home[-1],
                            path_from_home=self.path_from_home)

    def _load_menu(self, menu, path_from_home=None):
        if path_from_home is None:
            path_from_home = self.path_from_home
        if isinstance(menu, BaseMenu):
            menu.env = self.env
            menu.path_from_home = path_from_home
        elif isclass(menu) and issubclass(menu, BaseMenu):
            menu = menu(self.env,
                        path_from_home=path_from_home)
        else:
            raise TypeError('Menu must of type BaseMenu, menu:{0}, type:{1}'
                            .format(str(menu), type(menu)))
        self = menu
        self.cmdloop(intro=self.intro)
        self.oprint("**** {0} MENU ****".format(str(self.name)) + "\n")

    def emptyline(self):
        return

    def default(self, args):
        self.eprint('Command or syntax not recognized: "{0}"'.format(args))
        return self.do_help('')

    def do_clear(self, args):
        """
        Clear current screen
        """
        os.system('clear')

    def menu_summary(self, args):
        """Prints Summary of commands and sub-menu items"""
        submenus = ""
        commands = ""
        prevname = None
        names = self.get_names()
        menu_items = []
        maxlen = 0
        for name in names:
            if name[:3] == 'do_':
                if name == prevname:
                    continue
                prevname = name
                if len(name[3:]) > maxlen:
                    maxlen = len(name[3:])
                menu_items.append(name)
        for name in menu_items:
            cmd = str(name[3:])
            cmd_method = getattr(self, name)
            doc = str(cmd_method.__doc__) or ''
            doc = doc.lstrip().splitlines()[0].strip()
            if hasattr(cmd_method,'__submenu__'):
                submenus += '\t{0} {1} "{2}"'.format(cmd.ljust(maxlen),
                                                     "-->",
                                                     doc) + "\n"
            else:
                commands += '\t{0} {1} "{2}"'.format(cmd.ljust(maxlen),
                                                     "-->",
                                                     doc) + "\n"
        self.oprint("{0}\n{1}\n{2}\n{3}\n".format('\t*** SUB MENUS ***',
                                                  submenus,
                                                  '\t*** COMMANDS ***',
                                                  commands))

    def parseline(self, line):
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = line.strip()
        if not line:
            return None, None, line
        elif '?' in line    :
            if line[0] == '?':
                if len(line) == 1:
                    return 'menu_summary', '', line
            else:
                line = 'help ' + str(line).replace('?','')

        return Cmd.parseline(self, line)

    def do_quit(self, args):
        """Quits the program."""
        self.oprint("Quitting.")
        raise SystemExit
