__author__ = 'clarkmatthew'


class BaseEnv():
    """
    The intention of this class is to hold environment variables which might be
    global to the tool, it's menus, and the command executed within.
    """
    def __init__(self):
        self.default_username = None
        self.default_password = None
        self.default_sshkey = None
        self.credpath = None
        self.config_file = None
        self.access_key = None
        self.secret_key = None
        self.account_id = None
        self.account_name = None
        self.user_name = None
        self.debug=True
        self.default_input = None # ie stdin
        self.default_output = None # ie stdout or stderr
        self.prompt_method = None # define this method as a global way to
                                  # construct menu prompts
        self.path_delimeter = ">" # Used for constructing the default prompt
                                  # and displayed path string(s)

    def read_config(self, path):
        print 'not implemented yet'

    def set_config(self, key, value):
        print 'not implemented yet'

    def create_config(self, path):
        print 'not implemented yet'





