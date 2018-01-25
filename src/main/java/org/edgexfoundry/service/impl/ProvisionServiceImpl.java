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
 * @microservice:  device-bluetooth
 * @version: 1.0.0
 *******************************************************************************/
package org.edgexfoundry.service.impl;

import java.io.File;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import javax.ws.rs.NotFoundException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import org.edgexfoundry.controller.DeviceProfileClient;
import org.edgexfoundry.config.ApplicationProperties;
import org.edgexfoundry.service.ProvisionService;
import org.edgexfoundry.service.YamlReader;
import org.edgexfoundry.domain.meta.DeviceProfile;

@Service
public class ProvisionServiceImpl implements ProvisionService {

	// private final Logger logger = LoggerFactory.getLogger(this.getClass());
	// replace above logger with EdgeXLogger below
	private final org.edgexfoundry.support.logging.client.EdgeXLogger logger = org.edgexfoundry.support.logging.client.EdgeXLoggerFactory
			.getEdgeXLogger(this.getClass());
	
	private Set<DeviceProfile> provisionedProfiles = Collections.synchronizedSet(new HashSet<>());

	@Autowired
	private DeviceProfileClient deviceProfileClient;

	@Autowired
	private YamlReader yamlReader;

	@Autowired
	private ApplicationProperties applicationProperties;

	@Override
	public void doProvision() {
		registerDeviceProfiles();
	}

	private void registerDeviceProfiles() {
		List<String> profileYamlPaths = applicationProperties.getDeviceProfilePaths();
		if (profileYamlPaths == null || profileYamlPaths.size() == 0)
			return;
		for (String path : profileYamlPaths) {
			File[] files = yamlReader.listYamlFiles(path);
			addProfileFromYamls(files);
		}
	}

	private void addProfileFromYamls(File[] files) {
		for (File yamlFile : files) {
			DeviceProfile deviceProfile = yamlReader.readYamlFileAsDeviceProfile(yamlFile);
			deviceProfile.setOrigin(System.currentTimeMillis());
			if (!isProfileExisting(deviceProfile)) {
				logger.debug("Device Profile: " + deviceProfile.getName() + "is not in DB.  Creating...");
				String id = deviceProfileClient.add(deviceProfile);
				deviceProfile.setId(id);
				provisionedProfiles.add(deviceProfile);
			} else {
				logger.debug("Device Profile: " + deviceProfile.getName() + "has already been in DB");
			}
		}
	}

	private boolean isProfileExisting(DeviceProfile deviceProfile) {
		boolean result = false;
		if (deviceProfile == null) {
			return result;
		}
		DeviceProfile retrievedDeviceProfile = fetchProfile(deviceProfile.getName());
		if (retrievedDeviceProfile != null) {
			provisionedProfiles.add(retrievedDeviceProfile);
			result = true;
		}
		return result;
	}

	private DeviceProfile fetchProfile(String deviceProfileName) {
		try {
			return deviceProfileClient.deviceProfileForName(deviceProfileName);
		} catch (NotFoundException nfE) {
			return null;
		}
	}

	@Override
	public Set<DeviceProfile> getProvisionedProfiles() {
		return provisionedProfiles;
	}

}
