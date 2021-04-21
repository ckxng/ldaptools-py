#!/usr/bin/env python3
'''print a user from within the OU'''

# this script might be called from the project directory, in cases where
# the ldaptools module has not been "installed". This inserts the 
# project directory into python's path, so the module can be found
from pathlib import Path
from sys import exit, path
project = str(Path(__file__).resolve().parents[1])
path.insert(0, project)

from ldaptools import connect, argparser
from pprint import pprint

def getuser(conn, username, base):
    '''returns a user from within the specified base

    Parameters:
    conn(object): a ldap3 connection object
    username(string): the posix username to search for (called uid in ldap)
    base(string): the basedn to search

    Returns two values in a tuple:
    True/False depending on whether a single matching user was found
    a user object or None if not found

    Raises:
    Exception if an unexpected state occurs
    ValueError if multiple objects match the query
    '''
    status, _, response, _ = conn.search(
            search_base=base,
            search_filter='(uid=%s)'%username,
            attributes=['*'])

    if(status): #we think we found something
        if(len(response)<1):
            raise Exception('for some reason status is false and response is 0... that should not happen')
        elif(len(response)>1):
            raise ValueError('too many responses were found (duplicate uid?)')
        return (status, response[0])

    # we did not find anything
    return (status, None)


def getuid(conn, uid, base):
    '''returns a user from within the specified base
 
    Parameters:
    conn(object): a ldap3 connection object
    uid(int): the posix uid to search for (called uiNumberd in ldap)
    base(string): the basedn to search
 
    Returns two values in a tuple:
    True/False depending on whether a single matching user was found
    a user object
 
    Raises:
    Exception if an unexpected state occurs
    ValueError if multiple objects match the query
    '''
    status, _, response, _ = conn.search(
            search_base=base,
            search_filter='(uidNumber=%s)'%uid,
            attributes=['*'])

    if(status): #we think we found something
        if(len(response)<1):
            raise Exception('for some reason status is false and response is 0... that should not happen')
        elif(len(response)>1):
            raise ValueError('too many responses were found (duplicate uid?)')
        return (status, response[0])
 
    # we did not find anything
    return (status, None)

if __name__ == '__main__':
    parser = argparser('print a user matching the posix username or uid')
    parser.add_argument('--username',
            default=None,
            help='posix username to find')
    parser.add_argument('--uid',
            default=None,
            help='posix uid to find')
    parser.add_argument('--base',
            default='ou=People,dc=company,dc=com',
            help='OU to search (ex: ou=People,dc=company,dc=com)')
    args = parser.parse_args()
    conn = connect(args=args)

    if(args.username):
        found, response = getuser(conn, args.username, args.base)
    elif(args.uid):
        found, response = getuid(conn, args.uid, args.base)
    else:
        print('either --username or --uid must be provided')
        sys.exit(1)

    if(found):
        pprint(response)
    else:
        print('not found')
        exit(1)

