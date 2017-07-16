#!/usr/bin/python -OO
'''
implement local website http://myturn/

Copyright 2015-2016 John Otis Comeau <jc@unternet.net>
distributed under the terms of the GNU General Public License Version 3
(see COPYING)

must first mate a local IP address with the name `myturn` in /etc/hosts, e.g.:

127.0.1.125 myturn
'''
from __future__ import print_function
import sys, os, urllib2, logging, pwd, subprocess, site, cgi
try:  # command-line testing won't have module available
    import uwsgi
except ImportError:
    uwsgi = type('uwsgi', (), {'opt': {}})  # object with empty opt attribute
logging.basicConfig(level = logging.DEBUG if __debug__ else logging.INFO)
logging.debug('uwsgi.opt: %s' % repr(uwsgi.opt))
MAXLENGTH = 1024 * 1024  # maximum size in bytes of markdown source of post
HOMEDIR = pwd.getpwuid(os.getuid()).pw_dir
DATADIR = uwsgi.opt.get('check_static', '/var/www/myturn')
THISDIR = os.path.dirname(sys.argv[0]) or os.path.abspath('.')
logging.debug('HOMEDIR: %s' % HOMEDIR)
logging.debug('USER_SITE: %s' % site.USER_SITE)
USER_CONFIG = os.path.join(HOMEDIR, 'etc', 'myturn')
PRIVATE_KEY = os.path.join(USER_CONFIG, 'myturn.private.pem')
PUBLIC_KEY = os.path.join(USER_CONFIG, 'myturn.public.pem')
MIMETYPES = {'png': 'image/png', 'ico': 'image/x-icon', 'jpg': 'image/jpeg',
             'jpeg': 'image/jpeg',}
FILETYPES = [
    'directory',
    'md',
    'url',
    'txt',
    'html',
    'css',
] + MIMETYPES.keys()

def server(env = None, start_response = None):
    '''
    primary server process, sends page with current groups list
    '''
    logging.debug('env: %s' % repr(env))
    start = DATADIR
    logging.debug('start: %s' % start)
    path = (env.get('HTTP_PATH', env.get('REQUEST_URI', '/'))).lstrip('/')
    if not path:
        mimetype = 'text/html'
        page = read(os.path.join(start, 'index.html'))
        print page  # FIXME: first load groups
    else:
        page, mimetype = render(path)
    start_response('200 groovy', [('Content-type', mimetype)])
    return page

def render(pagename, standalone=False):
    '''
    Return content with Content-type header
    '''
    if pagename.endswith('.html'):
        return read(pagename), 'text/html'
    elif not pagename.endswith(('.png', '.ico', '.jpg', '.jpeg')):
        # assume plain text
        return ('<div class="post">%s</div>' % cgi.escape(
            read(pagename, maxread=32768)), 'text/plain')
    elif standalone:
        return (read(pagename, maxread=(10 * 1024 * 1024),
            MIMETYPES[os.path.splitext(pagename)[1]])
    else:
        return '', None

def read(filename):
    '''
    Return contents of a file
    '''
    with open(filename) as infile:
        return infile.read()
if __name__ == '__main__':
    print('\n'.join(example_client(os.environ, lambda *args: None)))
