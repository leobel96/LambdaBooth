# LambdaBooth
A simple guide to make a photobooth with python and a Raspberry Pi. This photobooth works in this way: a person push a button, a 5 seconds timer starts, after the 5 seconds a photo is taken using a DSLR camera connected to the Raspberry, the background of the photo is changed with a random background taken from a list provided by the user using chromakey technique, the original and modified photos are saved in two folders chosen by the user.

## Bill Of Materials
To make the Lambdabooth you need:
- A DSLR camera, please refer to [this list]() to make sure your camera is supported
- A Raspberry Pi
- A cable to connect your camera to USB (please refer to your camera's manual)
- A micro USB Power Supply for Raspberry Pi
- A big momentary push button to take the photo such as [this one](https://it.aliexpress.com/store/product/16mm-BIG-head-Plastic-Emergency-Stop-switch-1NO1NC-LA16-11ZS-A/2030101_32755091219.html?spm=a2g0y.12010108.1000016.1.34c85ab5uKJrBb&isOrigTitle=true)
- A momentary button to switch off Raspberry Pi
- A 7 segment display for the countdown such as [this one](https://www.aliexpress.com/item/Free-Shipping-1pcs-Common-Anode-1-Bit-Digital-Tube-7-segment-2-3-inch-Red-LED/32282721171.html?spm=a2g0s.8937460.0.0.6cae2e0ef7D98c)
- Material for the LambdaBooth's box. You can use wood, plastic,...
- Electric cables for connections

## Dependencies
1. Python 3 and pip3: If you have a recent version of Raspbian installed on your Raspberry Pi, they should already be installed
2. Gphoto2: It is necessary to control a DSLR camera using the raspberry. Installing it is as simple as: `sudo apt-get install gphoto2 libgphoto2*`
3. Opencv3: It is necessary for chromakeying. The installation is pretty long (it could require 4 hours on a first gen Raspberry Pi). To install it I have followed [this guide](https://www.life2coding.com/install-opencv-3-4-0-python-3-raspberry-pi-3/) from step 1 to step 11. There is also a [bash script](https://github.com/pageauc/opencv3-setup) that can simplify all the process and automate it but I've not tested it.
4. Maybe, in the end, you could notice errors when trying to import opencv module in Python. This is caused by other dependencies missing. In my case they were libatlas, libqt4 and libqt4-test. I've installed them in this way: `sudo apt-get install libatlas-base-dev libqt4 libqt4-test`. If you notice other errors caused by dependencies missing, please use Google to find a way to install them.

## Installation
1. Clone all the repository in your Raspberry Pi
2. Edit parameters in "LambdaBooth.py" according to your needs
3. Create a folder for original photos, a folder for backgrounds and a folder for edited photos paying attention to edit their paths in LambdaBooth.py
4. Make/seek backgrounds with the same dimensions of the original photo. The code tells you what is the right width and height
5. Add the possibility to shutdown the Raspberry Pi with the button following [this guide](https://github.com/raspberrypi/firmware/blob/master/boot/overlays/README#L619)
6. Make "Lambdabooth.py" autostart at boot adding it to crontab following [this guide](https://www.raspberrypi.org/forums/viewtopic.php?t=139774#p927101)
7. Connect the buttons according to your configuration and camera
8. Wire the display as shown [here]()

## TODO
- Video Demonstration
- Result Example
- Lambdabooth.py file
