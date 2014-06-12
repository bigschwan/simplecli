#!/usr/bin/python
__author__ = 'clarkmatthew'


from simplecli.baseenv import BaseEnv
from menutree.homemenu import HomeMenu


if __name__ == '__main__':
    env = BaseEnv()
    menu = HomeMenu(env=env)
    menu.cmdloop('*** Home Menu ***')
