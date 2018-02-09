#!/usr/bin/env python
# Copyright 2016-2017 Dell Inc.
# Copyright 2017-2018 Mobiliya
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
# @original author: Tyler Cox, Dell
# @updated by: Smit Sheth, Mobiliya
# @version: 1.0.0
from flask import Flask, request
from flask.json import jsonify
import collections
import binascii

from BACNetDriver import *

app = Flask(__name__)

def convert(data):
    if isinstance(data, bytearray):
        return "0x" + binascii.hexlify(data)
    elif "error" in data:
        return data
    else:
        return data

@app.route("/api/v1/ping")
def flask_ping():
    return "pong"
        
@app.route("/read", methods=['PUT', 'POST'])
def flask_read():
    data = request.get_json(force=True)
    address = data.get('address')
    obj_type = data.get('type')
    obj_inst = int(data.get('instance'))
    if (isinstance(obj_inst,str)):
        obj_inst = int(obj_inst)
    prop_id = data.get('property')
    bytes = convert(driver.read(obj_type, obj_inst, prop_id, address))
    if "error" in bytes:
        return bytes
    return jsonify(value=bytes)

@app.route("/write", methods=['PUT', 'POST'])
def flask_write():
    data = request.get_json(force=True)
    address = data.get('address')
    obj_type = data.get('type')
    obj_inst = int(data.get('instance'))
    prop_id = data.get('property')
    value = data.get('value')
    bytes = convert(driver.write(obj_type, obj_inst, prop_id, address, value))
    if "error" in bytes:
        return bytes
    return jsonify(value=bytes)

@app.route("/scan")
def flask_scan():
    scan_val = driver.scan()
    if(scan_val is not None):
    	scan_val = convert(driver.scan())
    print("Discovered device:",scan_val)	
    return  jsonify(scan=scan_val)
   
if __name__ == "__main__":
    global driver
    driver = StartServer()
    app.run(host='0.0.0.0',port=5002,threaded=True)

