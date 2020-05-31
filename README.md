## METASCAN
# Scan Anaconda/Python metadata for version mismatches

It will scan current Anaconda/Python base prefix.
Other than current Python/Anaconda installation folder can be specified as an argument.
Normally it process Lib\site-packages and conda-meta folders.
With option -p it will add processing of pkgs folder also.
Folders "conda-meta" and "pkgs" available in Anaconda only, not in Python.
Versions 0.0 process only file/folder names, not contents.
Output with problems found presented below.

I have no any idea is it really a problem or not, when I have
anaconda-project with versions 0.8.3 and 0.8.4 within same base environment
and no any other virtual environments created. File
Lib\site-vendors\anaconda_project\version.py has 0.8.3 inside.

``` console
d:\My\ProPy>py pico\metascan.py -p
Act: d:\InstSoft\Python\Conda3x64\condabin\conda.bat activate
Run: d:\InstSoft\Python\Conda3x64\Python.exe
Arg: pico\metascan.py -p
 --- Scan metadata for version mismatch ---
Prefix: d:\InstSoft\Python\Conda3x64
LibSP : d:\InstSoft\Python\Conda3x64\Lib\site-packages
conda-meta : d:\InstSoft\Python\Conda3x64\conda-meta
pkgs  : d:\InstSoft\Python\Conda3x64\pkgs
Version Mix:
  ['anaconda_project', '0.8.3', 'dist-info', 'LibSP']
  ['anaconda-project', '0.8.4', 'py_0', 'conda-meta']
  ['anaconda-project', '0.8.4', 'py_0', 'pkgs']
Version Mix:
  ['conda_package_handling', '1.7.0', 'dist-info', 'LibSP']
  ['conda-package-handling', '1.6.1', 'py37h62dcd97_0', 'conda-meta']
  ['conda-package-handling', '1.6.1', 'py37h62dcd97_0', 'pkgs']
Version Mix:
  ['setuptools', '46.4.0.post20200518', 'py3.7', 'egg-info', 'LibSP']
  ['setuptools', '46.4.0', 'py37_0', 'conda-meta']
  ['setuptools', '46.4.0', 'py37_0', 'pkgs']
Version mix in metadata for 3 package(s)
d:\My\ProPy>
```

