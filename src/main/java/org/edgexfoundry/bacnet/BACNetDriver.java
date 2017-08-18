/*******************************************************************************
 * Copyright 2016-2017 Dell Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @microservice:  device-bacnet
 * @author: Tyler Cox, Dell
 * @version: 1.0.0
 *******************************************************************************/
package org.edgexfoundry.bacnet;

import org.edgexfoundry.data.DeviceStore;
import org.edgexfoundry.data.ObjectStore;
import org.edgexfoundry.data.ProfileStore;
import org.edgexfoundry.domain.BACNetAttribute;
import org.edgexfoundry.domain.BACNetDevice;
import org.edgexfoundry.domain.BACNetObject;
import org.edgexfoundry.domain.ScanList;
import org.edgexfoundry.domain.meta.Addressable;
import org.edgexfoundry.domain.meta.ResourceOperation;
import org.edgexfoundry.handler.BACNetHandler;
import org.edgexfoundry.support.logging.client.EdgeXLogger;
import org.edgexfoundry.support.logging.client.EdgeXLoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

@Service
public class BACNetDriver {

	private final static EdgeXLogger logger = EdgeXLoggerFactory.getEdgeXLogger(BACNetDriver.class);
	
	@Autowired
	ProfileStore profiles;
	
	@Autowired
	DeviceStore devices;
	
	@Autowired
	ObjectStore objectCache;
	
	@Autowired
	BACNetHandler handler;
	
	@Autowired
	BacNetClient bacNetClient;
	
	public ScanList discover() {
		ScanList scan = new ScanList();
		return scan;
	}
	
	// operation is get or set
	// Device to be written to
	// BACNet Object to be written to
	// value is string to be written or null
	public void process(ResourceOperation operation, BACNetDevice device, BACNetObject object, String value, String transactionId, String opId) {
		String result = "";
		
		result = processCommand(operation.getOperation(), device.getAddressable(), object.getAttributes(), value);
		
		//if (result == null)
		//	devices.setDeviceByIdOpState(device.getId(), OperatingState.disabled);
		
		objectCache.put(device, operation, result);
		handler.completeTransaction(transactionId, opId, objectCache.getResponses(device, operation));
	}

	// Modify this function as needed to pass necessary metadata from the device and its profile to the driver interface
	public String processCommand(String operation, Addressable addressable, BACNetAttribute attributes, String value) {
		String intface = addressable.getAddress();
		intface +=  ":" + (addressable.getPort()==0 ? "47808" : addressable.getPort());
		logger.info("ProcessCommand: " + operation + ", address: " + intface + ", attributes: " + attributes + ", value: " + value );
		String result = "";
		Gson gson = new Gson();
		String request = gson.toJson(attributes);	
		JsonObject request_json = new JsonParser().parse(request).getAsJsonObject();
		request_json.addProperty("address", intface);
		
		try{
			if(operation.equals("get")){
				request = request_json.toString();
				result = bacNetClient.read(request);
			} else if(operation.equals("set")){
				Float fValue = Float.valueOf(value);
				request_json.addProperty("value", fValue);
				request = request_json.toString();
				result = bacNetClient.write(request);
			}
			if (result.contains("error"))
				throw new Exception();
			JsonObject args = new JsonParser().parse(result).getAsJsonObject();
			if (result.contains("value"))
				result = args.get("value").getAsString();
		} catch(Exception e) {
			result = null;
			logger.error("Address: " + intface + " Request: " + request + " Value: " + value);
		}
		
		return result;
	}

	public void initialize() {
	}
	
	public void disconnectDevice(Addressable address) {
	}

}
