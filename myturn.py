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
import sys, os, urllib2, logging, pwd, subprocess, site, cgi, errno
from lxml import html
from lxml.html import builder
try:  # command-line testing won't have module available
    import uwsgi
except ImportError:
    uwsgi = type('uwsgi', (), {'opt': {}})  # object with empty opt attribute
logging.basicConfig(level = logging.DEBUG if __debug__ else logging.INFO)
logging.debug('uwsgi.opt: %s', repr(uwsgi.opt))
#logging.debug('sys.argv: %s', sys.argv)  # only shows [uwsgi]
#logging.debug('current working directory: %s', os.path.abspath('.'))  # '/'
# so we can see that sys.argv and PWD are useless for uwsgi operation
HOMEDIR = pwd.getpwuid(os.getuid()).pw_dir
THISDIR = os.path.dirname(uwsgi.opt.get('wsgi-file', ''))
APPDIR = uwsgi.opt.get('check_static', os.path.join(THISDIR, 'html'))
logging.debug('HOMEDIR: %s' % HOMEDIR)
logging.debug('USER_SITE: %s' % site.USER_SITE)
USER_CONFIG = os.path.join(HOMEDIR, 'etc', 'myturn')
PRIVATE_KEY = os.path.join(USER_CONFIG, 'myturn.private.pem')
PUBLIC_KEY = os.path.join(USER_CONFIG, 'myturn.public.pem')
MIMETYPES = {'png': 'image/png', 'ico': 'image/x-icon', 'jpg': 'image/jpeg',
             'jpeg': 'image/jpeg',}
DATA = {
    'groups': {}
}

def server(env = None, start_response = None):
    '''
    primary server process, sends page with current groups list
    '''
    logging.debug('env: %s' % repr(env))
    start = APPDIR
    logging.debug('start: %s' % start)
    path = env.get('HTTP_PATH')
    logging.debug('path, attempt 1: %s', path)
    path = path or env.get('REQUEST_URI')
    logging.debug('path, attempt 2: %s', path)
    path = (path or '/').lstrip('/')
    logging.debug('path should not be None at this point: "%s"', path)
    if not path:
        mimetype = 'text/html'
        page = read(os.path.join(start, 'index.html'))
        parsed = html.fromstring(page)
        if env and env.get('wsgi.input'):
            logging.debug('POST: %s', cgi.parse_qsl(env['wsgi.input'].read()))
            timestamp = datetime.datetime.utcnow()
        grouplist = parsed.xpath('//select[@name="group"]')
        logging.debug('grouplist: %s', grouplist)
        grouplist = grouplist[0]
        # sorting a dict gives you a list of keys
        groups = sorted(DATA['groups'], key=lambda g: g['timestamp'])
        for group in groups:
            newgroup = builder.OPTION(group, value=group)
            grouplist.append(newgroup)
        # make newest group the "selected" one
        for group in grouplist.getchildren():
            try:
                del group.attrib['selected']
            except KeyError:
                pass
        grouplist[-1].set('selected', 'selected')
        page = html.tostring(parsed)
    else:
        try:
            page, mimetype = render(os.path.join(start, path))
        except (IOError, OSError) as filenotfound:
            start_response('404 File not found',
                           [('Content-type', 'text/html')])
            return '<h1>No such page: %s</h1>' % str(filenotfound)
    start_response('200 groovy', [('Content-type', mimetype)])
    return page

def render(pagename, standalone=True):
    '''
    Return content with Content-type header
    '''
    logging.debug('render(%s, %s) called', pagename, standalone)
    if pagename.endswith('.html'):
        logging.debug('rendering static HTML content')
        return read(pagename), 'text/html'
    elif not pagename.endswith(('.png', '.ico', '.jpg', '.jpeg')):
        # assume plain text
        logging.warn('app is serving %s instead of nginx', pagename)
        return (read(pagename), 'text/plain')
    elif standalone:
        logging.warn('app is serving %s instead of nginx', pagename)
        return (read(pagename),
            MIMETYPES.get(os.path.splitext(pagename)[1], 'text/plain'))
    else:
        logging.error('not standalone, and no match for filetype')
        raise OSError('File not found: %s' % pagename)

def read(filename):
    '''
    Return contents of a file
    '''
    logging.debug('returning contents of %s', filename)
    with open(filename) as infile:
        return infile.read()

if __name__ == '__main__':
    print(server(os.environ, lambda *args: None))
