# Pichler
Scripts for gathering data from [Pichler PKOM4](http://www.pichlerluft.at/heat-pump-combination-unit.html) heat pump unit.

## Setup
* Clone repo.
* Download [Nabto](https://downloads.nabto.com/assets/nabto-libs/4.3.0/nabto-libs.zip) libraries.
* Unpack libraries (.dll, .so) for your OS to `libs` folder.
* Provide device ID and credentials in `pichler.ini` file.
  * To prevent accidental commit of uour credentials, use `git update-index --skip-worktree pichler.ini`.
* Test your setup by running `python info.py`.  
  It should connect to your device and output basic runtime values.
