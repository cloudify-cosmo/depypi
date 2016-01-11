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
import sys

import re
import sh
from yolk.pypi import CheeseShop

from . import logger

lgr = logger.init()

FILES_TO_CHECK = 'setup.py'


class VersionChecker():
    def __init__(self, path='', extra_files=None):
        self.path = path
        if extra_files is None:
            self.files_to_check = [FILES_TO_CHECK]
        else:
            self.files_to_check.append(FILES_TO_CHECK)
        logger.configure()

    def _command(self, args, cmd):
        """Runs python commands from command line
        :param args: arguments to run command with.
        :return: returns the text output of the command.
        """
        current_dir = os.getcwd()
        try:
            if self.path:
                os.chdir(self.path)
            cmd = sh.Command(cmd)
            p = cmd(*args)
            p.wait()
        except (sh.ErrorReturnCode, ValueError, OSError) as e:
            lgr.error(e)
            sys.exit(1)
        finally:
            os.chdir(current_dir)
        return p

    def _get_file_dependencies(self, path_to_file):
        args = ["setup.py", "install", "-v", "-n"]
        output = self._command(args, 'python')
        dependencies = []
        for line in output:
            if line.startswith("Searching for"):
                dependencies.append(
                        line.replace("Searching for ", "").strip().encode(
                                'ascii', 'ignore'))
        return dependencies

    def get_all_dependencies(self):
        for f in self.files_to_check:
            full_path_to_file = os.path.join(self.path or '', f)
            return self._get_file_dependencies(full_path_to_file)

    def get_dependency_for_this_package(self, package_name):
        args = ["install", package_name, "-v", "-n"]
        output = self._command(args, 'pip')
        dependencies = []
        for line in output:
            if line.startswith("Searching for"):
                dependencies.append(
                        line.replace("Searching for ", "").strip().encode(
                                'ascii', 'ignore'))
        return dependencies

    def _get_package_name_from_condition(self, condition):
        return re.search('(.+)[=<>][0-9,.]*', condition)

    # def _get_subdependencies_for_package(self):
    #     pass
    #
    # def get_all_sub_dependencies(self):
    #     for dep in self.get_all_dependencies():
    #         name = self._get_package_name_from_condition(dep)
