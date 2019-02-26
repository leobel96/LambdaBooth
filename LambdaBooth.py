'''
  _                    _         _       ____              _   _
 | |    __ _ _ __ ___ | |__   __| | __ _| __ )  ___   ___ | |_| |__
 | |   / _` | '_ ` _ \| '_ \ / _` |/ _` |  _ \ / _ \ / _ \| __| '_ \
 | |__| (_| | | | | | | |_) | (_| | (_| | |_) | (_) | (_) | |_| | | |
 |_____\__,_|_| |_| |_|_.__/ \__,_|\__,_|____/ \___/ \___/ \__|_| |_|


Please refer to the official repository on Github:
https://github.com/leobel96/LambdaBooth for information
on how to install and use it. Enjoy!

'''
import logging
import os
import random
import sys
import time
import yaml  # pip install pyyaml

# ENABLE/DISABLE FEATURES:
BUTTON = 0  # use/don't use button
CAMERA = 0  # use/don't use camera
CHROMAKEY = 1  # use/don't use chromakey
COUNTDOWN = 0  # use/don't use countdown
OVERLAY = 0  # use/don't use overlay
GOOGLE_UPLOAD = 1  # use/don't use google photos upload
FACEBOOK_UPLOAD = 1  # use/don't use facebook upload
PRINTING = 0  # send/don't send result to printer

if BUTTON or COUNTDOWN:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
if CAMERA:
    import gphoto2 as gp
if OVERLAY or CHROMAKEY:
    import cv2  # pip install opencv-contrib-python
if FACEBOOK_UPLOAD or GOOGLE_UPLOAD:
    import json
    import requests  # pipenv install requests
    import threading
    import webbrowser
    from flask import Flask, request  # pip install Flask
if PRINTING:
    import cups  # pip install pycups

num = {' ': (0, 0, 0, 0, 0, 0, 0),
       '0': (1, 1, 1, 1, 1, 1, 0),
       '1': (0, 1, 1, 0, 0, 0, 0),
       '2': (1, 1, 0, 1, 1, 0, 1),
       '3': (1, 1, 1, 1, 0, 0, 1),
       '4': (0, 1, 1, 0, 0, 1, 1),
       '5': (1, 0, 1, 1, 0, 1, 1),
       '6': (1, 0, 1, 1, 1, 1, 1),
       '7': (1, 1, 1, 0, 0, 0, 0),
       '8': (1, 1, 1, 1, 1, 1, 1),
       '9': (1, 1, 1, 1, 0, 1, 1)}

with open("configuration.yaml", 'r') as f:
    configuration = yaml.load(f)
button_GPIO = configuration["button"]["button_GPIO"]
segments_GPIO = configuration["countdown"]["segments_GPIO"].split(',')
camera_path = configuration["camera"]["camera_path"]
default_photo = configuration["image_manipulation"]["no_camera_photo"]
background_path = configuration["image_manipulation"]["background_path"]
out_path = configuration["image_manipulation"]["out_path"]
overlay_image = configuration["image_manipulation"]["overlay_image"]
g_album_name = configuration["google_upload"]["g_album_name"]
g_client_id = configuration["google_upload"]["g_client_id"]
g_client_secret = configuration["google_upload"]["g_client_secret"]
fb_app_id = configuration["facebook_upload"]["fb_app_id"]
fb_app_secret = configuration["facebook_upload"]["fb_app_secret"]
fb_page_id = configuration["facebook_upload"]["fb_page_id"]
fb_album_name = configuration["facebook_upload"]["fb_album_name"]
printer_name = configuration["printing"]["printer_name"]

logging.basicConfig(level=logging.INFO)
g_album_id = None
g_access_token = None
g_refresh_token = None
g_expiration = None
fb_user_token = None
fb_album_id = None
g_code = None
fb_code = None

# Button initialization
if BUTTON:
    GPIO.setup(button_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(button_GPIO, GPIO.FALLING)

# 7-segments initialization
if COUNTDOWN:
    for gpio in segments_GPIO:
        GPIO.setup(gpio, GPIO.OUT, initial=GPIO.LOW)

if GOOGLE_UPLOAD:
    g_event = threading.Event()
    app1 = Flask(__name__)
    g_server = threading.Thread(target=app1.run,
                                kwargs={"host": "127.0.0.1", "port": 5000,
                                        "debug": False, "threaded": True})

    @app1.route('/', methods=["POST", "GET"])
    def g_index():
        global g_code
        g_code = request.args.get('code')
        g_event.set()  # Wakes up google_initialization
        request.environ.get('werkzeug.server.shutdown')()  # Kills Flask server
        return("<h1>You can close the page now.</h1>")

if FACEBOOK_UPLOAD:
    fb_event = threading.Event()
    app2 = Flask(__name__)
    fb_server = threading.Thread(target=app2.run,
                                 kwargs={"host": "localhost", "port": 5001,
                                         "debug": False, "threaded": True})

    @app2.route('/', methods=["POST", "GET"])
    def fb_index():
        global fb_code
        fb_code = request.args.get('code')
        print(fb_code)
        fb_event.set()  # Wakes up facebook_initialization
        request.environ.get('werkzeug.server.shutdown')()  # Kills Flask server
        return("<h1>You can close the page now.</h1>")


def show_number(number):
    for loop in range(7):
        GPIO.output(segments_GPIO[loop], num[str(number)][loop])


def take_photo(save_folder):
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))
    logging.debug('Capturing image')
    file_path = gp.check_result(gp.gp_camera_capture(
      camera, gp.GP_CAPTURE_IMAGE))
    timestr = time.strftime("%Y%m%d_%H%M%S")
    target = os.path.join(save_folder, timestr + ".jpg")
    logging.debug('Copying image to {0}'.format(target))
    camera_file = gp.check_result(gp.gp_camera_file_get(
      camera, file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL))
    gp.check_result(gp.gp_file_save(camera_file, target))
    return target


def random_back(path):
    random_filename = random.choice([
      x for x in os.listdir(path)
      if os.path.isfile(os.path.join(path, x))
    ])
    return os.path.join(path, random_filename)


def image_manipulation(front_file, back_path, over_file, save_folder, method):
    img = cv2.imread(front_file)
    width = img.shape[0]  # To select the right background and overlay
    height = img.shape[1]
    if CHROMAKEY:
        back_file = random_back(back_path)
        back = cv2.imread(back_file)
        reds = img[:, :, 2]
        greens = img[:, :, 1]
        blues = img[:, :, 0]
        mask = ((reds < (greens - 20))
                & (blues < (greens - 20))
                & (greens > 35))
        try:
            img[mask] = back[mask]
        except IndexError:
            logging.error("Background dimensions should be {0}x{1}"
                          .format(width, height))
            sys.exit()
    if OVERLAY:
        over = cv2.imread(over_file, cv2.IMREAD_UNCHANGED)
        over_width = over.shape[0]
        over_height = over.shape[1]
        x_offset = 50
        y_offset = 50
        if over_width == width and over_height == height:  # It's a frame
            mask = (over[:, :, 3] != 0)  # Alpha pixels
            over = over[:, :, 0:3]  # Non-alpha pixels
            img[mask] = over[mask]
        elif (over_width < (width-x_offset) and
              over_height < (height-y_offset)):  # It's a logo
            if method == 1:
                mask = (over[:, :, 3] != 0)
                over = over[:, :, 0:3]
                img_r = img[x_offset:(x_offset+over_width),
                            y_offset:(y_offset+over_height), :]
                img_r[mask] = over[mask]
                img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), :] = img_r
            else: 
                # This is another method to do the same thing.
                # It is much slower but the final result
                # is better with big logos

                alpha = over[:, :, 3]
                img = img.astype(float)
                over = over.astype(float)
                alpha = alpha.astype(float)/255
                over[:, :, 0] = cv2.multiply(over[:, :, 0], alpha)
                over[:, :, 1] = cv2.multiply(over[:, :, 1], alpha)
                over[:, :, 2] = cv2.multiply(over[:, :, 2], alpha)
                img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 0] = cv2.multiply(img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 0], 1-alpha)
                img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 1] = cv2.multiply(img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 1], 1-alpha)
                img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 2] = cv2.multiply(img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 2], 1-alpha)
                img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 0] = cv2.add(img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 0], over[:, :, 0])
                img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 1] = cv2.add(img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 1], over[:, :, 1])
                img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 2] = cv2.add(img[x_offset:(x_offset+over_width),
                    y_offset:(y_offset+over_height), 2], over[:, :, 2])
        else:
            logging.error("The overlay is neither a logo nor a frame. " +
                          "Make it as big as the image to use it " +
                          "as a frame or make it smaller than " +
                          "image - offset to use it as a logo.")
            sys.exit()
    basename = os.path.basename(front_file)
    basename = os.path.join(save_folder, basename)
    cv2.imwrite(basename, img)
    return basename


def google_refresh_token():
    global g_access_token
    global g_refresh_token
    global g_expiration
    url = ("https://www.googleapis.com/oauth2/v4/token?"
           "refresh_token={0}&"
           "client_secret={1}&"
           "client_id={2}&"
           "grant_type=refresh_token"
           .format(g_refresh_token, g_client_secret, g_client_id))
    resp = requests.post(url)
    if resp.status_code != 200:
        logging.debug('Error in token refresh')
        return 0
    g_access_token = resp.json()["access_token"]
    g_expiration = int(time.time())+int(resp.json()["expires_in"])
    dictionary = {"access_token": g_access_token,
                  "refresh_token": g_refresh_token,
                  "expiration": g_expiration}
    with open('google.json', 'w+') as f:
        json.dump(dictionary, f, ensure_ascii=False)


def google_initialization():
    global g_access_token
    global g_refresh_token
    global g_expiration
    global g_code
    if os.path.isfile("google.json"):
        with open("google.json", "r") as f:
            content = f.read()
            g_access_token = json.loads(content)["access_token"]
            g_refresh_token = json.loads(content)["refresh_token"]
            g_expiration = json.loads(content)["expiration"]
            if (g_expiration - int(time.time())) < 300:
                google_refresh_token()
    else:
        redirect_uri = "http://127.0.0.1:5000/"
        url = ("https://accounts.google.com/o/oauth2/v2/auth?"
               "scope=https://www.googleapis.com/auth/photoslibrary&"
               "redirect_uri={0}&"
               "response_type=code&"
               "client_id={1}".format(redirect_uri, g_client_id))
        webbrowser.open(url)
        g_server.run()
        g_event.wait()  # Waits for Flask killing
        url = ("https://www.googleapis.com/oauth2/v4/token?"
               "code={0}&"
               "redirect_uri={1}&"
               "client_secret={2}&"
               "client_id={3}&"
               "grant_type=authorization_code"
               .format(g_code, redirect_uri, g_client_secret, g_client_id))
        resp = requests.post(url)
        if resp.status_code != 200:
            logging.debug('Error in google token request')
            return 0
        g_access_token = resp.json()["access_token"]
        g_refresh_token = resp.json()["refresh_token"]
        g_expiration = int(time.time())+int(resp.json()["expires_in"])
        dictionary = {"access_token": g_access_token,
                      "refresh_token": g_refresh_token,
                      "expiration": g_expiration}
        with open('google.json', 'w+') as f:
            json.dump(dictionary, f, ensure_ascii=False)


def gphotos_upload(filename, g_album_name):
    global g_access_token
    global g_refresh_token
    global g_expiration
    global g_album_id
    global g_code
    start = time.time()
    if (g_access_token is None or g_refresh_token is None or
    g_expiration is None):
        google_initialization()
    if (g_expiration - int(time.time())) < 300:
        google_refresh_token()
    if g_album_id is None:
        url = 'https://photoslibrary.googleapis.com/v1/albums'
        headers = {"Content-type": "application/json",
                   "Authorization": "Bearer {0}".format(g_access_token)}
        body = {"album": {"title": g_album_name}}
        body = json.dumps(body)
        resp = requests.post(url, headers=headers, data=body)
        if resp.status_code != 200:
            logging.error('Error in google album creation')
            return 0
        g_album_id = resp.json()["id"]
    url = 'https://photoslibrary.googleapis.com/v1/uploads'
    headers = {"Content-type": "application/octet-stream",
               "Authorization": "Bearer {0}".format(g_access_token),
               "X-Goog-Upload-Protocol": "raw"}
    files = open(filename, 'rb').read()
    resp = requests.post(url, headers=headers, data=files)
    if resp.status_code != 200:
        logging.error('Error in google file upload')
        return 0
    url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
    headers = {"Content-type": "application/json",
               "Authorization": "Bearer {0}".format(g_access_token)}
    body = {"albumId": g_album_id,
            "newMediaItems": [{"description": "LambdaBooth",
                              "simpleMediaItem": {"uploadToken": resp.text}}]}
    body = json.dumps(body)
    try:
        resp = requests.post(url, headers=headers, data=body)
    except requests.exceptions.ConnectionError:
        logging.error('Connection Refused')
    if resp.status_code != 200:
        logging.error('Error in google file upload')
        return 0
    logging.info('Google upload completed in {0} s'
                 .format(time.time() - start))


def facebook_initialization():
    global fb_user_token
    global fb_code
    if os.path.isfile("facebook.json"):
        with open("facebook.json", "r") as f:
            content = f.read()
            fb_user_token = json.loads(content)["user_token"]
    else:
        redirect_uri = "http://localhost:5001/"
        scopes = "publish_pages,manage_pages"
        url = ("https://www.facebook.com/v3.2/dialog/oauth?"
               "client_id={0}&"
               "redirect_uri={1}&"
               "response_type=code&"
               "scope{2}".format(fb_app_id, redirect_uri, scopes))
        webbrowser.open(url)
        fb_server.run()
        fb_event.wait()  # Waits for Flask killing
        resp = requests.get("https://graph.facebook.com/v3.2/oauth/"
                            "access_token?client_id={0}&"
                            "redirect_uri={1}&"
                            "client_secret={2}&code={3}"
                            .format(fb_app_id, redirect_uri,
                                    fb_app_secret, fb_code))
        fb_user_token = resp.json()["access_token"]
        if resp.status_code != 200:
            logging.error('Error in facebook user token request')
            return 0
        dictionary = {"user_token": fb_user_token}
        with open('facebook.json', 'w+') as f:
            json.dump(dictionary, f, ensure_ascii=False)


def fb_upload(filename, fb_album_name):
    global fb_album_id
    start = time.time()
    if fb_user_token is None:
        facebook_initialization()
    redirect_uri = "https://www.facebook.com/"
    resp = requests.get("https://graph.facebook.com/{0}?fields=access_token&"
                        "access_token={1}".format(fb_page_id, fb_user_token))
    if resp.status_code != 200:
        logging.error('Error in facebook page token request')
        return 0
    fb_page_token = resp.json()["access_token"]
    if fb_album_id is None:
        resp = requests.post("https://graph.facebook.com/{0}/albums?"
                             "name={1}&access_token={2}"
                             .format(fb_page_id, fb_album_name, fb_page_token))
        fb_album_id = resp.json()["id"]
    files = {'file': open(filename, 'rb')}
    resp = requests.post("https://graph.facebook.com/{0}/photos?"
                         "access_token={1}"
                         .format(fb_album_id, fb_page_token), files=files)
    if resp.status_code != 200:
        logging.error('Error in facebook photo upload')
        return 0
    logging.info('Facebook upload completed in {0} s'
                 .format(time.time() - start))


def send_to_printer(filename, printername):
    conn = cups.Connection()
    conn.printFile(printer, filename, filename, {})
    logging.debug('Printing')
    while(bool(conn.getJobs(which_jobs='not-completed'))):
        time.sleep(1)  # Wait for completion


def main():
    if COUNTDOWN:
        time.sleep(1)
        show_number(4)
        time.sleep(1)
        show_number(3)
        time.sleep(1)
        show_number(2)
        time.sleep(1)
        show_number(1)
        time.sleep(1)

    start_time = time.time()

    if CAMERA:
        front_image = take_photo(camera_path)
        logging.debug("take_photo time = {0} s"
                      .format(time.time() - start_time))
    else:
        front_image = default_photo

    if CHROMAKEY or OVERLAY:
        mid_time = time.time()
        front_image = image_manipulation(front_image, background_path,
                                         overlay_image, out_path, 1)
        logging.debug("image_manipulation time = {0} s"
                      .format(time.time() - mid_time))

    if GOOGLE_UPLOAD:
        threading.Thread(target=gphotos_upload,
                         args=(front_image, g_album_name)).start()

    if FACEBOOK_UPLOAD:
        threading.Thread(target=fb_upload,
                         args=(front_image, fb_album_name)).start()

    if PRINTING:
        mid_time = time.time()
        send_to_printer(front_image, printer_name)
        logging.debug("printing time = {0} s"
                      .format(time.time() - mid_time))

    logging.info("Main thread completed successfully in {0} s"
                 .format(time.time() - start_time))


if BUTTON:
    logging.info("Waiting for button pression")
    if COUNTDOWN:
        show_number(5)
    while True:
        if GPIO.event_detected(button_GPIO):
            GPIO.remove_event_detect(button_GPIO)
            main()
            GPIO.add_event_detect(button_GPIO, GPIO.FALLING)
else:
    if COUNTDOWN:
        show_number(5)
    main()
