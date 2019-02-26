#! /bin/sh
sudo apt-get update
sudo pip3 install pyyaml
sudo apt-get install gphoto2 libgphoto2*
sudo pip3 install gphoto2
sudo pip install opencv-contrib-python
sudo pip3 install --upgrade requests
sudo pip3 install Flask
sudo apt-get install libcups2-dev --fix-missing
sudo pip3 install pycups
sudo apt install firefox-esr

# OpenCV dependencies
sudo apt-get install libhdf5-dev
sudo apt-get update
sudo apt-get install libhdf5-serial-dev
sudo apt install libqtcore4 libqtgui4 libqt4-test
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
sudo apt-get install libqtgui4
sudo apt-get install python3-pyqt5
sudo chmod -x /usr/lib/gvfs/gvfs-gphoto2-volume-monitor
sudo chmod -x /usr/lib/gvfs/gvfsd-gphoto2