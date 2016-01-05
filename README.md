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

## Logic

upload and register operation have no default target and require a flag (either test or force) to run
isonpypi defaults to checking pypi and if called with --test flag with check pypitest instead
If ~/.pypirc already exists it will be backed up and restored after an operation should you use the credentials flag.

