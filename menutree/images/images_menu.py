__author__ = 'clarkmatthew'


from simplecli.basemenu import BaseMenu, CliError
from simplecli.namespace import Namespace
from simplecli.config import Config
import os
import json
import re
import copy
import operator
import requests
from texttable import Texttable
from prettytable import PrettyTable


class Images_Menu(BaseMenu):
    name = 'images_menu'
    _summary = 'Image Utilities Menu'
    _submenus = []
    #_catalog_url = "http://emis.eucalyptus.com/catalog"
    #_fast_emi_script_url = "eucalyptus.com/install-emis"

    def _setup(self):
        try:
            config = self.env.get_config_from_namespace(namespace_name='main',
                                                        config_name='images')
        except ValueError:
            config = None
        if not config:
            config = Config(config_file_path=self.env.simplecli_config_file,
                            name='images')
            config.catalog_url = "http://emis.eucalyptus.com/catalog"
            config.fast_emi_script_url = "eucalyptus.com/install-emis"
            config._update_from_file()
            self.env.add_config_to_namespace(namespace_name='main',
                                             config=config,
                                             create=True)
        self._catalog_url = config.catalog_url
        self._fast_emi_script_url = config.fast_emi_script_url

    def do_install_quick_image(self, args):
        """
        Use Eucalyptus provided Images to quickly install sample
        EMI images on your cloud. Requires the following variables to be
        set either in the current user's environment of the environment/config
        of this CLI shell...
        """
        ret = 1
        scriptname = 'fast-emis.py'
        url = self._fast_emi_script_url
        commands = ['curl -sL {0} > {1}'.format(url, scriptname),
                    'wget {1} --no-check-certificate -O {0}'
                        .format(scriptname, url)]
        for command in commands:
            base_command = command.split()[0]
            if not os.system('which ' + str(base_command)):
                command = str(command)
                ret = os.system(command)
                if ret:
                    self.eprint('Command:"{0}" failed with code:"{1}"'
                                       .format(command, ret))
                break
        if os.path.isfile(scriptname):
            self.oprint('Running script:' + scriptname)
            ret = os.system('python ' + str(scriptname))
        else:
            self.eprint('Could not find script("{0}") to run to intall image')
            ret = ret or 1
        return ret


    def do_show_emi_page(self, args):
        """
        Attempts to render emis.eucalyptus.com into text for quick reference.
        """
        try:
            import html2text
        except:
            self.eprint('Could not load html2text, '
                        'try installing with pip install html2text')
        else:
            r = requests.get("http://emis.eucalyptus.com")
            buf = ""
            doc = html2text.html2text(r.text)
            for line in doc.splitlines():
                line = str(line)
                if line.startswith('#'):
                    line =self._color(line)
                buf += line + "\n"
            self.oprint(buf)

    def do_show_urls(self, args):
        """
        Shows URLs currently used for local image utlities/cmds
        """
        self.oprint(self._color("\n\t***** CURRENT IMAGE MENU URLS *****"))
        tab = Texttable()
        table = [['NAME', 'URL']]
        table.append(['FAST EMI SCRIPT', self._fast_emi_script_url])
        table.append(['IMAGE CATALOG', self._catalog_url])
        tab.add_rows(table)
        tab.set_cols_dtype(['t','t'])
        self.oprint(tab.draw())


    def do_set_catalog_url(self, url):
        """
        Sets the image catalog url used by this menu
        """
        if url:
            self.oprint('Setting catalog url to:' + str(url))
            self._catalog_url = str(url)

    def do_set_fast_emi_script(self, url):
        """
        Sets the fast emi script url used by this menu
        """
        if url:
            self.oprint('Setting fast emi script url to:' + str(url))
            self._fast_emi_script_url = str(url)


    def do_show_catalog(self, filtersarg):
        """
        Shows a list of images and their  brief summaries.
        If no filter is provided all images will be shown.
        Filters are in the format:
        attribute_name= <-op>:value1, <-op>:value2, ...
        Where options for <-op>  are either operators or reg ex:
        Available operators:
            -eq, -ge, -gt, -le, -lt, etc.
        Available regex:
            -re.search, -re.match, etc..
        default operator is -eq (equal)

        Usage: show_catalog [filters]
        Examples:
                show_catalog os=cirros,centos

                show_catalog date=-gt:20120517102326 os=ubuntu size=-lt:5

                show_catalog description:-re.search:'random text'
        """
        filter_list = filtersarg.split()
        filters = {}
        for item in filter_list:
            try:
                filter, values = item.split('=')
                values = values.split(',')
                filters[filter] = values
            except Exception as e:
                raise CliError(
                    'Could not parse filter argument:"{0}", error:"{1}"'
                    .format(item, str(e)))
        # Get the image catalog from the catalog url and create image_j
        # objects from the json provided. Use image_j versioned validators
        # to verify json and/or provide sane defaults, etc..
        r = requests.get(self._catalog_url)
        j = json.loads(r.text)
        images = []
        if 'images' in j:
            for image in j['images']:
                images.append(CatalogImage(image))
        show_images = copy.copy(images)
        for image in images:
            for filter in filters:
                match = False
                # See if the image has an attribute that matches
                # Note: Replace '-' with '_' for image attribute lookups
                # as they are renamed in the class
                image_attr = getattr(image, str(filter).replace('-','_'))
                if image_attr:
                    # iterate through any filters provided from the command line
                    # if an image fails to meet the criteria of any filter
                    # it will be removed from the display list
                    for value in filters[filter]:
                        # Check if filter is using a normal
                        # operator ie: -eq, -gt, ex: filter=-eq:words
                        op = re.search("^-+\w\w:", value)
                        if op:
                            mod = operator
                        else:
                            # Check if filter is using reg ex in filter
                            # ie: filter=-re.search:expression
                            op = re.search("^-+re.\w+:", value)
                            if op:
                                mod = re
                        if op:
                            opstr = op.group()
                            value = value.replace(opstr, '')
                            op = opstr.replace('-','').strip(':')
                            op = op.replace('re.','')
                            op = getattr(mod, op, None)
                            if not op:
                                self.eprint('Warning: operator "{0}" ({1}) '
                                            'not valid? for mod:"{2}"'
                                            .format(op, opstr, mod))
                        # If an operator was not provided or was invalid,
                        # use the default op for 'equals'
                        op = op or operator.eq
                        # This can be improved to do more complex lookups and
                        # inspection, for now only handling lists and
                        # instances.
                        if isinstance(image_attr, list):
                            if value in image_attr:
                                match = True
                                break
                        else:
                            # Evaluate each item against the filters...
                            if getattr(op, '__module__', None) == 'operator':
                                # Using operator.<func>
                                try:
                                    if op(float(image_attr), float(value)):
                                        match = True
                                        break
                                except:
                                    if op(image_attr, value):
                                        match = True
                                        break
                            else:
                                # Using re.<func>
                                if op(value, str(image_attr)):
                                    match = True
                                    break
                if not match:
                    show_images.remove(image)
                    break
        # Now format and print the images...
        if not show_images:
            self.eprint('No images for filters:' + str(filters))
        for image in show_images:
            summary = image.get_summary_full()
            if summary:
                line_len = len(summary.splitlines()[0])
                line = ""
                for x in xrange(0, line_len):
                    line += '#'
                line += '\n'
                header = "\n\n" + line
                header += ('{0}\n'
                           .format(self._color(image.name).center(line_len)))
                header += line
                self.oprint(header)
                self.oprint(image.get_summary_full())




class CatalogImage(Namespace):
    '''
    Populate attributes from provided JSON string, or dict.
    If version is provided attempt to do some basic verification on the
    attributes against the version method matching.
    If version is not provided or is not found below then the default
    validation method will be used.
    The validation methods can be used for type casting, or further building
    out the image instance...

    Note: JSON attributes may need the chars converted from  '-' to '_' when
     creating the image attributes.
    '''

    def __init__(self, j_dict):
        # if j_dict is a string then assume it's json and attempt to convert it
        # to a dict
        if isinstance(j_dict, str):
            j_dict = json.loads(j_dict)
        #Load all attributes from dict into self...
        self.version = None
        super(CatalogImage, self).__init__(newdict=j_dict)
        #See if there's a validation/init method for this specific version...
        validation_method = None
        if not self.version:
            validation_method = getattr(
                self, '_validation_method_' + j_dict['version'])
        if not validation_method:
            self._validate_default(j_dict)
        else:
            validation_method(j_dict)

    def _validate_default(self, j_dict):
        self._validate_method_1(j_dict)

    def _validate_method_1(self, j_dict):
        '''
        Intends to validate a minimum set of attributes provided by the
        dict/json.
        '''
        self.architecture = j_dict['architecture']
        self.contact = j_dict['contact']
        self.date = j_dict['date']
        self.description = j_dict['description']
        self.hypervisors_supported = j_dict['hypervisors-supported']
        self.name = j_dict['name']
        self.os = j_dict['os']
        self.recipe = j_dict['recipe']
        self.single_kernel = j_dict['single-kernel']
        self.stamp = j_dict['stamp']
        self.url = j_dict['url']
        self.version = j_dict['version']

    def get_summary_full(self):
        table = [['IMAGE ATTRIBUTE', 'VALUE']]
        tab = Texttable()
        tab.set_cols_dtype(['t','t'])
        for key in self.__dict__:
            table.append([str(key), str(self.__dict__[key])])
        tab.add_rows(table)
        return tab.draw()







