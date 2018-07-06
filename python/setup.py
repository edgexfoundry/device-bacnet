# Copyright 2016-2017 Dell Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @microservice:  device-bacnet
# @author: Tyler Cox, Dell
# @version: 1.0.0
from distutils.core import setup
import glob, os.path, os
import platform

def dirs_only(directory):
    split = directory.split('/')
    array = [os.path.join(split[1], '*')]
    for r,d,f in os.walk(directory):
        for dir in d:
            path = os.path.join(r, dir, '*').split(split[0] + '/')[1]
            array.append(path)
    return array


setup(
    # Application name:
    name="EdgeXResourceBacnet",

    scripts=['app/FlaskController.py','app/BACNetDriver.py'],
    # Version number (initial):
    version="1.0.1",

    # Application author details:
    author="Dell Inc.,",
    author_email="tyler_cox@dell.com",

    # Packages
    packages=["app"],
    package_data={'app': ['application.properties',]},

    # Include additional files into the package
    include_package_data=True,

    # Details
    #url="http://pypi.python.org/pypi/MyApplication_v010/",

    #
    # license="LICENSE.txt",
    description="EdgeX BACNet driver service.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
	
	#if platform.system() == 'Linux':
	#	requirements.extend([])
    install_requires=['flask==1.0.2', 'bacpypes==0.16.7','pyyaml==3.13'],
    
)
