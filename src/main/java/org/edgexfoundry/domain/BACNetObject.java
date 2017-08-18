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
package org.edgexfoundry.domain;

import org.edgexfoundry.domain.BACNetAttribute;
import org.edgexfoundry.domain.meta.DeviceObject;

public class BACNetObject extends DeviceObject {

	private BACNetAttribute attributes;

	public BACNetObject(DeviceObject object) {
		this.setName(object.getName());
		this.setTag(object.getTag());
		this.setDescription(object.getDescription());
		this.setProperties(object.getProperties());
		this.setAttributes(new BACNetAttribute(object.getAttributes()));
	}
	
	@Override
	public BACNetAttribute getAttributes() {
		return attributes;
	}
	
	public void setAttributes(BACNetAttribute attributes) {
		this.attributes = attributes;
	}

	@Override
	public String toString() {
		return "BACNetObject [ " + super.toString() + ", attributes=" + attributes + "]";
	}

}
