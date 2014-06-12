simplecli
==========

Simple Python CLI framework for presenting cloud related utilities. 
Simple CLI uses python's Cmd() and extends it to provide an interactive menu tree. 



install:
========
(sudo) python setup.py install


basic usage:
============
To Run the provided menutree run: 
python simplecli/start.py

This should produce an interactive shell similar to the following sample:

### simplecli/start.py 
*** Home Menu ***
home_menu#?
Command or syntax not recognized: "?"

Documented commands (type help <topic>):
========================================
back  clear  help  home  quit  services_menu  show_cli_env  tests_menu

  *** SUB MENUS ***
  services_menu --> "(MENU ITEM) Services Menu"
  tests_menu    --> "(MENU ITEM) Tests Menu"

  *** COMMANDS ***
  back          --> "Go Back to last menu"
  clear         --> "Clear current screen"
  help          --> "List available commands with "help" or detailed help with "help cmd"."
  home          --> "Return to the home menu of the cli"
  quit          --> "Quits the program."
  show_cli_env  --> "show current cli environment variables"
home_menu#
home_menu#tests_menu
*** tests_menu ***
home_menu>tests_menu#?
Command or syntax not recognized: "?"

Documented commands (type help <topic>):
========================================
back                clear  home               object_storage_menu  show_cli_env
block_storage_menu  help   network_test_menu  quit               

  *** SUB MENUS ***
  block_storage_menu  --> "(MENU ITEM) Block Storage Menu"
  network_test_menu   --> "(MENU ITEM) Network Tests Menu"
  object_storage_menu --> "(MENU ITEM) Object Storage Menu"

  *** COMMANDS ***
  back                --> "Go Back to last menu"
  clear               --> "Clear current screen"
  help                --> "List available commands with "help" or detailed help with "help cmd"."
  home                --> "Return to the home menu of the cli"
  quit                --> "Quits the program."
  show_cli_env        --> "show current cli environment variables"
home_menu>tests_menu#


