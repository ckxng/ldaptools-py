#!/usr/bin/env python3
'''return who is logged in'''

# this script might be called from the project directory, in cases where
# the ldaptools module has not been "installed". This inserts the 
# project directory into python's path, so the module can be found
from pathlib import Path
from sys import path
project = str(Path(__file__).resolve().parents[1])
path.insert(0, project)

from ldaptools import connect, argparser

def whoami(conn):
    '''returns who is logged in

    Parameters:
    conn(object): a ldap3 connection object
    
    Returns:
    a string representing the user that is logged in
    
    Raises:
    Exception if the query fails
    '''
    status, result, response, _ = conn.extended('1.3.6.1.4.1.4203.1.11.3')
    if(not status):
        raise Exception('query failed')

    user='Anonymous'
    if(result['responseValue'] != b''):
        user=result['responseValue'].decode('UTF-8')

    return user

if __name__ == '__main__':
    args = argparser('return who is logged in').parse_args()
    conn = connect(args=args)
    print(whoami(conn))

