#!/usr/bin/python3
'''
convert json log made by myturn.py into cvs
'''
import sys, os, json, fcntl, logging, csv, glob

def process(filename):
    '''
    read and lock json file, convert to cvs, and delete
    '''
    timestamp = os.path.splitext(os.path.basename(filename))[0]
    groupname = os.path.basename(os.path.dirname(filename))
    print('report for group "%s" conversation ending at %s' % (
          groupname, timestamp))
    with open(filename) as infile:
        try:
            fcntl.flock(infile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as lockfail:
            logging.error('failed locking %s: %s', filename, lockfail.errno)
            return
        data = json.loads(infile.read())
        writer = csv.writer(sys.stdout)
        for record in data:
            for username in record:
                for start, stop in record[username]:
                    writer.writerow([username, start, stop or timestamp])
        os.unlink(filename)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        filenames = glob.glob(
            '/usr/local/jcomeauictx/pyturn-*/statistics/*/*.json'
        )
    for filename in filenames:
        process(filename)
