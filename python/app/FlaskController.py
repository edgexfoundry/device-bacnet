#!/usr/bin/env python
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

if __name__ == "__main__":
    global driver
    driver = StartServer()
    app.run(host='0.0.0.0',port=5002,threaded=True)

