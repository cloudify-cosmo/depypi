########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
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

from setuptools import setup
import os
import codecs

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()


setup(
    name='depypi',
    version='0.1.1',
    url='https://github.com/cloudify-cosmo/depypi',
    author='Gigaspaces',
    author_email='cosmo-admin@gigaspaces.com',
    license='LICENSE',
    platforms='All',
    description='Uploads registers and verifies Pypi operations.',
    long_description=read('README.rst'),
    packages=['depypi'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'depypi = depypi.depypi:main',
        ]
    },
    install_requires=[
        "requests>=2.7.0",
        "sh>=1.11",
        "click==4.0",
    ]
)
