# Draw GPS route on map

Because of Chrome safe settings it's necessary to run built-in python tiny web-server in script directory.

To do that open terminal window, change directory to project folder and type 

    python -m http.server 8000
    
After that you can run tracking script in another terminal window. 

To use the script run map.py with following arguments:

`python map.py your_icloud_login your_icloud_password gps_tracks_filename timeout_between_tracks`

Please note, that file with GPS track must have .gpx extension.

Run example:

`python map.py test@icould.com qwerty tracks.gpx 5`

While script is running, you will track GPS continiously.

To draw current track in your browser type `update` in terminal. Internet connection required.

To stop tracking use Ctrl+C.

In case you want to open map with track when script isn't working, use `open index.html` to watch map.
