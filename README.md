Meteor Network Station
=====

An automated meteor station software for Petnica Meteor Network. The automation right now includes:
- Turning the camera on at night and off in the morning
- Opening and closing the camera shutter
- Measuring camera compartment temperature and humidity
- Self update
- Sending information to a central server that overviews the whole network.

Planned automations:
- Garbage meteor data cleanup
- Meteor data upload to central server
- Cloudiness estimation

Running
=====

Code has been tested on Linux and Windows, both 32 and 64 bit.
To run, place the project on the partition where meteor data will be stored and execute start.py with administrator privileges. (Requires Python 3.4+).
