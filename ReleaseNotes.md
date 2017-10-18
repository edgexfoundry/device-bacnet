# v0.2 (10/20/2017)
# Release Notes

## Notable Changes
The Barcelona Release (v 0.2) of the BACnet micro service includes the following:
* POM changes for appropriate repository information for distribution/repos management, checkstyle plugins, etc.
* Removed all references to unfinished DeviceManager work as part of Dell Fuse
* Added Dockerfile for creation of micro service targeted for ARM64
* Consolidated Docker properties files to common directory

## Bug Fixes
* Fixed Consul configuration properties
* Fixed Device equality logic
* Added check for service existence after initialization to Base Service
 
## Pull Request/Commit Details
 - [#18](https://github.com/edgexfoundry/device-bacnet/pull/18) - Remove staging plugin contributed by Jeremy Phelps ([JPWKU](https://github.com/JPWKU))
 - [#17](https://github.com/edgexfoundry/device-bacnet/pull/17) - Adds null check in BaseService contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#16](https://github.com/edgexfoundry/device-bacnet/pull/16) - Fixes Maven artifact dependency path contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#15](https://github.com/edgexfoundry/device-bacnet/pull/15) - Add public nexus group to base pom contributed by Jeremy Phelps ([JPWKU](https://github.com/JPWKU))
 - [#14](https://github.com/edgexfoundry/device-bacnet/pull/14) - Add staging and release repo definitions contributed by Jeremy Phelps ([JPWKU](https://github.com/JPWKU))
 - [#13](https://github.com/edgexfoundry/device-bacnet/pull/13) - Removed device manager url refs in properties files contributed by Jim White ([jpwhitemn](https://github.com/jpwhitemn))
 - [#12](https://github.com/edgexfoundry/device-bacnet/pull/12) - Added support for aarch64 arch contributed by ([feclare](https://github.com/feclare))
 - [#11](https://github.com/edgexfoundry/device-bacnet/pull/11) - Fixes device comparison logic contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#10](https://github.com/edgexfoundry/device-bacnet/pull/10) - Fixes startup script contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#9](https://github.com/edgexfoundry/device-bacnet/pull/9) - Consolidates Docker properties files contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#8](https://github.com/edgexfoundry/device-bacnet/pull/8) - Fixes Consul Properties contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#7](https://github.com/edgexfoundry/device-bacnet/pull/7) - Adds Docker build capability contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#6](https://github.com/edgexfoundry/device-bacnet/pull/6) - Add distributionManagement for artifact storage contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#5](https://github.com/edgexfoundry/device-bacnet/pull/5) - fix change of packaging for schedule clients contributed by Jim White ([jpwhitemn](https://github.com/jpwhitemn))
 - [#4](https://github.com/edgexfoundry/device-bacnet/pull/4) - Fixes settings files contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#2](https://github.com/edgexfoundry/device-bacnet/pull/2) - Contributed Project Fuse source code contributed by Tyler Cox ([trcox](https://github.com/trcox))
 - [#1](https://github.com/edgexfoundry/device-bacnet/pull/1) - Added README.md contributed by Jeremy Phelps ([JPWKU](https://github.com/JPWKU))
