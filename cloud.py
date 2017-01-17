import pyicloud
import time
from sys import argv

script, login, password, timeout = argv
api = pyicloud.PyiCloudService(login, password)
with open('gps_log.txt', 'w') as log:
    while True:
        devices = api.devices
        for device in devices:
            time.sleep(int(timeout))
            latitude, longitude = (device.location()['latitude'],
                                   device.location()['longitude'])
            hour, minute, second = time.strftime("%H,%M,%S").split(',')
            currenttime = '{}:{}:{}'.format(hour, minute, second)
            print('{} {} {}'.format(currenttime, latitude, longitude))
            log.write('{} {} {}\n'.format(currenttime, latitude, longitude))
