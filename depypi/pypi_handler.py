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

import os
import shutil
import sys

import sh
import requests

from . import logger

lgr = logger.init()

PYPI_TEMPLATE = "[distutils]\n" \
                "index-servers =\n" \
                "    pypi\n" \
                "[pypi]\n" \
                "repository=https://pypi.python.org/pypi\n" \
                "username={0}\n" \
                "password={1}"

PYPITEST_TEMPLATE = "[distutils]\n" \
                    "index-servers =\n" \
                    "    pypitest\n\n" \
                    "[pypitest]\n" \
                    "repository=https://testpypi.python.org/pypi\n" \
                    "username={0}\n" \
                    "password={1}"


class PypiHandler():
    def __init__(self, path='', credentials=None, target="pypitest",
                 dist_type='sdist'):
        """A Pypi handler object for uploading, registering and testing.
        :param path: location of setup.py
        :param credentials: credentials to use for upload or registation
        if none are specified a best effort will be made to use either:
        ~/.pypirc or environment variables PYPIUSER and PYPIPWD.
        Credentials are not needed for checking pypi and pypitest for packages.
        :param target: pypi for live and pypitest for test
        :return: None
        """
        logger.configure()
        if credentials:
            if isinstance(credentials, tuple):
                self.pypiuser = credentials[0]
                self.pypipwd = credentials[1]
            else:
                lgr.error("Credentials provided are of the wrong format."
                          "Should be tuple(str,str) if calling by API, or "
                          "-c user password")
                sys.exit(1)
        self.path = path
        self.target = target
        if target == "pypitest":
            self.test_target = "testpypi"
        else:
            self.test_target = target
        self.name = self.get_package_name()
        self.version = self.get_package_version()
        self.credentials = credentials
        self.cleanup_pypirc = False
        self.dist_type = dist_type
        self.pypirc_file = os.path.expanduser('~/.pypirc')
        self.pypirc_backup_file = os.path.expanduser('~/.pypirc.crt.backup')

    def _command(self, args):
        """Runs python commands from command line
        :param args: arguments to run command with.
        :return: returns the text output of the command.
        """
        current_dir = os.getcwd()
        try:
            if self.path:
                os.chdir(self.path)
            p = sh.python(*args)
            p.wait()
        except (sh.ErrorReturnCode, ValueError, OSError) as e:
            lgr.error(e)
            if self.cleanup_pypirc:
                self._cleanup_injected_credentials()
            sys.exit(1)
        finally:
            os.chdir(current_dir)
        return p

    def get_package_version(self):
        """Gets the version of the python package
        :return: version of the python package
        """
        args = ("setup.py", "--version")
        return ''.join(self._command(args=args).splitlines())

    def get_package_name(self):
        """Gets the name of the python package
        :return: name of the python package
        """
        args = ("setup.py", "--name")
        return ''.join(self._command(args=args).splitlines())

    def upload(self):
        """Uploads a package to Pypi\TestPypi and verify it is available
        :param target: pypi for live and pypitest for testpypi
        :return: None
        """
        self._verify_and_inject_credentials()
        args = ("setup.py", self.dist_type, "upload", "-r", self.target)
        lgr.info(self._command(args=args))
        try:
            if self.is_package_of_specific_version_available_on_pypi(
                    self.name, self.version):
                lgr.info(
                        "package {0} of version {1} is available on {2}".format(
                                self.name, self.version, self.target))
            else:
                lgr.warn(
                        "The upload operation was completed successfully but "
                        "verification has failed")
        finally:
            if self.cleanup_pypirc:
                self._cleanup_injected_credentials()

    def register(self):
        """Registers a package to Pypi or TestPypi and verify it is registered
        :param target: pypi for live and pypitest for testpypi
        :return: None
        """
        self._verify_and_inject_credentials()
        args = ("setup.py", "register", "-r", self.target)
        lgr.info(self._command(args=args))
        try:
            if self.is_package_of_specific_version_registered_on_pypi(
                    self.name, self.version):
                lgr.info(
                        "package {0} of version {1} is registered on {2}".format(
                                self.name, self.version, self.target))
            else:
                lgr.warn(
                        "The register operation was completed successfully "
                        "but verification has failed")
        finally:
            if self.cleanup_pypirc:
                self._cleanup_injected_credentials()

    def _check_url(self, url):
        """Checks availability of a specific file for download
        :param url: URL to check
        :return: True or False based on availability
        """
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            lgr.error(e)
            return None
        if 200 <= r.status_code < 300:
            return True
        else:
            return False

    def is_package_of_specific_version_registered_on_pypi(
            self, package_name, expected_version):
        """Is Package of specific version registered on Pypi?
        :param package_name: package_name
        :param expected_version: expected_version
        :return: True or False based on registration
        """
        url = "https://{0}.python.org/pypi/{1}/{2}".format(
                self.test_target, package_name, expected_version)
        return self._check_url(url)

    def is_package_of_specific_version_available_on_pypi(
            self, package_name, expected_version):
        """Is Package of specific version available on Pypi?
        :param package_name: package_name
        :param expected_version: expected_version
        :return: True or False based on availability
        """
        url = "https://{0}.python.org/packages/source/{3}/{1}/{1}-{2}.tar.gz" \
              "".format(self.test_target, package_name, expected_version,
                        package_name[0])
        return self._check_url(url)

    def _create_credentials_string(self):
        """
        Creates credentials string for temporary use
        :return: file contents
        """
        if self.target == "pypi":
            return PYPI_TEMPLATE.format(self.pypiuser,
                                        self.pypipwd)
        else:
            return PYPITEST_TEMPLATE.format(self.pypiuser,
                                            self.pypipwd)

    def _verify_and_inject_credentials(self):
        """Verify credentials exist or make best effort to retrieve them
        If credentials were specified ~/.pypirc will be backed up and then
        overwritten for the duration of tool use, afterwhich the original
        file will be restored.
        Otherwise a best effort will be made to use existing credentials from
        ~/.pypirc, environment variables. If no credentials are found,
        will exist with code 1
        :return: None
        """
        if self.credentials:
            if os.path.isfile(self.pypirc_file):
                shutil.move(src=self.pypirc_file,
                            dst=self.pypirc_backup_file)
            with open(self.pypirc_file, 'w') as f:
                f.write(self._create_credentials_string())
            self.cleanup_pypirc = True
        elif os.path.isfile(self.pypirc_file):
            return
        else:
            self.pypiuser = os.getenv("PYPIUSER")
            self.pypipwd = os.getenv("PYPIPWD")
            self.cleanup_pypirc = True
            if self.pypipwd and self.pypiuser:
                with open(self.pypirc_file, 'w') as f:
                    f.write(self._create_credentials_string())
            else:
                lgr.error("Unable to find credentials for Pypi. Please "
                          "include one of the following:\n~/.pypirc file "
                          "(see http://peterdowns.com/posts/first-time-with-"
                          "pypi.html\n set environment variables PYPIUSER and "
                          "PYPIPWD\ncall with credentials flag. crt pypi "
                          "-c help for details")
                sys.exit(1)

    def _cleanup_injected_credentials(self):
        """remove injected credentials and restore original ones.
        :return: None
        """
        if os.path.isfile(self.pypirc_backup_file):
            shutil.move(src=self.pypirc_backup_file,
                        dst=self.pypirc_file)
        else:
            os.remove(self.pypirc_file)
