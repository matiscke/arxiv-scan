"""Miscellaneous function which don't fit in other modules"""

def load_html(address):
    ''' Load content from website'''
    kwargs = {}
    try:
        from ssl import create_default_context
        from urllib.request import urlopen  # python 3

        # DeprecationWarning: cafile, capath and cadefault are deprecated
        # kwargs['context'] = create_default_context(cafile=CAFILE)
    except ImportError:
        from urllib2 import urlopen  # python 2

        # kwargs['cafile'] = CAFILE
    f = urlopen(address, **kwargs)
    return f.read()
