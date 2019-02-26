
<p align="center">
  <img
    alt="Logo"
    src="https://github.com/leobel96/LambdaBooth/blob/master/images/logo.svg"
    width="500"
  />
</p>


LambdaBooth is an hardware and software modular and customizable photobooth that can make your parties even more funny.


## How it works
These are the LambdaBooth functions: 

1. A person pushes a button (BUTTON).
2. 5 seconds timer starts (COUNTDOWN).
3. After the 5 seconds a photo is taken using a supported DSLR camera connected to the Raspberry and saved in a folder chosen by the user (CAMERA).
4. The background of the photo is changed with a random background taken from a folder provided by the user using chromakey technique (CHROMAKEY).
5. An overlay image (frame, watermark, logo, ...) is put on the photo (OVERLAY).
6. The final photo is uploaded to a Google Photos album chosen by the user (GOOGLE_UPLOAD) and/or on a Facebook page album (FACEBOOK_UPLOAD). WARNING: Google and Facebook upload are intended for personal use only because in "configuration.yaml" file you have to insert also sensitive information.
7. The final photo is also printed (PRINTING).

The user can switch on/off every function of the seven provided without any issue from the "enable/disable features" menu in the file "LambdaBooth.py":

```python
## ENABLE/DISABLE FEATURES
BUTTON = 1  # use/don't use button
COUNTDOWN = 0  # use/don't use countdown
CAMERA = 1  # use/don't use camera
CHROMAKEY = 0  # use/don't use chromakey
OVERLAY = 1  # use/don't use overlay
GOOGLE_UPLOAD = 1  # use/don't use google photos upload
FACEBOOK_UPLOAD = 1  # use/don't use facebook upload
PRINTING = 0  # send/don't send the result to printer
```
and one can also configure every aspect from "configuration.yaml" file.


## Bill Of Materials
To make the **complete** version of Lambdabooth you need:

- A DSLR camera, please refer to [this list](http://www.gphoto.org/proj/libgphoto2/support.php) to make sure your camera is supported. I've tested it with a Canon EOS 1100D
- A Raspberry Pi (more powerful it is and faster will be the elaboration)
- A cable to connect your camera to USB (please refer to your camera's manual)
- A micro USB Power Supply for Raspberry Pi
- A big momentary push button to take the photo such as [this one](https://it.aliexpress.com/store/product/16mm-BIG-head-Plastic-Emergency-Stop-switch-1NO1NC-LA16-11ZS-A/2030101_32755091219.html?spm=a2g0y.12010108.1000016.1.34c85ab5uKJrBb&isOrigTitle=true)
- A momentary button to switch on/off Raspberry Pi
- A 7 segment display for the countdown such as [this one](https://www.aliexpress.com/item/Free-Shipping-1pcs-Common-Anode-1-Bit-Digital-Tube-7-segment-2-3-inch-Red-LED/32282721171.html?spm=a2g0s.8937460.0.0.6cae2e0ef7D98c)
- A well lit green screen such as [this one](https://www.amazon.com/LimoStudio-AGG1338-Studio-Backdrop-Included/dp/B00KQ23GGW/ref=sr_1_8?s=photo&ie=UTF8&qid=1532250306&sr=1-8&keywords=green+screen&dpID=41yE%252BXGppLL&preST=_SY300_QL70_&dpSrc=srch)
- Material for the LambdaBooth's box. You can use wood, plastic,...
- Electric cables for connections
Obviously you can decide to don't use many things (such as the display) and make your own photobooth.


## Dependencies
Every component needs its own dependecies to be satisfied. I've made a .sh file to install all the dependecies easily; you can run it with `curl -s https://github.com/leobel96/LambdaBooth/installation.sh | bash`. Alternatively here there is a list for every component:

1. Python 3 and pip3: If you have a recent version of Raspbian installed on your Raspberry Pi, they should already be installed.
2. PyYAML: It is necessary to read the configuration file. Install it with `sudo pip3 install pyyaml`
3. gphoto2 and python-gphoto2: They are necessary for CAMERA. Installing them is as simple as: `sudo apt-get install gphoto2 libgphoto2*` followed by `sudo pip3 install gphoto2`.
4. opencv3: It is necessary for CHROMAKEY and OVERLAY. I've compiled it myself, anyway this is a pretty hard and time consuming method (it requires many hours). Anyway you can also install it with `sudo pip3 install opencv-contrib-python`.
5. requests, flask, firefox: They are necessary for UPLOAD. Install them with: `sudo pip3 install --upgrade requests Flask` and `sudo apt install firefox-esr`.
6. CUPS, pycups: They are necessary for PRINTING. Install the first one following [this guide](https://www.howtogeek.com/169679/how-to-add-a-printer-to-your-raspberry-pi-or-other-linux-computer/) and the second one with `sudo apt-get install libcups2-dev --fix-missing` and `sudo pip3 install pycups`.


## Complete installation
1. Clone all the repository in your Raspberry Pi and install the dependencies indicated in the [previous chapter](#dependencies). IMPORTANT: You have to set Firefox as default browser to use UPLOAD because Chromium returns many errors.
2. Edit parameters in "LambdaBooth.py" according to your needs.
3. Create a folder for original photos, a folder for backgrounds and a folder for edited photos paying attention to edit their paths in `configuration.yaml` file.
4. Make/seek backgrounds and overlays(frames, logos, ...) with the same dimensions of the original photo (if you want to use CHROMAKEY or OVERLAY).
5. Add the possibility to shutdown and power on the Raspberry Pi with a button adding `dtoverlay=gpio-shutdown,gpio_pin=3` to the file "/boot/config.txt" and connecting the button between GPIO3 (BCM) and GND.
6. Make "LambdaBooth.py" autostart at boot adding it to crontab following [this guide](https://www.raspberrypi.org/forums/viewtopic.php?t=139774#p927101).
7. Connect the big fancy button you have bought to capture photo to one of the Rpi GPIO and edit the `configuration.yaml` file according to the pin you have chosen ([BCM numeration](https://pinout.xyz/#)).
8. Wire the 7 segment display as shown [in this guide](https://www.electronics-tutorials.ws/blog/7-segment-display-tutorial.html).
9. If you want to upload your photos to Google photos or a Facebook page, follow [Facebook API configuration](#facebook-api-configuration) and [Google API configuration](#google-api-configuration). For first time configuration you have to connect a monitor to raspberry to allow your Facebook and Google apps.
10. If you want to print your photos, first install CUPS following [this guide](https://www.howtogeek.com/169679/how-to-add-a-printer-to-your-raspberry-pi-or-other-linux-computer/), then change the value of "printer_name" in `configuration.yaml` according to your printer's "Queue Name" in CUPS server.
11. After the installation and after you have tested that everything works as expected, I suggest you to disable the raspberry pi's GUI following [these simple steps](http://ask.xmodulo.com/disable-desktop-gui-raspberry-pi.html) to reduce the GPU stress. 


## Facebook API configuration
1. Go to https://developers.facebook.com.
2. Click on Get Started.
3. Complete all the passages.
4. Now you should be on your facebook app page. Click on `Facebook Login` and add to `valid OAuth redirect URI`: `https://www.facebook.com/`
5. Click on "Settings" in the left column and "Base".
6. Copy-paste the `App ID` and `App secret` in the `configuration.yaml` file.
7. Now you can use your app to upload the images on a page YOU own. In particular find the `page_id` of your FB page following [this easy guide](https://www.labnol.org/internet/find-facebook-page-id-profile/6909/) and add it to `configuration.yaml` file.


## Google API configuration
1. Go to https://console.cloud.google.com/apis/library?pli=1
2. Click on `Select project` from the top and, then, `New project`.
3. Select the newly created project from the top.
4. Search for `Photos Library API`.
5. Enable it.
6. Go to `Credentials` menu from `APIs & Services` on the left.
7. `Create credentials`, `Oauth Client ID`
8. Click on `Configure consent screen`, `Add scope`, `Manually paste`, paste: `https://www.googleapis.com/auth/photoslibrary`, click on `ADD`, select a name for the app and, then `SAVE`.
9. Repeat passages 6 and 7.
10. Select `Application type` as `other` and `create`.
11. Now Copy-paste `client ID` and `client secret` in the `configuration.yaml` file.
12. The first time you run "LambdaBooth.py" you will be asked to give access to your APP to your photos. Give the access and the program will do the rest.


## Chromakey result example
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
