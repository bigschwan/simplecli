import os
import sys
from cmd import Cmd
from traceback import print_exc
from simplecli.baseenv import BaseEnv
from inspect import isclass
import termios
import tty

try:
    from colorama import init, Fore, Back
except ImportError:
    pass

class CliError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class BaseMenu(Cmd, object):

    #########################################################################
    # BaseMenu class is meant to be used to create parent and child menus   #
    # Menus can be defined with a unique name and then linked by either     #
    # the _submenues list providing BaseMenu class submenus, or by adding   #
    # the plugin file into the plugins dir (specificied in simplecli.conf)  #
    # to add the menu to the parent menu(s) as a child/sub menu             #
    #########################################################################

    # This must be defined for subclasses of BaseMenu
    name = None

    # _submenus is a list of BaseMenu types which will be accessible through
    # this menu's context. Submenus can also be linked via plugin menus.
    _submenus = []

    # _summary is a brief single string summary used in help menus
    _summary = None

    # _description is buffer used for more detailed help menus
    _description = None

    # _info is the message printed when this menu is loaded
    _intro = None

    # _parents if this menu is loaded as a plugin, _parents can be populated
    # with a list of strings matching the parent menu(s)'s name for which this
    # menu will be loaded as a sub menu.
    _parents = []


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
        if 'colorama' in sys.modules:
            init()
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
        self._path_from_home = []
        self.path_from_home = path_from_home
        self._init_submenus()


    def do_python_cmd(self, cmd):
        '''
        Executes python eval(cmd) for simple python debugging
        '''
        self.oprint(eval(cmd), allow_break=False)

    @property
    def path_from_home(self):
        return self._path_from_home

    @path_from_home.setter
    def path_from_home(self, path):
        self._path_from_home = path or []
        if not self._path_from_home or self._path_from_home[-1] != self:
            self._path_from_home.append(self)

    @property
    def path(self):
        return (str(self.path_delimeter)
                .join(str(x.name) for x in self.path_from_home))

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

    @intro.setter
    def intro(self, intro):
        self._intro = intro

    def _init_submenus(self, menus=None):
        # Get the menus defined for this menu class
        menus = menus or self._submenus or []
        # Get the dynamic menus/plugins
        menus.extend(self.env._get_plugins_for_parent(self))
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

    def _color(self, buf, color='BLUE'):
        color = str(color).upper()
        if 'colorama' in sys.modules:
            color = getattr(Fore, color, "")
            if not color:
                return buf
            lastchar = ''
            if buf.endswith('\n'):
                lastchar = '\n'
                buf.rstrip('\n')
            buf = '{0}{1}{2}{3}'.format(color,str(buf), lastchar, Fore.RESET)
        return buf


    def _get_terminal_size(self):
        '''
        Attempts to get terminal size. Currently only Linux.
        returns (height, width)
        '''
        # todo Add Windows support
        import fcntl
        import struct
        return struct.unpack('hh', fcntl.ioctl(self.stdout,
                                               termios.TIOCGWINSZ,
                                               '1234'))

    def _init_plugin_menus(self):
        plugins = self.env._get_plugins_for_parent(self.name)

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

    def oprint(self, buf, allow_break=True):
        if allow_break and self.env.page_break:
            height, width = self._get_terminal_size()
            lines = buf.splitlines()
            x = 0
            y = 0
            length = height
            line_cnt = len(lines)
            while y < line_cnt:
                length = length or line_cnt
                y += length
                if y >= line_cnt:
                    y = line_cnt - 1
                for line in lines[x:y]:
                    self.stdout.write(str(line) + "\n")
                self.stdout.flush()
                x = y
                if (y + 1) >= line_cnt:
                    return
                else:
                    self.stdout.write(':\r')
                    self.stdout.flush()
                    fd = self.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        ch = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    print '\b ',
                    ch = str(ch)
                    if ch == "\n" or ch == "\r" or ch == "":
                        length = height
                    elif ch == "a":
                        length = 0
                    elif ch == "q":
                        print "\n"
                        return
                    else:
                        length = 1
        else:
            self.stdout.write(str(buf).rstrip("\n") + "\n")
            self.stdout.flush()

    def eprint(self, buf):
        buf = self._color(buf=str(buf), color='RED')
        self.stderr.write(str(buf).rstrip("\n") + "\n")
        self.stderr.flush()

    def do_set_page_break(self, enable):
        """
        Enables/disables the global page break env var.
        Usage set_page_break [on/off]
        """
        if int(enable):
            self.env.page_break = True
        else:
            self.env.page_break = False

    def do_sample_cmd(self, args):
        """
        Sample command for test purposes

        Usage: sample_cmd x (optional: y)
        param x: arg to be printed to stdout
        param y: (optional) arg to be printed to stderr
        """
        if not args:
            raise CliError(None,'No Arguments provided to sample_cmd')
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
                            path_from_home=[])

    def onecmd(self, line):
        try:
            return Cmd.onecmd(self, line)
        except CliError as AE:
            self.eprint("ERROR: " + str(AE))
            return self.onecmd("? " + str(line))
        except Exception as FE:
            if self.env.debug:
                print_exc(file=self.stderr)
            self.eprint('\n"{0}", err:{1}'.format(line, str(FE)))
            self.oprint('\n')

    def do_back(self, args):
        """Go Back one level in menu tree"""
        if len(self.path_from_home) > 1:
            if self.path_from_home[-1] == self:
                self.path_from_home.pop()
            self._load_menu(self.path_from_home[-1],
                            path_from_home=self.path_from_home)

    def _load_menu(self, menu, path_from_home=None):
        if path_from_home is None:
            path_from_home = self.path_from_home
        if isinstance(menu, BaseMenu):
            menu.env = self.env
            menu.path_from_home = path_from_home
            menu._init_submenus()
        elif isclass(menu) and issubclass(menu, BaseMenu):
            existing_menu = self.env.get_menu_by_class(menu)
            if existing_menu:
                menu = existing_menu
                menu.path_from_home = path_from_home
                menu._init_submenus()
            else:
                menu = menu(self.env,
                            path_from_home=path_from_home)
                self.env.menu_instances.append(menu)
        else:
            raise TypeError('Menu must of type BaseMenu, menu:{0}, type:{1}'
                            .format(str(menu), type(menu)))
        self = menu
        self.cmdloop(intro=self.intro)
        self.oprint(self._color('BLUE') + "**** {0} MENU ****"
                    .format(str(self.name)) + "\n")

    def emptyline(self):
        return

    def default(self, args):
        self.eprint('Command or syntax not recognized: "{0}"'.format(args))
        return self.menu_summary(args)

    def do_clear(self, args):
        """
        Clear current screen
        """
        os.system('clear')

    def menu_summary(self, args):
        """Prints Summary of commands and sub-menu items"""
        submenus = ""
        basecommands = ""
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
            elif hasattr(BaseMenu, name):
                basecommands += '\t{0} {1} "{2}"'.format(cmd.ljust(maxlen),
                                                         "-->",
                                                         doc) + "\n"
            else:
                commands += '\t{0} {1} "{2}"'.format(cmd.ljust(maxlen),
                                                     "-->",
                                                     doc) + "\n"
        self.oprint("{0}\n{1}\n{2}\n{3}\n{4}\n{5}".format(
            '\t' + self._color('*** SUB MENUS ***'),
            submenus,
            '\t' + self._color('*** ' + self.name.upper() + ' COMMANDS ***'),
            commands,
            '\t' + self._color('*** BASE COMMANDS ***'),
            basecommands))

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

