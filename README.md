# LDAP Tools
The scripts in ./bin/ all have online help.  Run `./bin/SCRIPT.py -h` to 
get information on the script's purpose and how to use it.

This repo isn't intended to be installed with setuptools, rather it is
expected that the user will download the repo and use the scripts 
in-place.

## Environment Setup
This must be done before the scripts in ./bin/ will be functional.

From a system with Python 3 installed (where `/usr/bin/env python3` can 
find a python3 install), run the following:

    /usr/bin/env python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Contributing
Users are encouraged to contribute small, single-purpose scripts that are
useful for maintaining the LDAP environment.  Each script should have one
job and do it well.  Scripts should include a function, which can be 
consumed by other scripts.  Scripts should also include CLI functionality
based on `ldaptools.argparser` for consistency.

See the scripts themselves for an example.

## Author
[Cameron King](http://cameronking.me)

## Copying
This software is released under the MIT License. See LICENSE for details.

