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
 * @original author: Tyler Cox, Dell
 * @updated by: Smit Sheth, Mobiliya
 * @version: 1.0.0
 *******************************************************************************/
package org.edgexfoundry.bacnet;

import java.util.Map;
import java.util.concurrent.locks.ReentrantLock;

import org.edgexfoundry.domain.ScanList;
import org.jboss.resteasy.client.jaxrs.ResteasyClient;
import org.jboss.resteasy.client.jaxrs.ResteasyClientBuilder;
import org.jboss.resteasy.client.jaxrs.ResteasyWebTarget;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class BacNetClientImpl implements BacNetClient{

	@Value("${bacnet.server}")
	private String bacNetServerURL;
	
	private ReentrantLock lock = new ReentrantLock();
	
	private BacNetClient getClient() {
		ResteasyClient client = new ResteasyClientBuilder().build();
		ResteasyWebTarget target = client.target(bacNetServerURL);
		return target.proxy(BacNetClient.class);
	}

	@Override
	public String read(String request) {
		lock.lock();
		try {
			return getClient().read(request);
		} catch (Exception e) {
			e.printStackTrace();
			//disconnect(address);
			return null;
		} finally {
			lock.unlock();
		}
	}

	@Override
	public String write(String request) {
		lock.lock();
		try {
			return getClient().write(request);
		} catch (Exception e) {
			e.printStackTrace();
			//disconnect(address);
			return null;
		} finally {
			lock.unlock();
		}
	}
	
	@Override
	public String initialize() {
		lock.lock();
		try {
			return getClient().initialize();
		} finally {
			lock.unlock();
		}
	}

	@Override
	public ScanList scanForDevices() {
		lock.lock();
		try {
			ScanList scanList = getClient().scanForDevices();
			for (Map<String, String> device : scanList.getScan())
				;
			return scanList;
		} finally {
			lock.unlock();
		}
	}
}
