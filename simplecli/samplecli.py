__author__ = 'clarkmatthew'
from cmd import Cmd
from eucaops import Eucaops
import traceback
import os


class SecondPrompt(Cmd):
    def emptyline(self):
        return

    def default(self, args):
        print 'Command or syntax not recognized: "{0}"'.format(args)
        return self.do_help('')

    def do_clear(self, args):
        os.system('clear')

    def do_back(self, args):
        print 'going back (but not really)'


class MyPrompt(Cmd):
    tester = None
    password = 'foobar'

    def emptyline(self):
        return

    def default(self, args):
        print 'Command or syntax not recognized: "{0}"'.format(args)
        return self.do_help('')

    def do_clear(self, args):
        os.system('clear')

    def do_set_creds(self, args):
        """
        Creates a tests connection using the credpath provided. ie: './'
        """
        credpath = args or './'
        print 'Creating tester obj with args:' + str(credpath)
        #self.tester= Eucaops(credpath=args)
        self.tester = self.run_shit(Eucaops, credpath=credpath)

    def do_set_config(self, args):
        """
        Creates a tests connection using the config provided
        """
        self.tester = self.run_shit(Eucaops,
                                    config_file=args,
                                    password=self.password)

    def do_set_password(self, args):
        """
        Sets the root password to use with set_config connection
        """
        self.password = args

    def do_show_all_instances(self, args):
        '''
        Shows all instances available to your tests connection
        '''
        self.run_tester_shit('print_euinstance_list')

    def do_show_all_volumes(self, args):
        """
        Shows all volumes available to your tests connection
        """
        self.run_tester_shit('print_euvolume_list')

    def do_quit(self, args):
        """Quits the program."""
        print "Quitting."
        raise SystemExit

    def run_shit(self, cmd, *args, **kwargs):
        print ('Running cmd:"{0}" , args"{1}", kwargs"{2}"'
               .format(cmd, args, kwargs))
        try:
            return cmd(*args, **kwargs)
        except Exception as shtE:
            traceback.print_exc()
            print 'your shit failed:' + str(shtE)


    def run_tester_shit(self, cmd, *args, **kwargs):
        if not hasattr(self, 'tester') or not self.tester:
          print "make tester with set_creds or set_config first. See 'help'"
        else:
            cmd = getattr(self.tester, cmd)
            if args and args[0] == '?':
                print cmd.__doc__
                return
            try:
                if args and kwargs:
                    return cmd(args, kwargs)
                elif args:
                    return cmd(args)
                elif kwargs:
                    return cmd(kwargs)
                else:
                    return cmd()
            except Exception as shtE:
                traceback.print_exc()
                print 'your shit failed:' + str(shtE)

    def do_swap_cli(self, args):
        newprompt = SecondPrompt()
        newprompt.prompt = "#"
        self = newprompt
        self.cmdloop()




if __name__ == '__main__':
    prompt = MyPrompt()
    prompt.prompt = '> '
    prompt.cmdloop('Starting prompt...')