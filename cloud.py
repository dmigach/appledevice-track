import pyicloud
import time


def cloud_login(login, password):
    return pyicloud.PyiCloudService(login, password)


def track_gps(device):
    latitude, longitude = (device.location()['latitude'],
                           device.location()['longitude'])
    hour, minute, second = time.strftime("%H,%M,%S").split(',')
    currenttime = '{}:{}:{}'.format(hour, minute, second)
    #track = '{} {} {}'.format(currenttime, latitude, longitude)
    return latitude, longitude
