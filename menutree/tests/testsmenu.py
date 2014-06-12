__author__ = 'clarkmatthew'

from simplecli.basemenu import BaseMenu
from menutree.tests.object_storage_menu import Object_Storage_Menu
from menutree.tests.block_storage_menu import Block_Storage_Menu
from menutree.tests.network_test_menu import Network_Test_Menu

class TestsMenu(BaseMenu):
    name = 'tests_menu'
    _summary = 'Tests Menu'
    _submenus = [Object_Storage_Menu, Block_Storage_Menu, Network_Test_Menu]

