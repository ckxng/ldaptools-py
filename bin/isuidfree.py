#!/usr/bin/env python3
'''check if a uid is free within a basedn'''

# this script might be called from the project directory, in cases where
# the ldaptools module has not been "installed". This inserts the 
# project directory into python's path, so the module can be found
from pathlib import Path
from sys import exit, path
project = str(Path(__file__).resolve().parents[1])
path.insert(0, project)

from ldaptools import connect, argparser

def isuidfree(conn, uid, base):
    '''check if a UID is free within a particular search base

    Parameters:
    conn(object): a ldap3 connection object
    uid(int): a numeric UID to check posix users for a free uid
    base(string): the basedn to search

    Returns two values in a tuple:
    True if the uid is free, False if a user already has it
    array of dicts containing matching responses
    '''
    status, _, response, _ = conn.search(
            search_base=base,
            search_filter='(uidNumber=%s)'%uid,
            attributes=['uidNumber'])

    # returns false if status is true(result found)
    # returns true if status is false(result not found)
    return (not status, response)

if __name__ == '__main__':
    parser = argparser('check if uid is free')
    parser.add_argument('--uid',
            type=int,
            required=True,
            help='uid to check')
    parser.add_argument('--base',
            default='ou=People,dc=company,dc=com',
            help='OU to search (ex: ou=People,dc=company,dc=com)')
    args = parser.parse_args()
    conn = connect(args=args)

    free, response = isuidfree(conn, args.uid, args.base)
    print(free)
    if(args.verbose):
        print(response)
    if(not free):
        exit(1)

