import json
import os
import sys
from cmd import Cmd
from traceback import print_exc
from simplecli.baseenv import BaseEnv
from StringIO import StringIO
from collections import OrderedDict
import signal
import time
from inspect import isclass
import termios
import tty
import re
import readline
from prettytable import PrettyTable
from cloud_utils.log_utils import markup, get_traceback, red, blue, yellow, green, cyan
import readline


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
                 prompt_method=None,
                 path_delimeter=None,
                 stdin=None,
                 stdout=None,
                 stderr=None):
        # Note super does not work as Cmd() is an 'old style' class which
        # does not inherit from object(). Instead call init directly.
        #self._submenu_names = None
        self._last_keyboard_interupt = 0
        signal.signal(signal.SIGINT, self._keyboard_interupt_handler)
        if 'colorama' in sys.modules:
            init()
        self.stdout = stdout or env.default_output or sys.stdout
        self.stdin = stdin or env.default_input or sys.stdin

        # Attempt to populate the command history from history file,
        # if it has not yet, and the file is provided and exists
        try:
            history_len = readline.get_history_length()
            if history_len < 1:
                history_path = getattr(env.simplecli_config, 'history_file', None)
                if history_path and os.path.exists(history_path):
                    readline.read_history_file(history_path)
        except ImportError as IE:
            self.eprint('Failed to read in history file, err:{0}'.format(IE))
            pass
        Cmd.__init__(self, completekey='tab', stdin=stdin, stdout=stdout)
        self.stderr = stderr or env.default_error or sys.stderr
        if not self.name:
            raise ValueError('Class must define "name", extend BaseEnv')
        assert isinstance(env, BaseEnv), "env variable must be of type BaseEnv"
        self.env = env
        self.prompt_method = prompt_method or env.simplecli_config.prompt_method
        self.path_delimeter = path_delimeter or env.simplecli_config.path_delimeter
        self._path_from_home = []
        self.path_from_home = path_from_home
        self._setup()
        self._init_submenus()
        self._old_completer = readline.get_completer()
        readline.set_completion_display_matches_hook(self._completer_display)


    def _setup(self):
        """
        Implement this method to run custom checks and setup in __init__().
        """
        return


    def __repr__(self):
        return "{0}:{1}".format(self.__class__.__name__, self.name)


    def _keyboard_interupt_handler(self, signal, frame):
        self.eprint('Caught ctrl-c, press again quickly to exit')
        current_time = time.time()
        if (current_time - self._last_keyboard_interupt ) <= 1:
            self.do_quit(None, force=True)
            os._exit(0)
        else:
            # Set time of event and raise EOF to clear command line
            self._last_keyboard_interupt = current_time
            raise EOFError

    def _completer_display(self, substitution, matches, longest_match_length):

        try:
            pt = PrettyTable(['OPTIONS'])
            pt.header = False
            pt.border = False
            pt.align = 'l'
            height, width = self._get_terminal_size()
            pt.max_width = width - 5
            menus = ""
            cmds = ""
            total = []
            for match in matches:
                if not substitution or str(match).startswith(substitution):
                    total.append(match)
                    if match in self.submenu_names:
                        menus += " {0} ".format(blue(match, bold=True))
                    else:
                        cmds += " {0} ".format(yellow(match), bold=True)
            if menus:
                pt.add_row(["\n{0}".format(menus)])
            if cmds:
                if not menus:
                    cmds = "\n{0}".format(cmds)
                pt.add_row([cmds])
            line = readline.get_line_buffer()

            self.dprint("Completer_display():\nsubstitution:{0}\nmatches:{1}"
                        "\nlongest_match_length:{2}\nlen total:{3}\nline:{4},\nsubtype:{5}\n"
                        "total:{6}\nsubstitution:{7}\n"
                        .format(substitution, matches, longest_match_length, len(total), line,
                                type(substitution), total, substitution))
            if self.debug:
                self.do_cli_env(None)

            self.stdout.seek(0)
            self.stdout.write("")
            self.stdout.flush()
            readline.redisplay()
            self.oprint("{0}".format(pt))

            if len(matches) == 1:
                cli_text = "{0}{1}".format(self.prompt, matches[0])
            else:
                cli_text = "{0}{1}".format(self.prompt, substitution)

            self.stdout.write(cli_text)
            self.stdout.flush()
            readline.redisplay()

        except Exception as E:
            self.stderr.write(red("{0}\nError in completer_display:\nerror:{1}"
                              .format(get_traceback(), E)))
            self.stderr.flush()



    def do_python_cmd(self, cmd):
        '''
        Executes python eval(cmd) for simple python debugging
        '''
        self.oprint(eval(cmd), allow_break=False)

    @property
    def debug(self):
        return self.env.simplecli_config.debug

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
    def submenu_names(self):
        #if self._submenu_names is None:
        names = []
        for menu in self._submenus:
            names.append(menu.name)
        #self._submenu_names = names
        return names

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
        try:
            # todo Add Windows support
            import fcntl
            import struct
            return struct.unpack('hh', fcntl.ioctl(self.stdout,
                                                   termios.TIOCGWINSZ,
                                                   '1234'))
        except:
            return 80

    def _init_plugin_menus(self):
        plugins = self.env._get_plugins_for_parent(self.name)

    def emptyline(self):
        return

    def precmd(self, line):
        if line == 'EOF':
            line = ''
        return line

    def default(self, args):
        self.eprint('Command or syntax not recognized: "{0}"'.format(args))
        return self.menu_summary(args)

    def get_names(self):
        names = dir(self.__class__)
        for key in self.__dict__:
            if not key in names:
                names.append(key)
        return names

    def _get_complete_strings(self, text=None):
        if text is None:
            text = 'do_'
        ret = []
        for name in self.get_names():
            if name.startswith(text):
                ret.append(name[3:])
        return ret

    def _add_doc_string(value):
        def _doc(func):
            func.__doc__ = value
            return func
        return _doc

    @_add_doc_string(Cmd.do_help.im_func.func_doc)
    def do_help(self, arg):
        Cmd.do_help(self, arg)
        if not arg:
            self.menu_summary(arg)

    def hidden_ls(self, arg):
        return self.do_help(arg)

    def hidden_cd(self, args):
        if not args:
            return self.do_home(args=args)
        if args == '..' or args == '-':
            return self.do_back(args=args)

    def _add_sub_menu(self, menu, description=None):
        assert isinstance(menu, BaseMenu) or issubclass(menu, BaseMenu), \
            'Error adding sub menu, item is not BaseMenu type'
        # Add a local method/cli visible command to load
        # the submenu menu based on the menu name
        method_name = 'do_' + menu.name
        do_method = lambda line: self._sub_menu_handler(menu, line)
        setattr(self, method_name, do_method)
        new_method = getattr(self, method_name)
        new_method.__doc__ = description or menu._summary or ""
        new_method.__submenu__ = True
        # Add completer method to handle presenting the sub-contexts of each
        # Sub menu based on the completion strings
        complete_method_name = 'complete_' + menu.name
        complete_method = \
            lambda text, line, begidx, endidx: self._sub_menu_complete(text,
                                                                       menu,
                                                                       line,
                                                                       begidx,
                                                                       endidx)
        setattr(self, complete_method_name, complete_method)
        if not menu in self._submenus:
            self._submenus.append(menu)

    def _init_submenus(self, menus=None, add_setup_menu=True):
        # Get the menus defined for this menu class
        menus = menus or self._submenus or []
        if not isinstance(self, Setup_Menu) and add_setup_menu:
            if not Setup_Menu in menus:
                menus.append(Setup_Menu)
        # Get the dynamic submenus/plugins for this menu class
        menus.extend(self.env._get_plugins_for_parent(self))
        # Add each submenu to this menu instance
        for menu in menus:
            try:
                if isinstance(menu, BaseMenu) or issubclass(menu, BaseMenu):
                    self._add_sub_menu(menu)
                else:
                    raise AttributeError('Init sub-menu error, item must be '
                                         'of type BaseMenu')
            except Exception as ME:
                if self.env.simplecli_config.debug:
                    print_exc(file=self.stderr)
                mname = str(menu)
                self.dprint('Error loading submenu "{0}", err:{1}\n'
                            .format(mname,
                                    str(ME)))

    def _sub_menu_handler(self, menu, line):
        '''
        Method to be used when loading submenus, will determine if the
        menu context should be loaded, or if a command in the chain of
        submenus should be instead executed.
        '''
        self.dprint('\n submenu_handler. menu:{0}, line:"{1}"'
                    .format(menu.name, line))
        if not line:
            return self._load_menu(menu)
        else:
            if isinstance(menu, BaseMenu):
                menuclass = menu.__class__
            elif isclass(menu):
                menuclass = menu
            else:
                raise ValueError('menu is not BaseMenu type or class')
            try:
                menu = self.env.get_menu_by_class(menuclass=menuclass)
                if not menu:
                    menu = menuclass(self.env)
                    self.env.menu_cache.append(menu)
                assert isinstance(menu, BaseMenu)
                self.dprint('Running cmd:"{0}" , with menu:{1}'
                            .format(line, menu.name))
                cmd_attr = getattr(menu, 'do_' + line, None)
                # If a new submenu is being loaded, update the prompts path
                if cmd_attr and hasattr(cmd_attr,'__submenu__'):
                    menu.path_from_home = self.path_from_home
                return menu.onecmd(line)
            except:
                print_exc()
                raise

    def _sub_menu_complete(self, text, menu, line, begidx=None, endidx=None):
        '''
        Method to be used when loading submenus to allow the user to tab
        complete and see the items in the chain of submenus.
        '''

        self.dprint('sub_menu_complete(). self:{0}, menu:{1}, text:"{2}", '
                    'line:"{3}"'.format(self.name, menu.name, text, line))
        ret = []
        if isinstance(menu, BaseMenu):
            menuclass = menu.__class__
        elif isclass(menu):
            menuclass = menu
        else:
            raise ValueError('menu is not BaseMenu type or class')
        try:
            menu = self.env.get_menu_by_class(menuclass=menuclass)
            if not menu:
                menu = menuclass(self.env)
                self.env.menu_cache.append(menu)
            assert isinstance(menu, BaseMenu)
            self.dprint('sub_menu_complete() getting menu items from '
                        '{0}.completeddefault()'.format(menu.name))
            menu_items = menu.completedefault(text, line, begidx, endidx)
            for item in menu_items:
                if not hasattr(BaseMenu, 'do_' + item.strip()):
                    ret.append(item)
        except:
            print_exc()
            raise
        self.dprint('sub_menu_complete() returning menu items:' + str(ret))
        return ret

    def complete(self, text, state):
        """Return the next possible completion for 'text'.
        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        self.dprint('Complete()1: menu:"{0}", text:"{1}", state:"{2}"'
                    .format(self.name, text, state))
        if state == 0:
            import readline
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            self.dprint('Complete()2: text:{0}, origline:{1}'.format(text, line))
            if begidx>=0:
                cmd, args, foo = self.parseline(line)
                if not cmd:
                    self.dprint('Complete()3: no cmd after parseline(), '
                                'sending to default()')
                    compfunc = self.completedefault
                else:
                    try:
                        compfunc = getattr(self, 'complete_' + cmd)
                        self.dprint('Complete()4: got method complete_' + str(cmd))
                    except AttributeError:
                        self.dprint('Complete()5: no complete_ method '
                                    'found, sending to default()')
                        compfunc = self.completedefault
            else:
                self.dprint('Complete()2: non-zero state sending to '
                            'completenames(), state:{0}'.format(state))
                compfunc = self.completenames
            try:
                self.completion_matches = compfunc(text, line, begidx, endidx)
            except:
                print_exc()
                raise
        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def completedefault(self, text, line='', begidx=None, endidx=None):
        '''
        Used with complete() to look for matching
        local complete ('complete_') or execute('do_') methods to be used
        in the chain of submenu contexts
        '''
        self.dprint('completedefault(). menu:{0}, text:{1}, line:"{2}", '
                    'beg:{3}, end{4}'
                    .format(self.name, text, line, begidx, endidx ))
        # See if this is in the process of completing a word or line
        if not text and begidx is not None and endidx is not None:
            if begidx == endidx:
                text = line
        text = (text or '').lstrip()
        # See if this is being handled by a submenu and the local menu name
        # needs to be removed...
        self.dprint('completeefault(). Looking regex: re.search("^{0}\s*$", {1})'
                    .format(self.name, text))
        text = re.sub('^' + self.name + '\s*', '', text)
        self.dprint('completedefault() text after replace:"{0}"'.format(text))
        line = text
        # See if theres a 'complete_' method local to this menu based on the
        # first word in the line, if not return all the matching
        # local 'do_' methods.
        # Note: a submenu method will forward the line to be completed down
        # the chain of submenus to return available matching methods.
        try:
            firstword = str(text).split()[0]
            self.dprint('completedefault() got first word:' + str(firstword))
        except IndexError:
            firstword = None
        if firstword:
            complete_text = 'complete_' + firstword
            complete_meth = getattr(self, complete_text, None)
            if complete_meth:
                text = str(text).replace(firstword,'')
                try:
                    return complete_meth(text, line, begidx, endidx)
                except:
                    print_exc()
                    raise
        self.dprint('completedefault() returning {0}.get_names() for matching:{1}'
                    .format(self.name, 'do_'+ str(text)))
        dotext = 'do_' + str(text)
        return self._get_complete_strings(dotext)
        #return [a[3:] + " " for a in self._get_complete_strings() if a.startswith(dotext)]


    def oprint(self, buf, allow_break=True):
        '''
        Helper function to print to the output (ie stdout) specififed
        If page_break is set, this will also provide user interactive
        scrolling based on the terminal size.
        '''
        if allow_break and self.env.simplecli_config.page_break:
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
                    y = line_cnt
                for line in lines[x:y]:
                    self.stdout.write(str(line) + "\n")
                self.stdout.flush()
                x = y
                if (y + 1) >= line_cnt:
                    return
                else:
                    #Handle the 'more' type scrolling function...
                    self.stdout.write(':\r')
                    self.stdout.flush()
                    fd = self.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        ch = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    #print '\b ',
                    self.stdout.write('\b')
                    ch = str(ch)
                    if ch == "\n" or ch == "\r" or ch == "":
                        length = height
                    elif ch == "a":
                        length = 0
                    elif ch == "q":
                        print "\n"
                        self.stdout.write('\n')
                        return
                    else:
                        length = 1
                    self.stdout.flush()
        else:
            self.stdout.write(str(buf).rstrip("\n") + "\n")
            self.stdout.flush()

    def eprint(self, buf):
        buf = self._color(buf=str(buf), color='RED')
        self.stderr.write(str(buf).rstrip("\n") + "\n")
        self.stderr.flush()

    def dprint(self, buf):
        if self.debug:
            buf = self.name + ": " + str(buf)
            buf = self._color(buf=str(buf), color='YELLOW')
            self.stderr.write(str(buf).rstrip("\n") + "\n")
            self.stderr.flush()

    def do_output_test(self, args):
        """
        Sample command for test purposes

        Usage: sample_cmd x (optional: y)
        param x: arg to be printed to stdout
        param y: (optional) arg to be printed to stderr
        """
        args = args or 'test_stdout test_stderr'
        args = str(args).split()
        self.oprint('This is printed to stdout:' + str(args.pop(0)))
        if args:
            self.eprint('This is printed to stderr:' + str(args.pop(0)))

    def do_cli_env(self, args):
        """show current cli environment variables"""
        buf = ('\nCURRENT MENU CLASS:"{0}"'
               '\nPROMPT:"{1}"'
               '\nPATH FROM HOME:"{2}"'
               '\nSUB MENUS:"{3}"'
               '\nCLI CONFIG JSON:\n'
               .format(self,
                       self.prompt,
                       ",".join(x.name for x in self.path_from_home),
                       ", ".join(str(x) for x in self.submenu_names)))
        if not self.env:
            buf += "No env found?"
        else:
            buf += json.dumps(self.env.simplecli_config.__dict__, sort_keys=True, indent=4)
        self.oprint(yellow(buf))

    def do_home(self, args):
        """Return to the home menu of the cli"""
        if self == self.path_from_home[0]:
            self.oprint('Currently at home menu')
        else:
            self._load_menu(self.path_from_home[0],
                            path_from_home=[])

    def onecmd(self, line):
        cmd, arg, line = self.parseline(line)
        func = getattr(self, "hidden_{0}".format(cmd), None)
        try:
            if func:
                return func(arg)
            else:
                return Cmd.onecmd(self, line)
        except CliError as AE:
            self.eprint("ERROR: " + str(AE))
            return self.onecmd("? " + str(line))
        except SystemExit:
            raise
        except Exception as FE:
            if self.env.simplecli_config.debug:
                print_exc(file=self.stderr)
            self.eprint('\n"{0}": {1}({2})'.format(line, FE.__class__.__name__, str(FE)))
            self.oprint('\n')

    def do_back(self, args):
        """Go Back one level in menu tree"""
        if len(self.path_from_home) > 1:
            if self.path_from_home[-1] == self:
                self.path_from_home.pop()
            self._load_menu(self.path_from_home[-1],
                            path_from_home=self.path_from_home)

    def _load_menu(self, menu, path_from_home=None):
        self.dprint('load_menu():\n\tmenu:{0}\n\tpath from home:{1}'
                    '\n\tself.path_from_home{2}'
                    .format(menu, path_from_home, self.path_from_home))
        if path_from_home is None:
            path_from_home = self.path_from_home
        if isinstance(menu, BaseMenu):
            self.dprint('load_menu: got menu INSTANCE: "{0}"'.format(menu.__class__.__name__))
            if self.__class__ == menu.__class__:
                    return
            menu.env = self.env

            menu.path_from_home = path_from_home
            menu._init_submenus()
        elif isclass(menu) and issubclass(menu, BaseMenu):
            self.dprint('load_menu: got menu CLASS: "{0}"'.format(menu))
            existing_menu = self.env.get_menu_by_class(menu)
            if existing_menu:
                if existing_menu.__class__ == self.__class__:
                    return
                menu = existing_menu
                menu.path_from_home = path_from_home
                menu._init_submenus()
            else:
                menu = menu(self.env,
                            path_from_home=path_from_home)
                self.env.menu_cache.append(menu)
        else:
            raise TypeError('Menu must of type BaseMenu, menu:{0}, type:{1}'
                            .format(str(menu), type(menu)))
        self = menu
        readline.set_completer(menu.complete)
        readline.set_completion_display_matches_hook(menu._completer_display)
        self.cmdloop(intro=self.intro)
        self.oprint(self._color('BLUE') + "**** {0} MENU ****"
                    .format(str(self.name)) + "\n")


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
        main_pt = pt = PrettyTable(['MAIN'])
        main_pt.header = False
        main_pt.border = False
        main_pt.align = 'l'
        sub_pt = PrettyTable(['COMMAND', 'DESCRIPTION'])
        base_pt = PrettyTable(['COMMAND', 'DESCRIPTION'])
        current_pt = PrettyTable(['COMMAND', 'DESCRIPTION'])
        for table in [sub_pt, base_pt, current_pt]:
            table.header = False
            table.border = False
            table.align = 'l'
        #Sort out methods that begin with 'do_' as menu items...
        for name in names:
            if name[:3] == 'do_':
                if name == prevname:
                    continue
                prevname = name
                if len(name[3:]) > maxlen:
                    maxlen = len(name[3:])
                menu_items.append(name)
        #Sort out menu items into: submenus, local commands, and globals
        for name in menu_items:
            cmd = str(name[3:])
            cmd_method = getattr(self, name)
            doc = str(cmd_method.__doc__) or ''
            doc = doc.lstrip().splitlines()[0].strip()
            if hasattr(cmd_method,'__submenu__'):
                sub_pt.add_row([blue("\t{0}".format(cmd), bold=False), doc])
            elif hasattr(BaseMenu, name):
                base_pt.add_row([yellow("\t{0}".format(cmd), bold=False), doc])
            else:
                current_pt.add_row([green("\t{0}".format(cmd), bold=True), doc])
        buf = "{0}\n{1}\n{2}\n{3}\n{4}\n{5}".format(
            cyan('*** ' + self.name.upper() + ' COMMANDS ***', bold=True), current_pt,
            cyan('*** SUB MENUS ***', bold=True), sub_pt,
            cyan('*** BASE COMMANDS ***', bold=True), base_pt)
        main_pt.add_row([buf])
        self.oprint("{0}".format(main_pt))


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


    def get_submenu(self, submenu):
        if isinstance(submenu, str):
            print 'Looking up submenu by name:' + str(submenu)
            name = submenu
            for menu in self._submenus:
                if getattr(menu, 'name', "") == name:
                    return menu
        elif isclass(submenu):
            print 'Looking up submenu by class:' + str(submenu)
            for menu in self._submenus:
                print 'looking at menu:' + str(menu.name)
                if isinstance(menu, submenu):
                    return menu
        return None

    def hidden_exit(self, args, force=True, status=0):
        return self.do_quit(args=args, force=force, status=status)

    def do_quit(self, args, force=True, status=0):
        """Quits the program."""
        self.oprint("Quitting.")
        if 'force' in str(args).lower():
            force = True
        if not force:
            if 'saveall' in str(args).lower():
                self.env.save_all()
            else:
                diff = self.env.get_config_diff()
                if diff:
                    self.eprint("Configuration has not been saved.\n"
                                "Save now or use 'quit force' to quit"
                                " without saving,\n"
                                "or 'quit saveall' to save upon quit")
                    return
        try:
            import readline
            history_path = getattr(self.env.simplecli_config, 'history_file', None)
            if history_path:
                if not os.path.exists(history_path):
                    open(history_path, 'w').close()
                readline.set_history_length(100)
                readline.write_history_file(history_path)
        except ImportError:
            pass
        except:
            print_exc()
            raise
        try:
            if self._old_completer:
                readline.set_completer(self._old_completer)
        except:
            pass
        raise SystemExit

class Setup_Menu(BaseMenu):
    name = 'setup_menu'
    _summary = 'SimpleCLI Setup Menu'
    _description = 'SimpleCLI Setup Menu'
    _intro = 'SimpleCLI Setup Menu'

    @property
    def config(self):
        return self.env.simplecli_config

    def do_show(self, text):
        """
        Show configuration info
        """
        if text:
            text = text.strip()
            text = re.sub("^show\s*", '', text)
            if text:
                words = text.split()
                nextword = words[0]
                showmethod = getattr(self, 'show_' + str(nextword), None)
                if showmethod:
                   return showmethod(words[1:])
        return self.help_show()

    def help_show(self, *args):
        match = 'show_'
        showlist = [a[5:] + " " for a in self.get_names() if a.startswith(match)]
        self.oprint('Available show commands:\n{0}'.format("\n\t".join(showlist)))

    def complete_show(self, text, *ignore):
        text = re.sub("^show\s*", '', text)
        complete_method = getattr(self, 'show_' + text, None)
        if complete_method:
            return complete_method(text, ignore)
        match = 'show_' + str(text)
        return [a[5:] + " " for a in self.get_names() if a.startswith(match)]

    def show_stuff(self, args):
        print 'you got stuff'


    def show_config(self, configblock):
        """
        Show the current running configuration
        """
        configblock = configblock or None
        block = self.env.get_formatted_conf(block=configblock)
        if configblock and not block:
            block = '"{0}" configuration block not found'.format(configblock)
        self.oprint(block)


    def show_diff(self, args):
        """
        Show the diff between running and saved configuration
        """
        self.oprint(self.env.get_config_diff())

    def do_save_config(self, args):
        """
        Saves the running configuration to 'config_file_path'
        """
        return self.env.save_config()

    def do_set_debug(self, enable):
        """
        Enables/disables the global debug env var.
        Usage set_page_break [on/off]
        """
        enable = str(enable).lower().strip()
        if enable != 'on' and enable != 'off':
            self.eprint('"{0}", Invalid arg. Use "on/off"'.format(enable))
        if enable == 'on':
            self.env.simplecli_config.debug = True
        else:
            self.env.simplecli_config.debug = False


    def do_set_page_break(self, enable):
        """
        Enables/disables the global page break env var.
        Usage set_page_break [on/off]
        """
        enable = str(enable).lower().strip()
        if enable != 'on' and enable != 'off':
            self.eprint('"{0}", Invalid arg. Use "on/off"'.format(enable))
        if enable == 'on':
            self.env.simplecli_config.page_break = True
        else:
            self.env.simplecli_config.page_break = False


