# depypi
A Tool for deploying Python packages to PyPI with multiple user support and a Pythonic API

depypi allows registration and upload of packages to Pypi and PypiTest.
It can also check availability of packages on Pypi and PypiTest.
It also generate ~/.pypirc on the fly to allow usage of alternate credentials

## Usage

```shell
depypi --help
Usage: depypi [OPTIONS] COMMAND [ARGS]...

  Upload, register and query packages on pypi and pypitest

Options:
  --help  Show this message and exit.

Commands:
  isonpypi  Check if package exists on pypi
  register  register package to pypi
  upload    upload package to pypi
```

Example:

This will register and verify successful registration of a package to pypitest:
```shell
depypi register -t -p cloudify-cli/
```

This will check if this version has been uploaded to pypitest:
```shell
depypi isonpypi -t -p cloudify-cli/
```

This will upload a version to Pypi:
```shell
depypi upload -f -p cloudify-cli/
```

This will upload a version to Pypi with specific credentials:
```shell
depypi upload -f -p cloudify-cli/ -c USER PASSWORD
```

This will upload a version to PypiTest:
```shell
depypi upload -t -c heathenasparagus zaAQ1QAaz
INFO - running sdist
running egg_info
writing requirements to depypi.egg-info/requires.txt
writing depypi.egg-info/PKG-INFO
writing top-level names to depypi.egg-info/top_level.txt
writing dependency_links to depypi.egg-info/dependency_links.txt
writing entry points to depypi.egg-info/entry_points.txt
reading manifest file 'depypi.egg-info/SOURCES.txt'
writing manifest file 'depypi.egg-info/SOURCES.txt'
running check
creating depypi-0.0.1
creating depypi-0.0.1/depypi
master
creating depypi-0.0.1/depypi.egg-info
making hard links in depypi-0.0.1...
hard linking README.rst -> depypi-0.0.1
hard linking setup.py -> depypi-0.0.1
hard linking depypi/__init__.py -> depypi-0.0.1/depypi
hard linking depypi/depypi.py -> depypi-0.0.1/depypi
hard linking depypi/dictconfig.py -> depypi-0.0.1/depypi
hard linking depypi/logger.py -> depypi-0.0.1/depypi
hard linking depypi.egg-info/PKG-INFO -> depypi-0.0.1/depypi.egg-info
hard linking depypi.egg-info/SOURCES.txt -> depypi-0.0.1/depypi.egg-info
hard linking depypi.egg-info/dependency_links.txt -> depypi-0.0.1/depypi.egg-info
hard linking depypi.egg-info/entry_points.txt -> depypi-0.0.1/depypi.egg-info
hard linking depypi.egg-info/requires.txt -> depypi-0.0.1/depypi.egg-info
hard linking depypi.egg-info/top_level.txt -> depypi-0.0.1/depypi.egg-info
Writing depypi-0.0.1/setup.cfg
Creating tar archive
removing 'depypi-0.0.1' (and everything under it)
running upload
Submitting dist/depypi-0.0.1.tar.gz to https://testpypi.python.org/pypi
Server response (200): OK

WARNING - The upload operation was completed successfully but verification has failed
```
Occasionally there will be delay and verification will fall through. Afterwards we can check:
```shell
depypi isonpypi -t
INFO - package depypi of version 0.0.1 is available on testpypi
```

## Logic

upload and register operation have no default target and require a flag (either test or force) to run

isonpypi defaults to checking pypi and if called with --test flag with check pypitest instead

If ~/.pypirc already exists it will be backed up and restored after an operation should you use the credentials flag.

