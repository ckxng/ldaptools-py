#!/usr/bin/env python3
'''ldaptools - helper functions for ldap scripts in python3

Designed for LDAP servers that use 389 and START_TLS with TLS1.2.  To allow for
thread-safe operation, we also use SAFE_SYNC.

Three authentication types are provided by this module, anonymous bind, SASL
External auth/SSL Certificate, and SASL simple username/password.  
'''

from ssl import CERT_REQUIRED, PROTOCOL_TLSv1_2
from ldap3 import Tls, Server, Connection, AUTO_BIND_TLS_BEFORE_BIND, ALL, SAFE_SYNC, EXTERNAL, SASL, SIMPLE
from argparse import ArgumentParser

def connect(**kw):
    '''connects to LDAP and returns a ldap3 connection object

    if both auth_key and auth_cert are provided, then SASL external auth
    will be attempted with those SSL files.
    
    if auth_key and auth_cert are NOT provided, and auth_user and auth_pass ARE
    provided, then SASL simple authentication will be performed with those
    credentials
    
    otherwise, an anonymou bind will be performed.

    Additionally, the argparser function in this module can have its parsed args
    passed directly to this function, as a shortcut.  (Note, this method will
    overrise values passed in using other methods.)

        from ldaptools import connect, argparser
        parser = argparser()
        args = parser.parse_args()
        conn = connect(args=args)

    When looking at the ldap3 documentation, you will note that most of the examples
    re-use the connection object for searches.  This is not thread-safe.  Instead,
    this function assumes that you want to be thread-safe and provides a 
    client_strategy=SAFE_SYNC value to the connection object.  If you want to
    override this so that your code more closely matches the ldap3 documentation
    (at the cost of not being thread-safe), provide client_strategy=ldap3.SYNC instead.
    
    Params:
    server(string): *required* hostname or IP of the ldap server
    debug(bool): prints detailed debug info to console
    verbose(bool): prints some info to console
    auth_user(string): user to bind as (ie: uid=cking,ou=People,dc=company,dc=com)
    auth_pass(string): password to bind with
    auth_key(string): a path to a client private key in PEM format
    auth_cert(string): a path to a client signed certificate in PEM format
    args(object): a parsed args object from argparser created by ldaptools.argparser
    client_strategy: value to pass to ldap3 connection client_strategy (default SAFE_SYNC)

    Returns:
    ldap3 connection object

    Raises:
    ValueError if a required parameter is not provided
    '''
    server=kw.pop('server',None)
    auth_user=kw.pop('auth_user',None)
    auth_pass=kw.pop('auth_pass',None)
    auth_key=kw.pop('auth_key',None)
    auth_cert=kw.pop('auth_cert',None)
    client_strategy=kw.pop('client_strategy',SAFE_SYNC)

    if('args' in kw):
        server=kw['args'].server
        auth_user=kw['args'].auth_user
        auth_pass=kw['args'].auth_pass
        auth_key=kw['args'].auth_key
        auth_cert=kw['args'].auth_cert

    if(server == None):
        raise ValueError('server is required')

    authentication=None
    if(auth_key and auth_cert):
        authentication=SASL
    elif(auth_user and auth_pass):
        authentication=SIMPLE

    ldaptls = Tls(
            local_private_key_file=auth_key,
            local_certificate_file=auth_cert,
            ca_certs_file=None, # use OS defaults
            validate=CERT_REQUIRED, 
            version=PROTOCOL_TLSv1_2)

    # connect over clearext, as we will be using START_TLS
    ldapserver = Server(server, port=389, use_ssl=False, tls=ldaptls, get_info=ALL)
    
    # automatically upgrade the connection with START_TLS, then bind
    conn = Connection(ldapserver,
            user=auth_user, 
            password=auth_pass,
            sasl_mechanism=EXTERNAL,
            authentication=authentication,
            auto_bind=AUTO_BIND_TLS_BEFORE_BIND,
            client_strategy=client_strategy,
            collect_usage=True)

    return conn

def argparser(description=''):
    '''build a parser with common ldap params

    Parameters:
    description(string): description of this application that shows in --help

    Returns:
    argparser object
    '''
    parser = ArgumentParser(description=description)
    parser.add_argument('-s',
            default='default-host.company.com',
            dest='server',
            help='server name to connect to')
    parser.add_argument('-v',
            action='store_true',
            dest='verbose')
    parser.add_argument('-d',
            action='store_true',
            dest='debug')
    parser.add_argument('--user',
            default=None,
            dest='auth_user',
            help='bind user (ie. uid=cking,ou=People,dc=company,dc=com)')
    parser.add_argument('--pass',
            default=None,
            dest='auth_pass',
            help='bind password'),
    parser.add_argument('--key',
            default=None,
            dest='auth_key',
            help='path to client private key for SASL extended auth')
    parser.add_argument('--cert',
            default=None,
            dest='auth_cert',
            help='path to client cert for SASL extended auth')
    return parser

