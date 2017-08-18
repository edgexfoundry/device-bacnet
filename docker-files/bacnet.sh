#!/bin/sh

cd /edgex/edgex-resource-bacnet/virtualenv/bin/
source activate
python3 $2 -p $3 &
java -jar /edgex/edgex-device-bacnet/$1