__author__ = 'clarkmatthew'


from simplecli.baseenv import BaseEnv
from menutree.homemenu import HomeMenu


if __name__ == '__main__':
    env = BaseEnv()
    menu = HomeMenu(env=env)
    menu.homemenu = menu
    menu.cmdloop('*** Home Menu ***')
