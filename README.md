# Pichler
Scripts for gathering data from [Pichler PKOM4](http://www.pichlerluft.at/heat-pump-combination-unit.html) heat pump unit.

## Setup
* Clone repo.
* Install dependencies (if you want to collect data):  
  `python -m pip install -r requirements.txt`
* Download [Nabto](https://downloads.nabto.com/assets/nabto-libs/4.4.0/nabto-libs.zip) libraries.
* Unpack libraries (.dll, .so) for your OS to `libs` folder.
* Set device id and user name/password using environment variables:
  * `PICHLER_DEVICE_ID`
  * `PICHLER_USER`
  * `PICHLER_PASSWORD`
* Set MQTT host/port using environment variables:
  * `MQTT_HOST`
  * `MQTT_PORT`
* Test your setup by running `python info.py`.  
  It should connect to your device and output basic runtime values.

## Collecting data
You can use `collect.py` script for periodic data collection on background.  
Script reads selected values (`data_points` array) from Pichler unit and publishes them to MQTT broker.

Data will be read and published every minute.

To run `collect.py` in background use:  
`python -u collect.py > collect.log 2>&1 &`
