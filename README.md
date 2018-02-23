"# myo_code" 

event_logger.py

usage: event_logger.py [-h] [-f OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -f OUTPUT, --output OUTPUT
                        Output file path if outputting to file

Pressing enter in the command prompt logs an event without any tags, while typing a tag first and then pressing enter logs an event with the tag.


Myo_Data_Collection.py

Install:
myo python library
myo_connect application from Thalmatic

Setup:
`echo "export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:/Developer/myo_sdk/myo.framework:/Applications/Myo Mapper.app/Contents/Frameworks/myo.framework" >> ~/.bash_profile

MyoConnect must be running in order to use code

usage: myo_data_collection.py [-h] [-d DESCRIPTION]
                              [-s [{stdout,file,local,dev,prod} [{stdout,file,local,dev,prod} ...]]]
                              [-e F_EMG] [-i F_IMU] [-t TIMEDELAY]

optional arguments:
  -h, --help            show this help message and exit
  
  -d DESCRIPTION, --description DESCRIPTION
                        The description of the reconding session
  
  -s [{stdout,file,local,dev,prod} [{stdout,file,local,dev,prod} ...]], --store [{stdout,file,local,dev,prod} [{stdout,file,local,dev,prod} ...]]
                        Where should results be stored?
  
  -e F_EMG              EMG Output file path if outputting to a file via
                        --store file
  
  -i F_IMU              IMU Output file path if outputting to a file via
                        --store file
  
  -t TIMEDELAY, --timedelay TIMEDELAY
                        Time to run the data collection for
