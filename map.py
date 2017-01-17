from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from scipy.misc import imread
import numpy as np
from datetime import datetime
from sys import argv
import os
import subprocess
import urllib


def bound(lonmin, latmin, lonmax, latmax, directory):
    bound_string = "{}, {}, {}, {}".format(lonmin, latmin, lonmax, latmax)

    master_string = "clear-map\nchange-directory {}/\n" \
                    "load-source {}/kart.osm\n" \
                    "use-ruleset alias=default\n" \
                    "set-print-bounds-geo {}" \
                    "\nexport-bitmap scale=10" \
                    " file=gpsdraw.png\n".format(directory,
                                                 directory, bound_string)

    filename = 'tegngps.mscript'
    with open(filename, 'w') as file_handler:
        file_handler.write(master_string)


def check_connection():
    # Check if we're online
    print("---Check network availability")
    try:
        r = urllib.request.urlopen('http://84.208.42.38', timeout=10)
    except:
        return False
    if r:
        print("\tSuccess")
    else:
        print("\tFail")
    return r


def get_work_dir():
    return (subprocess.check_output('pwd', shell=True)[:-1]).decode("utf-8")


def collect_data_from_log(gps_log):
    print("---Data extraction")
    with open(gps_log, 'r') as file_handler:
        return file_handler.readlines()


def get_coordinates_list(gps_file):
    return [line.rstrip('\n') for line in gps_file]


def get_times_lats_longs(log):
    return ([(row.split()[0]) for row in log],
            [float(row.split()[1]) for row in log],
            [float(row.split()[2]) for row in log])


def get_start_stop_points(list_of_coordinates):
    return list_of_coordinates[0], list_of_coordinates[-1]


def get_start_stop_time(list_of_time):
    return [datetime.strptime(time, '%H:%M:%S') for time in
            [list_of_time[-0], list_of_time[-1]]]


def find_map_crop(longitude_list, latitude_list):
    print("---Finding map crop")
    delta = max(longitude_list) - min(longitude_list)
    padding = 0.2 * delta

    return ((min(longitude_list) - padding),
            (min(latitude_list) - padding),
            (max(longitude_list) + padding),
            (max(latitude_list) + padding))


def download_osm_file(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat):
    print("---Loading OSM map data")
    wget_command = 'wget --show-progress -q -O kart.osm ' \
                   '"http://overpass-api.de/api/map?bbox={},{},{},{}"'.format(
                    llcrnrlon,
                    llcrnrlat,
                    urcrnrlon,
                    urcrnrlat)
    subprocess.call(wget_command, shell=True)


def convert_osm_to_png(directory):
    print("---Maperative launch")
    maperative = 'mono /Applications/Maperitive/Maperitive.exe'
    map_command = ' -exitafter -defaultscript {}/tegngps.mscript'.format(directory)
    with open(os.devnull, 'w') as null:
        subprocess.call(maperative + map_command, stdout=null,
                        stderr=subprocess.STDOUT, shell=True)


def draw_blank_map():
    basemap.drawcoastlines()
    basemap.drawcountries()
    basemap.drawmapboundary(fill_color='aqua')
    basemap.fillcontinents(color='green', lake_color='aqua')
    basemap.drawmeridians(np.arange(0, 360, 0.5))
    basemap.drawparallels(np.arange(-90, 90, 0.5))

if __name__ == '__main__':
    work_dir = get_work_dir()
    script, gps_log_path = argv
    gps_lines = collect_data_from_log(gps_log_path)
    coordinates_list = get_coordinates_list(gps_lines)
    time_list, lat_list, lon_list = get_times_lats_longs(coordinates_list)
    start_lat, stop_lat = get_start_stop_points(lat_list)
    start_lon, stop_lon = get_start_stop_points(lon_list)
    start_time, stop_time = get_start_stop_time(time_list)
    llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat = find_map_crop(lon_list, lat_list)
    print("\tLonMin %s" % llcrnrlon)
    print("\tLatMin %s" % llcrnrlat)
    print("\tLonMax %s" % urcrnrlon)
    print("\tLatMax %s" % urcrnrlat)
    response = check_connection()
    if response:
        download_osm_file(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat)
        # Bounds settings for Maperative
        bound(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat, work_dir)
        convert_osm_to_png(work_dir)
    else:
        print("---No network connection")

    # Creating the map
    print("---Storing Basemap")
    basemap = Basemap(projection='merc', lat_0=stop_lat, lon_0=stop_lon,
                      resolution='l', area_thresh=0.1,
                      llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat,
                      urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat)

    if response is False:
        draw_blank_map()

    x, y = basemap(lon_list, lat_list)
    x0, y0 = basemap(start_lon, start_lat)
    x1, y1 = basemap(stop_lon, stop_lat)

    basemap.plot(x, y, color='r', linewidth=1,
                 label='Testrute')  # Lines between the points
    basemap.plot(x0, y0, 'bo', markersize=2)  # Plot start
    basemap.plot(x1, y1, 'b+', markersize=2)  # Plot finish

    start_label = 'START\n{}\n{}\n{}'.format(str(start_time)[11:], start_lat,
                                             start_lon)
    stop_label = 'FINISH\n{}\n{}\n{}'.format(str(stop_time)[11:], stop_lat,
                                             stop_lon)

    plt.text(x0 - 350, y0, start_label, fontsize=3)
    plt.text(x1 + 150, y1, stop_label, fontsize=3)

    if response:
        print("---Add png for background")
        img = imread("gpsdraw.png")
        basemap.imshow(img, zorder=1, origin='upper')
    title_string = gps_log_path
    plt.title(title_string)
    print("---Saving image")
    plt.plot()
    plt.savefig('{}.png'.format(gps_log_path), bbox_inches='tight', dpi=500)

    print("---Cleaning temporary files")
    with open(os.devnull) as null:
        subprocess.call('rm -rf kart.osm tegngps.mscript gpsdraw.png',
                        stdout=null, stderr=subprocess.STDOUT, shell=True)
