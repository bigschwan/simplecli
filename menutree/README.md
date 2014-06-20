menutree
==========

Currently Menu tree is an example set of menus both statically linked and/or 
using the simplecli plugin discovery mechanism. 
This is intended to show examples of how a menu environment can be created. 


basic usage:
------------
To Run the provided menutree run: 
python example_start.py



Example:
-------------
```
### python example_start.py 
*** Home Menu ***
home_menu#
back           clear          help           home           images_menu    quit           sample_cmd     services_menu  show_cli_env   tests_menu     
home_menu#images_menu
*** images_menu ***
home_menu>images_menu# ?
Command or syntax not recognized: "?"

Documented commands (type help <topic>):
========================================
back   home                 sample_cmd           show_catalog   show_urls
clear  install_quick_image  set_catalog_url      show_cli_env 
help   quit                 set_fast_emi_script  show_emi_page

  *** SUB MENUS ***

  *** IMAGES_MENU COMMANDS ***
  install_quick_image --> "Use Eucalyptus provided Images to quickly install sample"
  set_catalog_url     --> "Sets the image catalog url used by this menu"
  set_fast_emi_script --> "Sets the fast emi script url used by this menu"
  show_catalog        --> "Shows a list of images and their  brief summaries."
  show_emi_page       --> "Attempts to render emis.eucalyptus.com into text for quick reference."
  show_urls           --> "Shows URLs currently used for local image utlities/cmds"

  *** BASE COMMANDS ***
  back                --> "Go Back one level in menu tree"
  clear               --> "Clear current screen"
  help                --> "List available commands with "help" or detailed help with "help cmd"."
  home                --> "Return to the home menu of the cli"
  quit                --> "Quits the program."
  sample_cmd          --> "Sample command for test purposes"
  show_cli_env        --> "show current cli environment variables"
home_menu>images_menu#show_catalog os=fedora,cirros hypervisors_supported=kvm, date=-gt:20140410025734
No images for filters:{'hypervisors_supported': ['kvm', ''], 'date': ['-gt:20140410025734'], 'os': ['fedora', 'cirros']}
home_menu>images_menu#show_catalog os=fedora,cirros hypervisors_supported=kvm, date=-gt:20140410025733


###############################################################################
                              3839552141                             
###############################################################################
+--------------------------------------+--------------------------------------+
|           IMAGE ATTRIBUTE            |                VALUE                 |
+======================================+======================================+
| single-kernel                        | False                                |
+--------------------------------------+--------------------------------------+
| description                          | Fedora 18 1.7GB root - Hypervisor-   |
|                                      | Specific Kernel, 3.9.6-200.fc18      |
|                                      | kernel version; cloud-init enabled,  |
|                                      | ec2-user enabled, sudo rights;       |
|                                      | Selinux Enabled; euca2ools 2.1.3     |
|                                      | installed                            |
+--------------------------------------+--------------------------------------+
| url                                  | starter-emis/euca-fedora18-ec2user-2 |
|                                      | 014.04.09-x86_64.tgz                 |
+--------------------------------------+--------------------------------------+
| single_kernel                        | False                                |
+--------------------------------------+--------------------------------------+
| hypervisors-supported                | [u'kvm']                             |
+--------------------------------------+--------------------------------------+
| recipe                               | fedora-based                         |
+--------------------------------------+--------------------------------------+
| contact                              | harold.spencer.jr@eucalyptus.com     |
+--------------------------------------+--------------------------------------+
| hypervisors_supported                | [u'kvm']                             |
+--------------------------------------+--------------------------------------+
| stamp                                | 89cf-3f6f                            |
+--------------------------------------+--------------------------------------+
| version                              | starter                              |
+--------------------------------------+--------------------------------------+
| architecture                         | x86_64                               |
+--------------------------------------+--------------------------------------+
| date                                 | 20140410025734                       |
+--------------------------------------+--------------------------------------+
| os                                   | fedora                               |
+--------------------------------------+--------------------------------------+
| name                                 | 3839552141                           |
+--------------------------------------+--------------------------------------+


###############################################################################
                              1298440207                             
###############################################################################
+--------------------------------------+--------------------------------------+
|           IMAGE ATTRIBUTE            |                VALUE                 |
+======================================+======================================+
| username                             | fedora                               |
+--------------------------------------+--------------------------------------+
| single-kernel                        | False                                |
+--------------------------------------+--------------------------------------+
| description                          | Fedora 20 2GB root, Hypervisor-      |
|                                      | Specific Kernel; cloud-init enabled, |
|                                      | fedora user enabled, sudo rights;    |
|                                      | SeLinux Enabled                      |
+--------------------------------------+--------------------------------------+
| url                                  | starter-emis/euca-fedora20-fedora-20 |
|                                      | 14.04.09-x86_64.tgz                  |
+--------------------------------------+--------------------------------------+
| stamp                                | e31d-f404                            |
+--------------------------------------+--------------------------------------+
| hypervisors-supported                | [u'kvm']                             |
+--------------------------------------+--------------------------------------+
| recipe                               | fedora-based                         |
+--------------------------------------+--------------------------------------+
| contact                              | kushal@eucalyptus.com                |
+--------------------------------------+--------------------------------------+
| hypervisors_supported                | [u'kvm']                             |
+--------------------------------------+--------------------------------------+
| tested                               | passed                               |
+--------------------------------------+--------------------------------------+
| version                              | starter                              |
+--------------------------------------+--------------------------------------+
| architecture                         | x86_64                               |
+--------------------------------------+--------------------------------------+
| single_kernel                        | False                                |
+--------------------------------------+--------------------------------------+
| date                                 | 20140410025734                       |
+--------------------------------------+--------------------------------------+
| os                                   | fedora                               |
+--------------------------------------+--------------------------------------+
| name                                 | 1298440207                           |
+--------------------------------------+--------------------------------------+
home_menu>images_menu#
```
