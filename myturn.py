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
import sys, os, urllib2, logging, pwd, subprocess, site, cgi, datetime
import urlparse, threading, copy
from collections import defaultdict, OrderedDict
from StringIO import StringIO
from lxml import html
from lxml.html import builder
logging.basicConfig(level = logging.DEBUG if __debug__ else logging.INFO)
LOCK = threading.Lock()
try:  # command-line testing won't have module available
    import uwsgi
    logging.debug('uwsgi: %s', dir(uwsgi))
except ImportError:
    uwsgi = type('uwsgi', (), {'opt': {}})  # object with empty opt attribute
    uwsgi.lock = LOCK.acquire
    uwsgi.unlock = LOCK.release
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
    'groups': {},
}
EXPECTED_ERRORS = (NotImplementedError, ValueError, KeyError, IndexError)

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
        try:
            data = handle_post(env)
        except EXPECTED_ERRORS as failed:
            start_response('500 Server Error', [('Content-type', 'text/html')])
            return cgi.escape(str(failed))
        grouplist = parsed.xpath('//select[@name="group"]')
        logging.debug('grouplist: %s', grouplist)
        grouplist = grouplist[0]
        # sorting a dict gives you a list of keys
        groups = sorted(data['groups'], key=lambda g: g['timestamp'])
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
    start_response('200 OK', [('Content-type', mimetype)])
    return page

def handle_post(env):
    '''
    process the form submission

    note what dict(parse_qsl(formdata)) does:

    >>> from urlparse import parse_qsl
    >>> parse_qsl('a=b&b=c&a=d&a=e')
    [('a', 'b'), ('b', 'c'), ('a', 'd'), ('a', 'e')]
    >>> OrderedDict(_)
    {'a': 'e', 'b': 'c'}
    >>>

    so only use it where you know that no key will have more than
    one value.
    '''
    uwsgi.lock()  # lock access to DATA global
    try:
        if env.get('REQUEST_METHOD') != 'POST':
            return copy.deepcopy(DATA)
        posted = urlparse.parse_qsl(formdata.read())
        postdict = dict(posted)
        logging.debug('posted: %s, postdict: %s', posted, postdict)
        # [name, total, turn] and submit=Submit if group creation
        # [name, group] and submit=Join if joining a group
        timestamp = datetime.datetime.utcnow()
        postdict['timestamp'] = timestamp
        try:
            buttonvalue = postdict.pop('submit')
        except KeyError:
            raise(ValueError('No "submit" button found'))
        if buttonvalue == 'Join':
            # name being added to group
            # don't allow if name already in group
            raise(NotImplementedError('Join not yet implemented'))
        elif buttonvalue == 'Submit':
            # group name, total (time), turn (time) being added to groups
            # don't allow if group name already being used
            groups = DATA['groups']
            group = postdict['name']
            if not group in groups:
                groups[group] = postdict
                return copy.deepcopy(DATA)
            else:
                raise(ValueError((
                    'Group {group[name]} already exists with total time '
                    '{group[total]} minutes and turn time '
                    '{group[turn]} seconds')
                    .format(group=groups[group])))
        else:
            raise(ValueError('Unknown form submitted'))
    finally:
        uwsgi.unlock()

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
        raise(OSError('File not found: %s' % pagename))

def read(filename):
    '''
    Return contents of a file
    '''
    logging.debug('returning contents of %s', filename)
    with open(filename) as infile:
        return infile.read()

if __name__ == '__main__':
    print(server(os.environ, lambda *args: None))
