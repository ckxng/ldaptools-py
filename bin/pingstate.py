#!/usr/bin/env python3
'''return the state of dn=state'''

# this script might be called from the project directory, in cases where
# the ldaptools module has not been "installed". This inserts the 
# project directory into python's path, so the module can be found
from pathlib import Path
from sys import path
project = str(Path(__file__).resolve().parents[1])
path.insert(0, project)

from ldaptools import connect, argparser

def pingstate(conn):
    '''returns the value of dn=state

    Example returned value:
    {
      'dsaIsActive': True, 
      'dsaEnv': 'prod', 
      'dsaSite': 'bed', 
      'dsaRole': 'consumer', 
      'dsaFQDN': 'servername.company.com'
    }

    Parameters:
    conn(object): a ldap3 connection object
    
    Returns:
    a dict containing the current dsa state
    
    Raises:
    Exception if the query fails
    '''
    status, result, response, _ = conn.search(
            'cn=state', 
            '(objectClass=*)',
            attributes=['dsaIsActive','dsaEnv','dsaSite','dsaRole','dsaFQDN'])

    if(not status):
        raise Exception('query failed')

    return response[0]['attributes']

if __name__ == '__main__':
    args = argparser('return the dn=state').parse_args()
    conn = connect(args=args)
    state=pingstate(conn)
    print(state['dsaIsActive'])
    if(args.verbose):
        print(state)

