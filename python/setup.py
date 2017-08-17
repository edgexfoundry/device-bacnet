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
    install_requires=['flask', 'bacpypes','pyyaml'],
    
)
