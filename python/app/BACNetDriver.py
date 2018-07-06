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
import atexit, threading, socket, yaml, struct
from bacpypes.core import run as run_bacpypes
from bacpypes.pdu import Address, GlobalBroadcast
from bacpypes.service.device import LocalDeviceObject
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import get_object_class, get_datatype
from bacpypes.apdu import (ReadPropertyMultipleRequest,
                           PropertyReference,
                           ReadPropertyRequest,
                           ReadAccessSpecification,
                           Error,
                           AbortPDU,
                           ReadPropertyACK,
                           WhoIsRequest,
                           WritePropertyRequest,
                           IAmRequest)
from bacpypes.primitivedata import Null, Atomic, Integer, Unsigned, Real, CharacterString
from bacpypes.constructeddata import Array, Any
from bacpypes.basetypes import PropertyIdentifier, ServicesSupported
from bacpypes.errors import DecodingError
from bacpypes.iocb import IOCB


def docker_test():
    if socket.gethostname() == "edgex-device-bacnet":
        return True
    return False

def StartServer():
    global _ss
    _ss = BACNetDriver()
    _ss.run()
    return _ss

# some debugging
_debug = 0

class BACNetDriver(BIPSimpleApplication):
    def __init__(self, *args):
        # register signal handler
        atexit.register(self._interrupt)
        # threading init
        self._parent_thread = threading.current_thread()
        self._done = False
        
        # store configuration
        self._configfile = 'application.properties'
        self._config = None

        # setup a bacnet stack thread
        self.bacnet_app = None
        self._bacnet_thread = threading.Thread(target=self._run_bacnet)
        self._bacnet_thread.daemon = True
        self._request = None

    def run(self):
        self._load_config()
        self._init_bacnet()
        self._bacnet_thread.start()
        
    def _interrupt(self):
        self._done = True
        
    def _load_config(self):
        self._config = Config()
        try:
            self._config.load(self._configfile)
        except Exception:
            import distutils.sysconfig
            self._configfile = '/'.join((distutils.sysconfig.get_python_lib(),'app', 'application.properties'))
            self._config.load(self._configfile)
        
    def _init_bacnet(self):
        # local bacnet device 
        ldo = LocalDeviceObject(
            objectName=self._config.bacnet.get('objectName'),
            objectIdentifier=int(self._config.bacnet.get('objectIdentifier')),
            maxApduLengthAccepted=int(self._config.bacnet.get('maxApduLengthAccepted')),
            segmentationSupported=self._config.bacnet.get('segmentationSupported'),
            vendorIdentifier=int(self._config.bacnet.get('vendorIdentifier')),)

        # Send an empty support string
        pss = ServicesSupported()
        ldo.protocolServicesSupported = pss.value

        # TODO: look to use domain name resolution on address
        info = self._config.bacnet.get('address')
        hostname = ""
        for i, c in enumerate(info):
            if c is '/' or c is ':':
                break
            hostname += c
        suffix = info[i:]

        # MRH: The way BACpypes binds to the interface for broadcast is tricky with containers
        #      overload this for now
        if docker_test():
            import fcntl
            hostname = socket.gethostname()
            netmask = socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 0x891b, struct.pack(b'256s', b'eth0'))[20:24])
            suffix = "/" + str(sum([bin(int(x)).count('1') for x in netmask.split('.')])) + ":47808"

        print("host %s" % hostname)
        addr = socket.gethostbyname(hostname)
        print("bacnet stack using %s" % (addr + suffix))
        self.this_application = DiscoveryApplication(ldo, addr + suffix)

    def _value_format(self, p, v):
        return str(v)

        
    def _run_bacnet(self):
        # go into main loop
        while not self._done and self._parent_thread.is_alive():
            try:
                run_bacpypes()     # run bacnet
            except e as Exception:
                print("caught bacnet exception %s" % e)
                continue
            else:
                print("shutting down bacnet thread")

    def read(self, obj_type, obj_inst, prop_id, address):
        datatype = get_datatype(obj_type, prop_id)
        if not datatype:
            print("invalid property %s for object type %s" % (prop_id,obj_type))
            return "error invalid property %s for object type %s" % (prop_id,obj_type)

        # build a request
        request = ReadPropertyRequest(objectIdentifier=(obj_type, obj_inst), propertyIdentifier=prop_id)
        request.pduDestination = Address(address)

        # TODO: How do we handle an index? This is a 'parameterized get' case that uses b
        # request.propertyArrayIndex = <handle me>

        # build an IOCB, save the request
        iocb = IOCB()
        iocb.ioRequest = request

        # give it to the application to send
        _ss.this_application.do_request(request, iocb)
        
        # wait for the response
        iocb.ioComplete.wait()

        # filter out errors and aborts
        if isinstance(iocb.ioResponse, Error) or isinstance(iocb.ioResponse, AbortPDU):
            print( "get operation failed %s %s %s" % (obj_type, obj_inst, str(iocb.ioResponse)))
            n = "error get operation failed %s %s %s" % (obj_type, obj_inst, str(iocb.ioResponse))
        else:
            n = self._value_format(prop_id,iocb.ioResponse)
            
        print("read %s %s %s %s" % (address, obj_inst, prop_id, n))

        return n
        
        
    def write(self, obj_type, obj_inst, prop_id, address,  value):
        n = ""
        datatype = get_datatype(obj_type, prop_id)
        if not datatype:
            return "error invalid property %s for object type %s" % (prop_id,obj_type)

        # set a priority
        priority = 1 #o.get('priority') if o.get('priority') else 1

        # TODO: How do we handle an index? This is a 'parameterized set' case
        indx = None

        # change atomic values into something encodeable, null is a special case
        if (value == 'null'):
            value = Null()
        elif issubclass(datatype, Atomic):
            if datatype is Integer:
                value = int(value)
            elif datatype is Real:
                value = float(value)
            elif datatype is Unsigned:
                value = int(value)
            value = datatype(value)
        elif issubclass(datatype, Array) and (indx is not None):
            if indx == 0:
                value = Integer(value)
            elif issubclass(datatype.subtype, Atomic):
                value = datatype.subtype(value)
            elif not isinstance(value, datatype.subtype):
                return "error invalid result datatype, expecting %s" % (datatype.subtype.__name__,)
        elif not isinstance(value, datatype):
            return "error invalid result datatype, expecting %s" % (datatype.subtype.__name__,)

        # build a request
        request = WritePropertyRequest(objectIdentifier=(obj_type, obj_inst), propertyIdentifier=prop_id)
        request.pduDestination = Address(address)

        # save the value
        request.propertyValue = Any()
        try:
            request.propertyValue.cast_in(value)
        except e as Exception:
            return "error write property cast error %r" % e

        # optional array index
        if indx is not None:
            request.propertyArrayIndex = indx

        # optional priority
        if priority is not None:
            request.priority = priority

        # build an IOCB, save the request
        iocb = IOCB()
        iocb.ioRequest = request

        # give it to the application to send
        _ss.this_application.do_request(request, iocb)
        
        # wait for the response
        iocb.ioComplete.wait()

        # filter out errors and aborts
        if isinstance(iocb.ioResponse, Error) or isinstance(iocb.ioResponse, AbortPDU):
            return "error set operation failed %s %s %s" % (obj_inst, prop_id, str(iocb.ioResponse))
            
        print("wrote %s %s %s %s" % (address, obj_inst, prop_id, value))

        return n

    def scan(self):
        addr = GlobalBroadcast()
        self.this_application.who_is(None, None, addr)
        return self.this_application.getdevice_discovered()
#
#   DiscoveryApplication
#
class DiscoveryApplication(BIPSimpleApplication):

    def __init__(self, *args):
        BIPSimpleApplication.__init__(self, *args)
        # keep track of requests to line up responses
        self.who_is_request = None
        # assigning invoke identifiers
        self.nextInvokeID = 1
        # keep track of requests to line up responses
        self.iocb = {}
        
        self.deviceinfo=None

    def request(self, apdu):
        """Sniff for Who-Is requests going downstream."""
        # save a copy of just the Who-Is request
        if isinstance(apdu, WhoIsRequest):
            self.who_is_request = apdu

        # forward it along
        BIPSimpleApplication.request(self, apdu)

    def get_next_invoke_id(self, addr):
        initialID = self.nextInvokeID
        while 1:
            invokeID = self.nextInvokeID
            self.nextInvokeID = (self.nextInvokeID + 1) % 256
            # see if we've checked for them all
            if initialID == self.nextInvokeID:
                raise RuntimeError("no available invoke ID")
            # see if this one is used
            if (addr, invokeID) not in self.iocb:
                break
        return invokeID

    def do_request(self, apdu, iocb):
        # assign an invoke identifier
        apdu.apduInvokeID = self.get_next_invoke_id(apdu.pduDestination)
        # build a key to reference the IOCB when the response comes back
        invoke_key = (apdu.pduDestination, apdu.apduInvokeID)
        # keep track of the request
        self.iocb[invoke_key] = iocb
        # forward it along, apduInvokeID set by stack
        BIPSimpleApplication.request(self, apdu)

    def confirmation(self, apdu):
        # build a key to look for the IOCB
        invoke_key = (apdu.pduSource, apdu.apduInvokeID)
        # find the request
        iocb = self.iocb.get(invoke_key, None)
        if not iocb:
            super()._app_complete(apdu.pduSource, apdu)
            return;

        del self.iocb[invoke_key]

        if isinstance(apdu, Error):
            iocb.ioResponse = apdu
        elif isinstance(apdu, AbortPDU):
            iocb.ioResponse = apdu
        elif (isinstance(iocb.ioRequest, ReadPropertyRequest)) and (isinstance(apdu, ReadPropertyACK)):
            # find the datatype
            datatype = get_datatype(apdu.objectIdentifier[0], apdu.propertyIdentifier)
            if not datatype:
                raise TypeError( "unknown datatype")

            # special case for array parts, others are managed by cast_out
            if issubclass(datatype, Array) and (apdu.propertyArrayIndex is not None):
                if apdu.propertyArrayIndex == 0:
                    value = apdu.propertyValue.cast_out(Unsigned)
                else:
                    value = apdu.propertyValue.cast_out(datatype.subtype)
            else:
                value = apdu.propertyValue.cast_out(datatype)

            # assume primitive values for now, JSON would be better
            iocb.ioResponse = value

            # find the datatype
            datatype = get_datatype(apdu.objectIdentifier[0], apdu.propertyIdentifier)
            if not datatype:
                raise TypeError( "unknown datatype")

            # special case for array parts, others are managed by cast_out
            if issubclass(datatype, Array) and (apdu.propertyArrayIndex is not None):
                if apdu.propertyArrayIndex == 0:
                    value = apdu.propertyValue.cast_out(Unsigned)
                else:
                    value = apdu.propertyValue.cast_out(datatype.subtype)
            else:
                value = apdu.propertyValue.cast_out(datatype)

            # assume primitive values for now, JSON would be better
            iocb.ioResponse = value
        else:
            iocb.ioResponse = 'ok'

        # trigger the completion event
        iocb.ioComplete.set()
        
    def do_IAmRequest(self, apdu):    
        """Do something with incoming I-Am requests."""
        if _debug: DiscoveryApplication._debug("do_IAmRequest %r", apdu)

        # check for required parameters
        if apdu.iAmDeviceIdentifier is None:
            raise MissingRequiredParameter("iAmDeviceIdentifier required")
        if apdu.maxAPDULengthAccepted is None:
            raise MissingRequiredParameter("maxAPDULengthAccepted required")
        if apdu.segmentationSupported is None:
            raise MissingRequiredParameter("segmentationSupported required")
        if apdu.vendorID is None:
            raise MissingRequiredParameter("vendorID required")

        # extract the device instance number
        device_instance = apdu.iAmDeviceIdentifier[1]
        if _debug: DiscoveryApplication._debug("    - device_instance: %r", device_instance)

        # extract the source address
        device_address = apdu.pduSource
        if _debug: DiscoveryApplication._debug("    - device_address: %r", device_address)

        # we didn't request anything yet
        if not self.who_is_request:
            return

        if (self.who_is_request.deviceInstanceRangeLowLimit is not None) and \
                (device_instance < self.who_is_request.deviceInstanceRangeLowLimit):
            pass
        elif (self.who_is_request.deviceInstanceRangeHighLimit is not None) and \
                (device_instance > self.who_is_request.deviceInstanceRangeHighLimit):
            pass
        else:
            # build a request for the object name
            request = ReadPropertyRequest(
                destination=apdu.pduSource,
                objectIdentifier=apdu.iAmDeviceIdentifier,
                propertyIdentifier='objectName',
                )

            # make an IOCB
            iocb = IOCB(request)
            if _debug: DiscoveryApplication._debug("    - iocb: %r", iocb)
            # let us know when its complete
            iocb.add_callback(self.device_discovered)
            # give it to the application
            self.request_io(iocb)

    def getdevice_discovered(self):          
        return self.deviceinfo

    def device_discovered(self, iocb):
        if _debug: DiscoveryApplication._debug("device_discovered %r", iocb)
       
        # do something for error/reject/abort
        if iocb.ioError:
            sys.stdout.write(str(iocb.ioError) + '\n')

        # do something for success
        elif iocb.ioResponse:
                apdu = iocb.ioResponse
                # should be an ack
                if not isinstance(apdu, ReadPropertyACK):
                        if _debug: DiscoveryApplication._debug("    - not an ack")
                        return
                # pull out the name
                device_name = apdu.propertyValue.cast_out(CharacterString)
                if _debug: DiscoveryApplication._debug("    - device_name: %r", device_name)
                self.deviceinfo=[{"name":device_name,"address":repr(apdu.pduSource)}]
        # do something with nothing?
        else:
                if _debug: DiscoveryApplication._debug("     - ioError or ioResponse expected")

class Config():

    def load(self, filename):
        f = open(filename,'r')
        _config = yaml.load(f)
        f.close()
        self.__dict__.update(_config)

    def store(self,filename):
        f = open(filename,'w')
        yaml.dump(self.__dict__, f, default_flow_style=False)
        f.close()

        
if __name__ == "__main__":
    StartServer()
