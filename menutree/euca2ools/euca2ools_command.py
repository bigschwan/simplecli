__author__ = 'clarkmatthew'

from prettytable import PrettyTable
from colorama import Fore, init
from subprocess import Popen, PIPE
import re





cmd_string = 'euca-describe-images --show-empty-fields -h'
cmd = cmd_string.split()
p = Popen(cmd, stdout=PIPE)
p_out, p_err = p.communicate()
if p.returncode:
    print str(p_out)
    raise RuntimeError('Cmd:"{0}" failed. Code:{1}. stderr:"{1}"'
                       .format(cmd_string, p.returncode, p_err))
lines = p_out.splitlines()
args = {}
arg = None
for line in lines:
    help = ""
    print 'Looking at line:' + str(line)
    if not line.strip():
        continue
    if re.search('^\w', line):
        print 'Parsing arg line: ' + str(line)
        line = line.strip()
        split_line = line.split()
        arg = line[0]
        help = " ".join(line[1:-1])
        args[arg] = help
        print 'got arg:"{0}", and help:"{1}"'.format(arg, args[arg])
    else:
        print 'parsing help line for arg:{0}, adding:{1}'.format(arg, line.strip())
        args[arg] += line.strip()
'''
pt = PrettyTable()
for arg in args:
    pt.add_row([arg, args[arg]])
print pt
'''







