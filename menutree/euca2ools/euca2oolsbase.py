__author__ = 'clarkmatthew'

from simplecli.basemenu import BaseMenu, CliError
from subprocess import Popen, PIPE
import os
import glob


class pkg_mgr(object):

    def info(self, pkg):
        raise NotImplementedError()

    def install(self, pkg):
        raise NotImplementedError()

    def uninstall(self, pkg):
        raise NotImplementedError()

    def search(self, pkg):
        raise NotImplementedError()

    def cmd(self, cmd_string):
        cmd = cmd_string.split()
        p = Popen(cmd, stdout=PIPE)
        p_out, p_err = p.communicate()
        if p.returncode:
            print str(p_out)
            raise RuntimeError('Cmd:"{0}" failed. Code:{1}. stderr:"{1}"'
                               .format(cmd_string, p.returncode, p_err))
        return p_out

class yum(pkg_mgr):

    def info(self, pkg):
        return self.cmd('yum info ' + str(pkg))

    def install(self, pkg):
        return self.cmd('yum install ' + str(pkg))



class Euca2oolsBase(BaseMenu):
    name = None
    _summary = None
    _submenus = []
    _source_url = "https://github.com/eucalyptus/euca2ools.git"
    _latest_pkg_url = ""
    _epel_url = "http://downloads.eucalyptus.com/software/euca2ools/2.1/rhel/6/x86_64/epel-release-6.noarch.rpm"
    _repo_url = "http://downloads.eucalyptus.com/software/euca2ools/3.0/rhel/6/x86_64/euca2ools-release-3.0.noarch.rpm"
    _pkg_mgr = None


    @property
    def pkg_mgr(self):
        if self._pkg_mgr:
            return self._pkg_mgr
        pms = ['yum', 'apt', 'pip']
        for pm in pms:
            for path in os.environ['PATHS']:
                pm_path = os.path.join(path, pm)
                if os.path.isfile(pm_path) and os.access(pm_path, os.X_OK):
                    self._pkg_mgr = pm
                    return pm
        raise RuntimeError('No package manager found available to this user:'
                           + ",".join(pms))




    def show_package_info(self):
        cmd = "yum info "
        p = Popen('')


    def _preflight_checks(self):
        config = getattr(self.env, 'euc2ools', None)
        if not config:



    def _find_euca2ools(self):
        tools_paths = {}
        for path in os.environ['PATH'].split(':'):
            tools = glob.glob(os.path.join(path,'euca*'))
            if tools:
                tools_paths[path] = tools
        return tools_paths




