Main Author: Tyler Cox

Language: Python

Copyright 2017, Dell, Inc.

BACNet Resource Library interface for BACNet Device Service

 

Copyright 2017, Dell, Inc.

### Modification ###

Once modified, please update the tar package for deployment using

```
#!shell

python setup.py sdist
```


### Setup/Initialization ###

 
* python-setuptools
* python-dev
* flask-restful==0.3.4
* requests==2.4.3

### Configuring ###


or create a virtual env to test out a package


```
#!shell

   virtualenv bacnetresource
   . bacnet/bin/activate
   pip install <path to tar.gz file>
   FlaskController.py -p 5001
```


