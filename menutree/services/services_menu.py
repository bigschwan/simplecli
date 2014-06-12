__author__ = 'clarkmatthew'

from simplecli.basemenu import BaseMenu
import menutree.services.block_storage_services_menu as block_storage_menu
import menutree.services.object_storage_services_menu as object_storage_menu
import menutree.services.network_services_menu as network_services_menu
import menutree.services.cloud_services_menu as cloud_services_menu


class Services_Menu(BaseMenu):
    name = 'services_menu'
    _summary = 'Services Menu'
    _submenus = [block_storage_menu.Block_Storage_Services_Menu,
                 cloud_services_menu.Cloud_Services_Menu,
                 network_services_menu.Network_Services_Menu,
                 object_storage_menu.Object_Storage_Services_Menu
                 ]

    def do_show_services(self, args):
        """Prints the current state of services """
        print 'Not implemented yet'




