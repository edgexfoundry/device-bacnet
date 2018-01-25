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
import java.io.FileInputStream;
import java.io.FilenameFilter;
import java.util.Map;

import org.springframework.stereotype.Service;
import org.yaml.snakeyaml.Yaml;

import org.edgexfoundry.service.YamlReader;
import org.edgexfoundry.domain.meta.DeviceProfile;
import org.edgexfoundry.exception.controller.DataValidationException;

@Service
public class YamlReaderSnakeImpl implements YamlReader {

	//private final Logger logger = LoggerFactory.getLogger(this.getClass());
	//replace above logger with EdgeXLogger below
	private final org.edgexfoundry.support.logging.client.EdgeXLogger logger = 
			org.edgexfoundry.support.logging.client.EdgeXLoggerFactory.getEdgeXLogger(this.getClass());

	@Override
	public File[] listYamlFiles(String path) {
		File dir = new File(path);
		File[] files = dir.listFiles(new FilenameFilter() {
			@Override
			public boolean accept(File dir, String name) {
				return name.endsWith(".yml") || name.endsWith(".yaml");
			}
		});
		return files;
	}

	@SuppressWarnings("unchecked")
	@Override
	public Map<String, Object> readYamlFileAsMap(File file) {
		try (FileInputStream fis = new FileInputStream(file)) {
			Yaml yaml = new Yaml();
			return (Map<String, Object>) yaml.load(fis);
		} catch (Exception ex) {
			logger.error("Exception occurs when reading Yaml file:" + file.getPath(), ex);
			throw new DataValidationException("Error parsing device profile from YAML: " + file.getPath());
		}
	}

	@Override
	public DeviceProfile readYamlFileAsDeviceProfile(File file) {
		try (FileInputStream fis = new FileInputStream(file)) {
			Yaml yaml = new Yaml();
			return yaml.loadAs(fis, DeviceProfile.class);
		} catch (Exception ex) {
			logger.error("Exception occurs when reading Yaml file:" + file.getPath(), ex);
			throw new DataValidationException("Error parsing device profile from YAML: " + file.getPath());
		}
	}

}
