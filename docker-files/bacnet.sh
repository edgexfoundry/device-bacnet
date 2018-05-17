#!/bin/sh

cd /edgex/edgex-resource-bacnet/virtualenv/bin/
source ./activate
python3 $4 -p $5 &
cd /edgex/edgex-device-bacnet
java -jar $1 $2 $3 $6 $7
