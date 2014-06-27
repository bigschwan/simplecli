__author__ = 'clarkmatthew'



class Namespace(object):
    """
    Convert dict (if provided) into attributes and return a somewhat
    generic object
    """
    def __init__(self, newdict=None):
        if newdict:
            for key in newdict:
                value = newdict[key]
                try:
                    if isinstance(value, dict):
                        setattr(self, Namespace(value), key)
                    else:
                        setattr(self, key, value)
                except:
                    print '"{0}" ---> "{1}" , type: "{2}"'.format(key,
                                                                 value,
                                                                 type(value))
                    raise