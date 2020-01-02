# Pichler
Scripts for gathering data from [Pichler PKOM4](http://www.pichlerluft.at/heat-pump-combination-unit.html) heat pump unit.

## Setup
* Clone repo.
* Download [Nabto](https://downloads.nabto.com/assets/nabto-libs/4.3.0/nabto-libs.zip) libraries.
* Unpack libraries (.dll, .so) for your OS to `libs` folder.
* Provide device ID and credentials in `pichler.ini` file.
  * To prevent accidental commit of your credentials, use:  
  `git update-index --skip-worktree pichler.ini`
* Test your setup by running `python info.py`.  
  It should connect to your device and output basic runtime values.
* If you want to collect unit's data to Influx database you should also:
  * Install [Influxdb](https://www.influxdata.com/blog/getting-started-python-influxdb/) python module:  
  `python -m pip install influxdb`
  * Provide Influx database setup in `collect.ini` file.

## Collecting data
You can use `collect.py` script for periodic data collection on background. Script reads selected values (`data_points` array) from Pichler unit and stores them to [Infux](https://www.influxdata.com) database.

Data will be read every minute and stored to db only when changed since last reading (or once an hour).

`Influx` database setup (host, credentials, database name) is taken from `collect.ini` file.

To run `collect.py` in background use:  
`python -u collect.py > collect.log 2>&1 &`
