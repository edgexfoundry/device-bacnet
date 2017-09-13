#!/bin/sh

cd /edgex/edgex-resource-bacnet/virtualenv/bin/
source activate
python3 $4 -p $5 &
java -jar /edgex/edgex-device-bacnet/$1 $2 $3