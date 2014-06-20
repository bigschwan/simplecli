__author__ = 'clarkmatthew'



##############################################################################
# This file is to provide an example template for creating menu plugins      #
##############################################################################

# example showing fake import of a menu class
# which is a subclass of simplecli/BaseMenu()
from menutree.images.images_menu import Images_Menu as MENU

# menuclass is the basemenu class to load. Make sure it is imported above.
# example:
menu_class = MENU

# parentmenu is either the name of the "menu's class" or the menu's
# class.name of the parent menu(s) in which this plugin should be made
# available under as a sub menu.
# If the menu's class or name is not found in the available BaseMenus,
# an error will be presented when the plugin is loaded.
# Example below shows that the menu created from 'MyPlugin' will be a sub menu
# option under the menus found by the name 'Test Menu', and by
# the class HomeMenu().
parent_menus = ['class:HomeMenu']

