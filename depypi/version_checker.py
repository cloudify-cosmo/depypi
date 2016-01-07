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

import sh

from . import logger

lgr = logger.init()

FILES_TO_CHECK = 'setup.py'


class VersionChecker():
    def __init__(self, path='', list_of_extra_files=[]):
        self.path = path
        self.files_to_check = list_of_extra_files
        self.files_to_check.append(FILES_TO_CHECK)
        print self.files_to_check
        logger.configure()

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
                sys.exit(1)
        finally:
                os.chdir(current_dir)
        return p

    def _get_file_dependencies(self, path_to_file):
        args = ["setup.py", "install", "-v", "-n"]
        output = self._command(args)
        dependencies = []
        for line in output:
            if line.startswith("Searching for"):
                dependencies.append(
                        line.replace("Searching for ", "").strip().encode(
                                'ascii', 'ignore'))
        return dependencies

    def check_package(self):
        for f in self.files_to_check:
            full_path_to_file = os.path.join(self.path or '', f)
            print self._get_file_dependencies(full_path_to_file)