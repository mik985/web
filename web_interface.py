import sys

sys.path.extend(['/home/jetson/.local/lib/python3.6/site-packages'])

from flask import Flask, render_template, request
import socket
import time
from math import ceil
import json
import os
import socket
import cv2
import numpy as np
# from main_grinding import photo_correction, write_box


global USE_GPIO, robot_configuration
# USE_GPIO = True
#
# if USE_GPIO:
#     import Jetson.GPIO as GPIO
#     GPIO.setwarnings(False)
#     GPIO.setmode(GPIO.BOARD)
#
# if USE_GPIO:
#     # from RobotTool import Kawasaki_Robot
#     pass
#
# if USE_GPIO:
#     # for buttons
#     GPIO.setup(38, GPIO.OUT)
#     GPIO.setup(29, GPIO.OUT)
#
#     # for leds
#     leds_pin = 15
#     GPIO.setup(leds_pin, GPIO.OUT)
#     GPIO.output(leds_pin, GPIO.HIGH)

    
def make_photo(camera_type) -> np.ndarray:
    """
    Create connection and make photo in RGB.
    """
    if camera_type == "hicvision_vpn":
        camera_port = "rtsp://admin:QsE221eM@192.168.1.150:554"
    elif camera_type in ("jetson_big","jetson_small"):
        if camera_type == "jetson_big":
            dispW = 4056
            dispH = 3040
        else:
            dispW = 2592
            dispH = 1944
        flip = 2
        fps = 15
        camera_port = 'nvarguscamerasrc !  video/x-raw(memory:NVMM), width=' + str(dispW) + \
                      ', height=' + str(dispH) + ', format=NV12,' \
                      ' framerate=' + str(fps) + '/1 ! nvvidconv flip-method=' + str(flip) + \
                      ' ! video/x-raw, width=' + str(dispW) + ', height=' + str(dispH) + \
                      ', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
    elif camera_type in ("usb_camera","rasp_sci"):
        camera_port = 0
        
    camera = cv2.VideoCapture(camera_port)
    if not camera.isOpened():
        print("Camera is not connected")
    ret, frame = camera.read()
    camera.release()
    if not ret:
        print("Photo is empty")
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    
def find_led(img_w_led, img_wo_led):
    """
    Order of detected corners should be [top-left, top-right, bottom-right, bottom-left].
    """
    diff_ = (img_w_led.astype(int)-img_wo_led.astype(int))
    diff_[diff_ < 0] = 0
    diff_ = diff_.mean(axis=2)
    diff_ = diff_ / diff_.max() * 255
    diff_ = diff_.astype(np.uint8)
    h, w = diff_.shape[:2]
    h, w = int(h/2), int(w/2)
    d = np.zeros((2*h, 2*w))
    c = 0
    dots = {}
    for i in ((0, h), (h, 2*h)):
        for j in ((0, w), (w, 2*w)):
            diff = diff_[i[0]:i[1],j[0]:j[1]]
            diff[diff < np.quantile(diff, 0.999)] = 0
            diff[diff > 0] = 255

            quarter = diff.copy()

            diff = cv2.blur(diff,(5,5))
            diff[diff < 255] = 0
            xs, ys = np.where(diff)
            dots[c] = [ceil(ys.mean()+j[0]), ceil(xs.mean()+i[0])]
            c += 1
    corners_camera = [x for x in dots.values()]
    corners_camera[-1], corners_camera[-2] = corners_camera[-2], corners_camera[-1]
    return corners_camera
    
script_running = False
USE_CAMERA = False
PATH_TO_PROJECT_ROOT = os.getcwd()
PATH_TO_CONFIG = os.path.join(PATH_TO_PROJECT_ROOT, "robot_configuration/config.json")
PATH_TO_LOCK_TMP = os.path.join(PATH_TO_PROJECT_ROOT, "lock.tmp")

with open(PATH_TO_CONFIG) as f:
    robot_configuration = json.load(f)
        
img_original = cv2.imread(os.path.join(PATH_TO_PROJECT_ROOT, "img_original.jpeg"))
    
# if robot_configuration["camera_type"] in ("hicvision_vpn", "not_use"):
#     img_original = photo_correction(img_original)

# write_box(img_original, np.array(robot_configuration['corners_camera'])).save(os.path.join(PATH_TO_PROJECT_ROOT, "static/Images/img_original.jpeg"))

KEYS_LIST_OF_TYPE_INT = ['brush_for_part_edge_area',
                         'brush_for_part_inner_area',
                         'ident_for_part_edge_area',
                         'ident_for_part_inner_area',
                         'work_speed_edge_area',
                         'work_speed_inner_area',
                         'free_speed',
                         'turn_on_arm',
                         'turn_on_grinder',
                         'turn_on_magnetic_table',
                         'turn_on_pneumatic_controller'
                         ]

KEYS_LIST_OF_TYPE_FLOAT = ['height',
                           'working_height',
                           'threshold_scores_rcnn',
                           'distance',
                           'threshold_corr',
                           'threshold_rcnn']

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    global script_running, PATH_TO_LOCK_TMP, RobotModel, robot_configuration, PATH_TO_CONFIG
    
    RobotModel = True

    pause = False

    with open(PATH_TO_CONFIG) as f:
        robot_configuration = json.load(f)
    
    if os.path.exists(PATH_TO_LOCK_TMP):
        script_running = True
    else:
        script_running = False
        
    if request.method == 'POST':
        if request.form.get('command') == 'Start' and RobotModel:
            if script_running:
                
              #  with open(PATH_TO_LOCK_TMP, "w") as f:
                #    RobotModel = f.read()

                print("program is already running")
            else:
                
               # RobotModel = check_tcp_model_robot(robot_configuration['robot_ip'], port=8888)

              #  with open(PATH_TO_LOCK_TMP, "w") as f:
             #       f.write(RobotModel)

                script_running = True
 
                robot_configuration['option'] = int(request.form.get('option'))
                print(int(request.form.get('option')))
                with open(PATH_TO_CONFIG, "w") as f:
                    json.dump(robot_configuration, f)
                if USE_GPIO:
                    GPIO.output(29, GPIO.HIGH)
                    time.sleep(0.2)
                    GPIO.output(29, GPIO.LOW)
            return render_template("index.html", RobotModel=RobotModel,
                                   pr_running=script_running)
        elif request.form.get('command') == 'Stop':
            if not script_running:
                print("program has already stopped")
            else:
                os.remove(PATH_TO_LOCK_TMP)
                script_running = False
                if USE_GPIO:
                    GPIO.output(38, GPIO.HIGH)
                    time.sleep(0.2)
                    GPIO.output(38, GPIO.LOW)
            return render_template("index.html", RobotModel=RobotModel,
                                   pr_running=script_running)

        elif request.form.get('command') == 'home':
            # arm = Kawasaki_Robot(ip=robot_configuration["robot_ip"])
            # arm.set_speed(robot_configuration['free_speed'])
            # arm.move_break_point(*robot_configuration["home"])
            # arm.close_socket()
            # time.sleep(1)
            print('home')
        elif request.form.get('command') == 'check_disk':
            # arm = Kawasaki_Robot(ip=robot_configuration["robot_ip"])
            # arm.set_speed(robot_configuration['free_speed'])
            # arm.move_break_point(*robot_configuration["check_disk_position"])
            # arm.close_socket()
            # time.sleep(1)
            print('check_disk')
        elif request.form.get('command') == 'Pause':
            print('Pause')
            # pause = True
            return render_template("index.html", RobotModel=RobotModel,
                                   pr_running=script_running, pause=pause)
        elif request.form.get('command') == 'Continue':
            print('Continue')
            # pause = False
            return render_template("index.html", RobotModel=RobotModel,
                                   pr_running=script_running, pause=pause)
    elif request.method == 'GET':
        if not script_running:
           # RobotModel = check_tcp_model_robot(robot_configuration['robot_ip'], port=8888)
            pass
    pause = True
    return render_template("index.html", RobotModel=RobotModel,
                           pr_running=script_running, pause=pause)


@app.route('/config', methods=['GET', 'POST'])
def config():
    global img_original, robot_configuration, script_running
    if not script_running:
        with open(PATH_TO_CONFIG) as f:
            robot_configuration = json.load(f)
    if request.method == 'POST':
        if request.form.get('command') == 'Apply':
            for key in KEYS_LIST_OF_TYPE_INT:
                print(request.form.get(key), key)
                robot_configuration[key] = int(request.form.get(key))
            for key in KEYS_LIST_OF_TYPE_FLOAT:
                robot_configuration[key] = float(request.form.get(key))
            
            robot_configuration['server_ip'] = request.form.get('server_ip')
            
            robot_configuration["camera_type"] = request.form.get("camera_type")

            robot_configuration["camera_position"] = request.form.get("camera_position")
            
            for i in range(len(robot_configuration["corners_robot"])):
                robot_configuration["corners_robot"][i][0] = float(request.form.get(f"y_edge_{i + 1}"))
                robot_configuration["corners_robot"][i][1] = float(request.form.get(f"x_edge_{i + 1}"))

            angles = ['O', 'A', 'T']
            for i in range(len(robot_configuration["orientation"])):
                robot_configuration["orientation"][i] = float(request.form.get(f"{angles[i]}"))

            coordinates_name_for_home = ['x_home', 'y_home', 'z_home', 'O_home', 'A_home', 'T_home']
            coordinates_name_for_photo = ['x_photo_position', 'y_photo_position', 'z_photo_position', 'O_photo_position', 'A_photo_position', 'T_photo_position']
            coordinates_name_for_disk_check = ['x_disk_check', 'y_disk_check', 'z_disk_check', 'O_disk_check', 'A_disk_check', 'T_disk_check']
            coordinates_name_for_inter_pos = ['x_inter', 'y_inter', 'z_inter', 'O_inter', 'A_inter', 'T_inter']
            for i in range(6):
                # set home position
                robot_configuration["home"][i] = float(request.form.get(f"{coordinates_name_for_home[i]}"))
                
                # set position for photo making
                robot_configuration["work_space_photo_position"][i] = float(request.form.get(f"{coordinates_name_for_photo[i]}"))
                
                # set position for disk checking
                robot_configuration["check_disk_position"][i] = float(request.form.get(f"{coordinates_name_for_disk_check[i]}"))
                
                # set intermediate position
                robot_configuration["intermediate_position"][i] = float(request.form.get(f"{coordinates_name_for_inter_pos[i]}"))
                
            robot_configuration['robot_ip'] = request.form.get('robot_ip')
            with open(PATH_TO_CONFIG, "w") as f:
                json.dump(robot_configuration, f, indent=4)
            return render_template("config.html", robot_configuration=robot_configuration)
        elif request.form.get('command') == "Detect corners":
            print('Detect corners')
#             if USE_GPIO:
# #                 GPIO.output(leds_pin, GPIO.LOW)
#                 GPIO.output(leds_pin, GPIO.HIGH)
#                 img_wo_led = make_photo(robot_configuration["camera_type"])
# #                 GPIO.output(leds_pin, GPIO.HIGH)
#                 GPIO.output(leds_pin, GPIO.LOW)
#                 time.sleep(1)
#                 img_w_led = make_photo(robot_configuration["camera_type"])
# #                 GPIO.output(leds_pin, GPIO.LOW)
#                 GPIO.output(leds_pin, GPIO.HIGH)
#                 if robot_configuration["camera_type"] in ("hicvision_vpn", "not_use"):
#                     img_wo_led = photo_correction(img_wo_led)
#                     img_w_led = photo_correction(img_w_led)
#                 cv2.imwrite(os.path.join(PATH_TO_PROJECT_ROOT, "img_wo_led.jpeg"), img_wo_led)
#                 cv2.imwrite(os.path.join(PATH_TO_PROJECT_ROOT, "img_w_led.jpeg"), img_w_led)
#                 corners_camera = find_led(img_w_led, img_wo_led)
#                 robot_configuration['corners_camera'] = corners_camera
#                 with open(PATH_TO_CONFIG, "w") as f:
#                     json.dump(robot_configuration, f, indent=4)
#                 write_box(img_wo_led, np.array(corners_camera)).save(os.path.join(PATH_TO_PROJECT_ROOT, "static/Images/img_original.jpeg"))
    elif request.method == 'GET':
        pass
    return render_template("config.html", robot_configuration=robot_configuration, img_src="/static/Images/img_original.jpeg", script_running=script_running)


@app.route('/debug', methods=['GET', 'POST'])
def dev():
    global PATH_TO_LOCK_TMP
    if request.method == 'POST':
        if request.form.get('command') == 'lockoff' and os.path.exists(PATH_TO_LOCK_TMP):
            os.remove(PATH_TO_LOCK_TMP)
    return render_template("debug.html")


def check_tcp_model_robot(ip, port=8888):
    time.sleep(1)
    tcpCliSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpCliSocket.settimeout(5)
    try:
        tcpCliSocket.connect((ip, port))
        recv_data = 0
        while not recv_data:
            recv_data = tcpCliSocket.recv(1024)
            if recv_data:
                recv_data = recv_data.decode('utf-8')
                tcpCliSocket.close()
                return recv_data
    except Exception:
        tcpCliSocket.close()
        return


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_host = s.getsockname()[0]
    app.run(local_host, port="9882")

    
