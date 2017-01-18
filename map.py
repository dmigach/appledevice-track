import gpxpy
import gpxpy.gpx
import cloud
from sys import argv
import webbrowser
import os
from urllib.request import pathname2url
import threading
import sys
import time


def open_gps_log(path):
    with open(path, 'r') as gps_track:
        return gpxpy.parse(gps_track)


def create_gps_log(path):
    with open(path, 'w') as gps_track:
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        gps_track.write(gpx.to_xml())
        return gpx


def append_points_to_track(points, gpx):
    track = gpx.tracks[0]
    for segment in track.segments:
        for point in points:
            segment.points.append(
                gpxpy.gpx.GPXTrackPoint(point[0] , point[1]))
    return gpx


def save_gpx_to_file(gpx, path):
    with open(path, 'w') as gpx_file:
        gpx_file.write(gpx.to_xml())


def format_html_template(latitude, longitude, zoom):
    with open('html_template.html', 'r') as file_handler:
        html = file_handler.read()
        path_for_format = '\"{}\"'.format(path_to_track)
        html = html.format(latitude=latitude, longitude=longitude, zoom=zoom,
                           path=path_for_format)
    with open('index.html', 'w') as file_handler:
        file_handler.write(html)


def open_widget():
    localhost = 'http://localhost:8000'
    #url = 'file:{}'.format(pathname2url(os.path.abspath('index.html')))
    webbrowser.open(localhost)


def input_thread(flag):
    print('Gathering GPS coordinate every {} seconds...'.format(timeout))
    inp = input('Type \'update\' to update track on map\n'
                'Use Ctrl+C to stop tracking\n')
    if inp == 'update':
        open_widget()
    flag.append(None)


def main(path, timeout):
    flag = []
    threading._start_new_thread(input_thread, (flag,))
    while not flag:
        try:
            time.sleep(timeout)
            new_tracks = []
            latitude, longitude = cloud.track_gps(device)
            #print('---Got track')
            new_tracks.append((latitude, longitude))
            if os.path.exists(path):
                gpx = open_gps_log(path)
            else:
                gpx = create_gps_log(path)
            if new_tracks:
                gps_points = new_tracks
                gpx = append_points_to_track(gps_points, gpx)
            track = gpx.tracks[0]
            segment = track.segments[0]
            latitudes = []
            longitudes = []
            for point in segment.points:
                latitudes.append(point.latitude)
                longitudes.append(point.longitude)
            save_gpx_to_file(gpx, path_to_track)

            lat = (max(latitudes) + min(latitudes)) / 2
            lon = (max(longitudes) + min(longitudes)) / 2
            ran = max((max(latitudes) - min(latitudes)),
                      (max(longitudes) - min(longitudes)))
            zoom = int(12 - (ran * 12 / 25))
            if zoom < 0:
                zoom = 0
            format_html_template(lat, lon, zoom)
            continue
        except KeyboardInterrupt:
            print("Shutdown requested...exiting")
        sys.exit(0)


if __name__ == '__main__':
    _ , login, password, path_to_track, timeout = argv
    print('---Connecting to iCloud...')
    cloud_api = cloud.cloud_login(login, password)
    device = cloud_api.devices[0]
    print('---Success. Starting tracking...')
    while True:
        main(path_to_track, int(timeout))




