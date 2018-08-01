
<p align="center">
  <img
    alt="Logo"
    src="https://github.com/leobel96/LambdaBooth/blob/master/images/logo.svg"
    width="500"
  />
</p>


LambdaBooth is an hardware and software photobooth that can make your parties even more funny.


## How it works
These are the LambdaBooth functions: 
1. A person pushes a button (BUTTON).
2. 5 seconds timer starts (COUNTDOWN).
3. After the 5 seconds a photo is taken using a supported DSLR camera connected to the Raspberry and saved in a folder chosen by the user (CAMERA).
4. The background of the photo is changed with a random background taken from a folder provided by the user using chromakey technique (CHROMAKEY).
5. An overlay image (frame, watermark, logo, ...), with the same dimensions of the photo, is put on the photo (OVERLAY).
6. The final photo is uploaded to a Google Photos album chosen by the user (UPLOAD).

The user can switch on/off every function of the six provided without any issue from the "enable/disable features" menu in the file "LambdaBooth.py":
```
## ENABLE/DISABLE FEATURES
BUTTON = 1      #use/don't use button
COUNTDOWN = 0       #use/don't use countdown
CAMERA = 1      #use/don't use camera
CHROMAKEY = 0      #use/don't use chromakey
OVERLAY = 1   #use/don't use overlay
UPLOAD = 1   #use/don't use google photos upload
```
and he can also configure every aspect from "user configuration" menu:
```
## USER CONFIGURATION
button_GPIO = 18    #pin to which button is connected (GPIO_pin and GND)
segments_GPIO = (5,6,13,19,26,16,20) #pins connected in order to a,b,c,d,e,f segments
camera_path = "in/"    #destination folder for photo taken
default_photo = "in/front3.png"     #photo used with no camera
background_path = "background/"    #source folder for backgrounds
out_path = "out/"   #destination folder for photo processed
overlay_image = "Risorsa1.png"   #image used for overlay (logo, frame, ...)
album_name = "nome"   #name used for google photos album creation
credentials_file = "credentials.json"   #file with google photos credentials
```

## Bill Of Materials
To make the Lambdabooth you need:
- A DSLR camera, please refer to [this list](http://www.gphoto.org/proj/libgphoto2/support.php) to make sure your camera is supported. I've tested it with a Canon EOS 1100D
- A Raspberry Pi (more powerful it is and faster will be the elaboration)
- A cable to connect your camera to USB (please refer to your camera's manual)
- A micro USB Power Supply for Raspberry Pi
- A big momentary push button to take the photo such as [this one](https://it.aliexpress.com/store/product/16mm-BIG-head-Plastic-Emergency-Stop-switch-1NO1NC-LA16-11ZS-A/2030101_32755091219.html?spm=a2g0y.12010108.1000016.1.34c85ab5uKJrBb&isOrigTitle=true)
- A momentary button to switch off Raspberry Pi
- A 7 segment display for the countdown such as [this one](https://www.aliexpress.com/item/Free-Shipping-1pcs-Common-Anode-1-Bit-Digital-Tube-7-segment-2-3-inch-Red-LED/32282721171.html?spm=a2g0s.8937460.0.0.6cae2e0ef7D98c)
- A well lit green screen such as [this one](https://www.amazon.com/LimoStudio-AGG1338-Studio-Backdrop-Included/dp/B00KQ23GGW/ref=sr_1_8?s=photo&ie=UTF8&qid=1532250306&sr=1-8&keywords=green+screen&dpID=41yE%252BXGppLL&preST=_SY300_QL70_&dpSrc=srch)
- Material for the LambdaBooth's box. You can use wood, plastic,...
- Electric cables for connections

## Dependencies
1. Python 3 and pip3: If you have a recent version of Raspbian installed on your Raspberry Pi, they should already be installed.
2. Gphoto2: It is necessary to control a DSLR camera using the Raspberry Pi. Installing it is as simple as: `sudo apt-get install gphoto2 libgphoto2*`.
3. Opencv3: It is necessary for chromakeying. The installation is pretty long (it could require 4 hours on a first gen Raspberry Pi). To install it I have followed [this guide](https://www.life2coding.com/install-opencv-3-4-0-python-3-raspberry-pi-3/) from step 1 to step 11. There is also a [bash script](https://github.com/pageauc/opencv3-setup) that can simplify all the process and automate it but I've not tested it.
4. Python-gphoto2: You need it to control your DSLR camera from Python. Install it with: `sudo pip install gphoto2`.
5. oauth2client, httplib2, requests: Used to upload photos on google photos. Install them with: `sudo pip3 install --upgrade oauth2client httplib2 requests`.

## Installation
1. Clone all the repository in your Raspberry Pi
2. Edit parameters in "LambdaBooth.py" according to your needs
3. Create a folder for original photos, a folder for backgrounds and a folder for edited photos paying attention to edit their paths in LambdaBooth.py
4. Make/seek backgrounds and overlays with the same dimensions of the original photo. The code tells you what is the right width and height
5. Add the possibility to shutdown the Raspberry Pi with the button following [this guide](https://github.com/raspberrypi/firmware/blob/master/boot/overlays/README#L619)
6. Make "LambdaBooth.py" autostart at boot adding it to crontab following [this guide](https://www.raspberrypi.org/forums/viewtopic.php?t=139774#p927101)
7. Connect the buttons according to your configuration and camera
8. Wire the display as shown [here]()
9. If you want to upload your photos to Google photos, the first time you have to follow [this guide](https://makezine.com/projects/raspberry-pi-photo-booth/) from paragraph 4 to first part of paragraph 7

## Result example
I've taken a pretty hard green screen photo from google images to test the Chromakey feature. The result is pretty good:

![Original Image](/images/front.jpg)
![Background](/images/background.jpg)
![Result Image](/images/front_mod.jpg)

Probably, editing parameters in chromakey function, you can achieve better results. Also edit them if you use a blue screen instead of a green one.

## Troubleshooting
- After dependencies installation, I noticed errors when trying to import opencv module in Python. This is caused by other dependencies missing. In my case they were libatlas, libqt4 and libqt4-test. I've installed them in this way: `sudo apt-get install libatlas-base-dev libqt4 libqt4-test`. If you notice other errors caused by dependencies missing, please use Google to find a way to install them.
- Running gphoto2, I kept having error 'Could not claim the USB device'. This was caused by two processes which keep camera busy. To fix it I've followed [this guide](https://askubuntu.com/questions/993876/gphoto2-could-not-claim-the-usb-device). The problem was that, after reboot, the services keep autorun and I had to kill them after every boot. To kill them forever I used `sudo chmod -x /usr/lib/gvfs/gvfs-gphoto2-volume-monitor` and `sudo chmod -x /usr/lib/gvfs/gvfsd-gphoto2`.
- For every problem related to opencv, gphoto2 or the other libraries used, please refer to their support page. In particular: [gphoto2](https://github.com/gphoto/gphoto2), [opencv](https://github.com/skvark/opencv-python) and [python-gphoto2](https://github.com/jim-easterbrook/python-gphoto2).

## TODO
- Video Demonstration
- LambdaBooth.py file
- Display wiring
