#!/usr/bin/python3 -OO
'''
implement local website http://myturn/

Copyright 2017 John Otis Comeau <jc@unternet.net>
distributed under the terms of the GNU General Public License Version 3
(see COPYING)

must first mate a local IP address with the name `myturn` in /etc/hosts, e.g.:

127.0.1.125 myturn
'''
from __future__ import print_function
import sys, os, urllib.request, urllib.error, urllib.parse, logging, pwd
import subprocess, site, cgi, datetime, urllib.parse, threading, copy, json
import uuid
from collections import defaultdict, OrderedDict
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
THISDIR = os.path.dirname(uwsgi.opt.get('wsgi-file', b'').decode())
APPDIR = (uwsgi.opt.get('check_static', b'').decode() or
          os.path.join(THISDIR, 'html'))
MIMETYPES = {'png': 'image/png', 'ico': 'image/x-icon', 'jpg': 'image/jpeg',
             'jpeg': 'image/jpeg',}
DATA = {
    'groups': {},
}
SESSIONS = {}  # threads linked with session keys go here
EXPECTED_ERRORS = (NotImplementedError, ValueError, KeyError, IndexError)

def findpath(env):
    '''
    locate directory where files are stored, and requested file
    '''
    #logging.debug('env: %s' % repr(env))
    start = APPDIR
    logging.debug('findpath: start: %s' % start)
    path = env.get('HTTP_PATH')
    #logging.debug('path, attempt 1: %s', path)
    path = path or env.get('REQUEST_URI')
    #logging.debug('path, attempt 2: %s', path)
    path = (path or '/').lstrip('/')
    logging.debug('findpath: should not be None at this point: "%s"', path)
    return start, path

def loadpage(webpage, path, data):
    '''
    input template and populate the HTML with data array

    eventually client-side JavaScript will perform many of these functions.
    '''
    parsed = html.fromstring(webpage)
    if 'groups' in data:
        groups = populate_grouplist(parsed, data)
    else:
        groups = None
    # only show load indicator if no path specified;
    # get rid of meta refresh if path has already been chosen
    if path == '':
        hide_except('loading', parsed)
        return html.tostring(parsed).decode()
    else:
        for tag in parsed.xpath('//meta[@http-equiv="refresh"]'):
            tag.getparent().remove(tag)
    if 'text' in data:
        parsed.xpath('//div[@id="error-text"]')[0].append(data['text'])
        hide_except('error', parsed)
    elif 'joined' in data.get('postdict', {}):
        logging.debug('found "joined": %s', data['postdict'])
        hide_except('session', parsed)
    elif groups:
        hide_except('joinform', parsed)
    else:
        hide_except('groupform', parsed)
    return html.tostring(parsed).decode()

def populate_grouplist(parsed, data):
    '''
    fill in 'select' element with options for each available group
    '''
    grouplist = parsed.xpath('//select[@name="group"]')
    logging.debug('populate_grouplist: %s', grouplist)
    grouplist = grouplist[0]
    # sorting a dict gives you a list of keys
    groups = sorted(data['groups'],
                    key=lambda g: data['groups'][g]['timestamp'])
    for group in groups:
        newgroup = builder.OPTION(group, value=group)
        grouplist.append(newgroup)
    # make newest group the "selected" one
    # FIXME: for someone who just created a group, mark *that* one selected
    for group in grouplist.getchildren():
        try:
            del group.attrib['selected']
        except KeyError:
            pass
    grouplist[-1].set('selected', 'selected')
    return groups

def hide_except(keep, tree):
    '''
    set "display: none" for all sections of the page we don't want to see
    '''
    for page in tree.xpath('//div[@class="body"]'):
        if not page.get('id').startswith(keep):
            page.set('style', 'display: none')
        elif 'style' in page.attrib:
            del page.attrib['style']

def server(env = None, start_response = None):
    '''
    primary server process, sends page with current groups list
    '''
    status_code, mimetype, page = '500 Server error', 'text/html', '(Unknown)'
    start, path = findpath(env)
    try:
        data = handle_post(env)
        logging.debug('server: data: %s', data)
        if path in ('', 'noscript', 'app'):
            page = loadpage(read(os.path.join(start, 'index.html')), path, data)
            status_code = '200 OK'
        elif path == 'status':
            page = cgi.escape(json.dumps(data))
            status_code = '200 OK'
        else:
            try:
                page, mimetype = render(os.path.join(start, path))
                status_code = '200 OK'
            except (IOError, OSError) as filenotfound:
                status_code = '404 File not found'
                page = '<h1>No such page: %s</h1>' % str(filenotfound)
    except UserWarning as request:
        if str(request) == 'Help requested':
            logging.debug('displaying help screen')
            text = read(os.path.join(THISDIR, 'README.md'))
            page = loadpage(read(os.path.join(start, 'index.html')), path,
                            {'text': builder.SPAN(cgi.escape(text))})
    except EXPECTED_ERRORS as failed:
        logging.debug('displaying error: "%r"', failed)
        page = loadpage(read(os.path.join(start, 'index.html')), path,
                        {'text': builder.SPAN(cgi.escape(repr(failed)))})
    start_response(status_code, [('Content-type', mimetype)])
    logging.debug('page: %s', page[:128])
    return [page.encode('utf8')]

def handle_post(env):
    '''
    process the form submission and return data structures

    note what dict(parse_qsl(formdata)) does:

    >>> from urllib.parse import parse_qsl
    >>> parse_qsl('a=b&b=c&a=d&a=e')
    [('a', 'b'), ('b', 'c'), ('a', 'd'), ('a', 'e')]
    >>> OrderedDict(_)
    {'a': 'e', 'b': 'c'}
    >>>

    so only use it where you know that no key will have more than
    one value.

    parse_qs will instead return a dict of lists.
    '''
    uwsgi.lock()  # lock access to DATA global
    worker = getattr(uwsgi, 'worker_id', lambda *args: None)()
    DATA['handler'] = (worker, env.get('uwsgi.core'))
    timestamp = datetime.datetime.utcnow().isoformat()
    try:
        if env.get('REQUEST_METHOD') != 'POST':
            return copy.deepcopy(DATA)
        posted = urllib.parse.parse_qsl(env['wsgi.input'].read().decode())
        DATA['postdict'] = postdict = dict(posted)
        logging.debug('handle_post: %s, postdict: %s', posted, postdict)
        # [groupname, total, turn] and submit=Submit if group creation
        # [username, group] and submit=Join if joining a group
        postdict['timestamp'] = timestamp
        if not postdict.get('session_key'):
            postdict['session_key'] = uuid.uuid4().hex
            logging.debug('set session_key = %s', postdict['session_key'])
        try:
            buttonvalue = postdict['submit']
        except KeyError:
            raise ValueError('No "submit" button found')
        update_session(postdict)
        if buttonvalue == 'Join':
            # username being added to group
            # don't allow if name already in group
            groups = DATA['groups']
            logging.debug('processing Join: %s', postdict)
            username = postdict.get('username', '')
            group = postdict.get('group', '')
            postdict['success'] = False  # assume a problem
            if not username:
                raise ValueError('Name field cannot be empty')
            elif group in groups:
                if username in groups[group]['participants']:
                    raise ValueError('"%s" is already a member of %s' % (
                                     username, group))
                groups[group]['participants'][username] = {
                    'timestamp': timestamp}
                if 'session' not in groups[group]:
                    groups[group]['session'] = {'start': timestamp}
                postdict['joined'] = True
            # else group not in groups, no problem, return to add group form
            data = copy.deepcopy(DATA)
            return data
        elif buttonvalue == 'Submit':
            # groupname, total (time), turn (time) being added to groups
            # don't allow if groupname already being used
            groups = DATA['groups']
            group = postdict['groupname']
            if not group in groups:
                groups[group] = postdict
                groups[group]['participants'] = {}
                return copy.deepcopy(DATA)
            else:
                raise ValueError((
                    'Group {group[groupname]} already exists with total time '
                    '{group[total]} minutes and turn time '
                    '{group[turn]} seconds')
                    .format(group=groups[group]))
        elif buttonvalue == 'OK':
            # affirming receipt of error message or Help screen
            return copy.deepcopy(DATA)
        elif buttonvalue == 'Help':
            raise UserWarning('Help requested')
        elif buttonvalue == 'My Turn':
            # attempting to speak in ongoing session
            # this could only be reached by browser in which JavaScript did
            # not work properly in taking over default actions
            logging.debug('env: %s', env)
            raise NotImplementedError(
                'Browser \'%s\' incompatible with script' %
                env.get('HTTP_USER_AGENT', '(unknown)'))
        else:
            raise ValueError('Unknown form submitted')
    finally:
        uwsgi.unlock()

def update_session(postdict):
    '''
    simple implementation of user sessions

    this is for keeping state between client and server, this is *not*
    the same as discussion sessions!

    another thread should go through and remove expired sessions
    '''
    # FIXME: this session mechanism can only be somewhat secure with https
    timestamp = postdict['timestamp']
    if 'session_key' in postdict and postdict['session_key']:
        session_key = postdict['session_key']
        if 'username' in postdict and postdict['username']:
            username = postdict['username']
            if session_key in SESSIONS:
                if SESSIONS[session_key]['username'] != username:
                    raise ValueError('Session belongs to "%s"' % username)
                else:
                    SESSIONS[session_key]['updated'] = postdict['timestamp']
            else:
                SESSIONS[session_key] = {
                    'timestamp': timestamp,
                    'updated': timestamp,
                    'username': username}
        else:
            logging.debug('no username associated with session %s', session_key)
    else:
        logging.warn('no session_key in POST')

def render(pagename, standalone=True):
    '''
    Return content with Content-type header
    '''
    logging.debug('render(%s, %s) called', pagename, standalone)
    if pagename.endswith('.html'):
        logging.debug('rendering static HTML content')
        return (read(pagename), 'text/html')
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
    logging.debug('read: returning contents of %s', filename)
    with open(filename) as infile:
        data = infile.read()
        logging.debug('data: %s', data[:128])
        return data

if __name__ == '__main__':
    print(server(os.environ, lambda *args: None))
