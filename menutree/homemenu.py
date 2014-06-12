#!/usr/bin/python

from simplecli.basemenu import BaseMenu
from menutree.services.services_menu import Services_Menu
from menutree.tests.testsmenu import TestsMenu


class HomeMenu(BaseMenu):
    name = 'home_menu'
    _summary = 'Home Menu'
    _submenus = [Services_Menu, TestsMenu]


