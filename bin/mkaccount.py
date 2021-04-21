#!/usr/bin/env python3
'''make an account within the specified basedn'''

# this script might be called from the project directory, in cases where
# the ldaptools module has not been "installed". This inserts the 
# project directory into python's path, so the module can be found
from pathlib import Path
from sys import exit, path
project = str(Path(__file__).resolve().parents[1])
path.insert(0, project)

from ldaptools import connect, argparser
from bin.genuid import genuid
from random import randint

def mkaccount(conn, username, uid, ou, gid=100, firstName=None, lastName=None, cn=None, gecos=None, email=None, shell='/bin/bash', home=None, password=None):
    '''create and add a user to the directory

    dn = mkaccount(conn, 
            username='svc_testaccount',
            uid=12345,
            ou='ou=Applications,dc=company,dc=com',
            gecos='Owner: John Doe <jdoe@company.com>',
            email='owningteam@company.com')

    dn = mkaccount(conn, 
            username='jdoe',
            uid=13579,
            ou='ou=People,dc=company,dc=com',
            firstName='John',
            lastName='Doe',
            email='jdoe@company.com',
            password='abc123!@#098zyx')

    Parameters:
    conn(object): a ldap3 connection object
    username(string): linux username (called uid in ldap)
    uid(int): posix uid (called uidNumber in ldap)
    gid(int): posix gid (called gidNumber in ldap)
    firstName(string): the first name of the user (called givenName in ldap)
    lastName(string): the last name of the user (called sn in ldap)
    gecos(string): the posix gecos string (otherwise constructed from the name)
    email(string): the user's email address (called mail in ldap)
    ou(string): the OU to add the user to (used to construct the dn)
    shell(string): the login shell (called loginShell in ldap)
    home(string): the home directory (called homeDirectory in ldap)
    password(string): the password to set (can be None)

    Returns two values in a tuple:
    dn of the created object
    attributes the user was created with

    Raises:
    Exception if unsucessful
    '''

    dn='uid=%s,%s'%(username,ou)

    objectClass=[
        'account',
        'inetOrgPerson',
        'organizationalPerson',
        'person',
        'posixAccount',
        'shadowAccount'
        ]

    attributes={
        'uid': username,
        'uidNumber': uid,
        'gidNumber': gid,
        'loginShell': shell,
        'objectClass': objectClass
        }

    # if a firstname was provided
    if(firstName != None):
        attributes['givenName'] = firstName

        # some items can be auto-filled if a firstname and lastname are provided
        if(lastName != None):
            if(gecos == None):
                attributes['gecos'] = '%s %s'%(firstName, lastName)
            if(cn == None):
                attributes['cn'] = '%s %s'%(firstName, lastName)

    # if a lastname is provided
    if(lastName != None):
        attributes['sn'] = lastName

    # if an email is provided
    if(email != None):
        attributes['mail'] = email

    # if a password was provided
    if(password != None):
        attributes['userPassword'] = password

    # populate home if not provided
    if(home == None):
        attributes['homeDirectory'] = '/home/%s'%username

    # if cn was not able to be populated from firstName and lastName
    if('cn' not in attributes):
        attributes['cn'] = username

    status, response, result, _ = conn.add('uid=%s,%s'%(username,ou),
            attributes=attributes)

    if(not status):
        raise Exception('user creation failed: %s'%response['description'])

    return (dn, attributes)

if __name__ == '__main__':
    parser = argparser('make a user account and add it to ldap')
    parser.add_argument('--username',
            required=True,
            help='new user username')
    parser.add_argument('--uid',
            type=int,
            required=True,
            help='new user uid'),
    parser.add_argument('--gid',
            type=int,
            required=True,
            help='new user gid'),
    parser.add_argument('--first',
            required=True,
            dest='firstName',
            help='new user first name'),
    parser.add_argument('--last',
            required=True,
            dest='lastName',
            help='new user last name'),
    parser.add_argument('--email',
            required=True,
            help='new user email'),
    parser.add_argument('--ou',
            default='ou=People,dc=company,dc=com',
            help='OU to create user in (ex: ou=People,dc=company,dc=com)')
    parser.add_argument('--shell',
            default='/bin/bash',
            help='new user shell'),
    parser.add_argument('--home',
            default=None,
            help='new user homedir'),
    parser.add_argument('--password',
            default=None,
            help='new user password'),
    args = parser.parse_args()
    conn = connect(args=args)

    dn, attributes = mkaccount(conn, 
            username=args.username, 
            uid=args.uid, 
            gid=args.gid, 
            firstName=args.firstName, 
            lastName=args.lastName, 
            email=args.email, 
            ou=args.ou, 
            shell=args.shell, 
            home=args.home, 
            password=args.password)
    print(dn)
    if(args.verbose):
        print(attributes)

