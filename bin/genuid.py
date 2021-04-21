#!/usr/bin/env python3
'''generate a new uid that is free within the basedn'''

# this script might be called from the project directory, in cases where
# the ldaptools module has not been "installed". This inserts the 
# project directory into python's path, so the module can be found
from pathlib import Path
from sys import exit, path
project = str(Path(__file__).resolve().parents[1])
path.insert(0, project)

from ldaptools import connect, argparser
from bin.isuidfree import isuidfree
from random import randint

def genuid(conn, uidmin, uidmax, base, attempts):
    '''generate a uid between uidmin and uidmax within the specified base

    Example:
    genuid(conn,uidmin=100,uidmax=110,base='ou=People,dc=company,dc=com')
    valid values could be:
    100,101,102,103,104,105,106,107,108,109

    Parameters:
    conn(object): a ldap3 connection object
    uidmin(int): the minimum uid to consider(inclusive)
    uidmax(int): the maximum uid to consider(exclusive)
    base(string): the basedn to search
    attempts(int): the maximum number of attempts before raising an error

    Returns:
    integer of the available uid

    Raises:
    ValueError if a valid id cannot be found within the specified number of attempts
    '''

    founduid=None
    for i in range(attempts):
        proposed=randint(uidmin,uidmax)
        if(isuidfree(conn,proposed,base)):
            founduid=proposed
            break
    
    if(founduid==None):
        raise ValueError('unable to find valid uid in %s attempts'%attempts)

    return founduid

if __name__ == '__main__':
    parser = argparser('generate a free uid')
    parser.add_argument('--uidmin',
            type=int,
            default=1000,
            help='minimum uid(inclusive)')
    parser.add_argument('--uidmax',
            type=int,
            default=8500,
            help='maximum uid(exclusive)')
    parser.add_argument('--attempts',
            type=int,
            default=10,
            help='number of attempts to try and find a free uid')
    parser.add_argument('--base',
            default='ou=People,dc=company,dc=com',
            help='OU to search (ex: ou=People,dc=company,dc=com)')
    args = parser.parse_args()
    conn = connect(args=args)

    uid = genuid(conn, args.uidmin, args.uidmax, args.base, args.attempts)
    print(uid)

