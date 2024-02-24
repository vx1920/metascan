## METASCAN
# Scan Anaconda/Python metadata for version mismatches

It may be problem to have multiple version of metadata for the same package
or multiple versions of package in different folders in sys.path().
It will scan current Anaconda/Python base prefix and make report.

Currently metascan processes only file/folder names, not contents.
Following modes are implemented:

# metascan fnd name
Search for specified name (case-insensitive search for name* on sys.path())

# metascan sim
Similar name files or folders on sys.path(). It shows possible package duplication
with same or different version in metadata. 

# metascan mix
 It is default mode. It reports version conflicts for same package names.
Normally it process sys.path() folder list and in case of Anaconda it also can scan conda-meta folder.
With option -p it will add processing of pkgs folder also.
Folders "conda-meta" and "pkgs" available in Anaconda only, not in Python.

Report with version mismatch found presented below (default mode is mix):

``` console
--- metascan version 0.0.1 for prefix: /usr
--- Scan metadata for version mismatch ---
--- Version Mix for <certifi>:
FLDR: /usr/lib/python3.10/site-packages/certifi-2022.9.24-py3.10.egg-info
FLDR: /usr/lib/python3.10/site-packages/certifi-2022.12.7.dist-info
--- Version Mix for <configobj>:
FLDR: /usr/lib/python3.10/site-packages/configobj-5.0.8.dist-info
FLDR: /usr/lib/python3.10/site-packages/configobj-5.0.6-py3.10.egg-info
--- Version Mix for <pip>:
FLDR: /usr/lib/python3.10/site-packages/pip-23.0.1.dist-info
FLDR: /usr/lib/python3.10/site-packages/pip-22.3.1-py3.10.egg-info
--- Version Mix for <prettytable>:
FLDR: /usr/lib/python3.10/site-packages/prettytable-3.6.0.dist-info
FLDR: /usr/lib/python3.10/site-packages/prettytable-3.5.0.dist-info
--- Version Mix for <setuptools>:
FLDR: /usr/lib/python3.10/site-packages/setuptools-67.6.0-py3.10.egg-info
FLDR: /usr/lib/python3.10/site-packages/setuptools-67.6.1.dist-info
--- Version mix in metadata for 5 package(s)

```

Here is report with similar packages found on sys.path():

``` console
python metascan.py sim

--- metascan version 0.0.1 for prefix: /usr
--- Same name items <__pycache__>:
FLDR: /home/myname/SATALOCAL/My/__pycache__
FLDR: /usr/lib64/python3.10/__pycache__
FLDR: /usr/lib64/python3.10/site-packages/__pycache__
FLDR: /usr/lib64/python3.10/_import_failed/__pycache__
FLDR: /usr/lib/python3.10/site-packages/__pycache__
--- Same name items <_brotli.cpython-310-x86_64-linux-gnu.so>:
FILE: /usr/lib64/python3.10/site-packages/_brotli.cpython-310-x86_64-linux-gnu.so
FILE: /usr/lib/python3.10/site-packages/_brotli.cpython-310-x86_64-linux-gnu.so
--- Same name items <_cffi_backend.cpython-310-x86_64-linux-gnu.so>:
FILE: /usr/lib64/python3.10/site-packages/_cffi_backend.cpython-310-x86_64-linux-gnu.so
FILE: /usr/lib/python3.10/site-packages/_cffi_backend.cpython-310-x86_64-linux-gnu.so
--- Same name items <brotli.py>:
FILE: /usr/lib64/python3.10/site-packages/brotli.py
FILE: /usr/lib/python3.10/site-packages/brotli.py
--- Same name items <cairo>:
FLDR: /usr/lib64/python3.10/site-packages/cairo
FLDR: /usr/lib/python3.10/site-packages/cairo
--- Same name items <cffi>:
FLDR: /usr/lib64/python3.10/site-packages/cffi
FLDR: /usr/lib/python3.10/site-packages/cffi
--- Same name items <cryptography>:
FLDR: /usr/lib64/python3.10/site-packages/cryptography
FLDR: /usr/lib/python3.10/site-packages/cryptography
```

