########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.


import sys

import click

from .pypi_handler import PypiHandler
from .version_checker import VersionChecker
from . import logger

lgr = logger.init()


@click.group()
def main():
    pass


@click.command()
@click.option('-d', '--dist-type', default=False, required=False,
              help='distribution type. default is sdist')
@click.option('-f', '--force', is_flag=True, default=False, required=False,
              help='upload to Pypi')
@click.option('-t', '--test', is_flag=True, default=False, required=False,
              help='upload to Pypitest')
@click.option('-p', '--path', required=False, type=str,
              help='location of setup.py')
@click.option('-c', '--credentials', nargs=2, required=False, type=str,
              help='use specific credentials for upload '
                   '(not what is in .pypirc). usage: crt -c user password')
def upload(path, credentials, test, force):
    """upload package to pypi
    """
    if force:
        pypi_handler = PypiHandler(path, credentials, target="pypi")
    elif test:
        pypi_handler = PypiHandler(path, credentials)
    else:
        lgr.error("Target not specified. Please use --force for pypi or "
                  "--test for pypitest")
        sys.exit(1)
    pypi_handler.upload()


@click.command()
@click.option('-d', '--dist-type', default=False, required=False,
              help='distribution type. default is sdist')
@click.option('-f', '--force', is_flag=True, default=False, required=False,
              help='register to Pypi')
@click.option('-t', '--test', is_flag=True, default=False, required=False,
              help='register to Pypitest')
@click.option('-p', '--path', required=False, type=str,
              help='location of setup.py')
@click.option('-c', '--credentials', nargs=2, required=False, type=str,
              help='use specific credentials for registration '
                   '(not what is in .pypirc). usage: crt -c user password')
def register(path, credentials, test, force):
    """register package to pypi
    """
    if force:
        pypi_handler = PypiHandler(path, credentials, target="pypi")
    elif test:
        pypi_handler = PypiHandler(path, credentials)
    else:
        lgr.error("Target not specified. Please use --force for pypi or "
                  "--test for pypitest")
        sys.exit(1)
    pypi_handler.register()


@click.command()
@click.option('-t', '--test', is_flag=True, default=False, required=False,
              help='check Pypitest. default is to check Pypi')
@click.option('-p', '--path', required=False, type=str,
              help='location of setup.py')
def isOnPypi(path, test):
    """Check if package exists on pypi
    """
    if test:
        pypi_handler = PypiHandler(path, target="testpypi")
    else:
        pypi_handler = PypiHandler(path, target="pypi")
    if pypi_handler.is_package_of_specific_version_available_on_pypi(
            package_name=pypi_handler.name,
            expected_version=pypi_handler.version):
        lgr.info("package {0} of version {1} is available on {2}".format(
            pypi_handler.name, pypi_handler.version, pypi_handler.target))
    else:
        lgr.info("package {0} of version {1} is not on {2}".format(
            pypi_handler.name, pypi_handler.version, pypi_handler.target))


@click.command()
@click.option('-p', '--path', required=False, type=str,
              help='location of setup.py')
def hasUnlockedDeps(path):
    """Checks if the package has unlocked dependencies
    """
    version_checker = VersionChecker(path)
    version_checker.check_package()

main.add_command(hasUnlockedDeps)
main.add_command(isOnPypi)
main.add_command(upload)
main.add_command(register)
