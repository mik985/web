from flask import Flask, render_template, request

global USE_GPIO
USE_GPIO = False

if USE_GPIO:
    import Jetson.GPIO as GPIO
    GPIO.setwarnings(False)
import time
import json
import os
import socket

if USE_GPIO:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(38, GPIO.OUT)
    GPIO.setup(29, GPIO.OUT)

script_running = False

if USE_GPIO:
    PATH_TO_PROJECT_ROOT = "/home/jetson/ManipulatorProject"
else:
    PATH_TO_PROJECT_ROOT = "/home/user/PycharmProjects/pythonProject"
PATH_TO_CONFIG = os.path.join(PATH_TO_PROJECT_ROOT, "robot_configuration/config.json")
PATH_TO_LOCK_TMP = os.path.join("/home/user/PycharmProjects/web/static/lock.tmp")
PATH_TO_COMMAND_JSON = "/home/user/PycharmProjects/pythonProject/command.json"

CAMERA_LIST = ["hicvision_vpn",
               "jetson_big",
               "jetson_small",
               "usb_camera",
               "rasp_sci",
               "not_use"]

# получение конфигурационных параметров робота
with open(PATH_TO_CONFIG) as f:
    robot_configuration = json.load(f)

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
    # RobotModel = check_tcp_model_robot(robot_configuration['robot_ip'], port=8888)
    RobotModel = True
    global script_running, PATH_TO_LOCK_TMP

    if os.path.exists(PATH_TO_LOCK_TMP):
        script_running = True
    else:
        script_running = False

    if request.method == 'POST':
        if request.form.get('command') == 'Start' and RobotModel:

            with open(PATH_TO_COMMAND_JSON, 'w') as f:
                json.dump(dict({'command': 'start'}), f, indent=4)

            if os.path.exists(PATH_TO_LOCK_TMP):
                script_running = True
                print("program is already running")
            else:
                with open(PATH_TO_LOCK_TMP, "w"):
                    pass
                script_running = True
                robot_configuration['option'] = int(request.form.get('option'))
                print(int(request.form.get('option')))
                with open(PATH_TO_CONFIG, "w") as f:
                    json.dump(robot_configuration, f)
                # if USE_GPIO:
                #     GPIO.output(29, GPIO.HIGH)
                #     time.sleep(0.2)
                #     GPIO.output(29, GPIO.LOW)
            return render_template("index.html", robot_configuration=robot_configuration, RobotModel=RobotModel,
                                   pr_running=script_running, pause=False)
        elif request.form.get('command') == 'Stop':

            with open(PATH_TO_COMMAND_JSON, 'w') as f:
                json.dump(dict({'command': 'stop'}), f, indent=4)

            if not os.path.exists(PATH_TO_LOCK_TMP):
                script_running = False
                print("program has already stopped")
            else:
                os.remove(PATH_TO_LOCK_TMP)
                script_running = False
                # if USE_GPIO:
                #     GPIO.output(38, GPIO.HIGH)
                #     time.sleep(0.2)
                #     GPIO.output(38, GPIO.LOW)
            return render_template("index.html", robot_configuration=robot_configuration, RobotModel=RobotModel,
                                   pr_running=script_running)
        elif request.form.get('command') == 'home' and RobotModel:
            # arm = Kawasaki_Robot(ip=robot_configuration["robot_ip"])
            # arm.set_speed(robot_configuration['free_speed'])
            # arm.move_break_point(*robot_configuration["home"])
            # arm.close_socket()
            # time.sleep(1)
            print('HOME')
        elif request.form.get('command') == 'check_disk' and RobotModel:
            # arm = Kawasaki_Robot(ip=robot_configuration["robot_ip"])
            # arm.set_speed(robot_configuration['free_speed'])
            # arm.move_break_point(*robot_configuration["check_disk_position"])
            # arm.close_socket()
            # time.sleep(1)
            print('check_disk')
        elif request.form.get('command') == 'Pause':
            with open(PATH_TO_COMMAND_JSON, 'w') as f:
                json.dump(dict({'command': 'pause'}), f, indent=4)
            print('Pause')
            pause = True
            return render_template("index.html", RobotModel=RobotModel,
                                   pr_running=script_running, pause=pause)
        elif request.form.get('command') == 'Continue':
            with open(PATH_TO_COMMAND_JSON, 'w') as f:
                json.dump(dict({'command': 'continue'}), f, indent=4)
            print('Continue')
            pause = False
            return render_template("index.html", RobotModel=RobotModel,
                                   pr_running=script_running, pause=pause)
    elif request.method == 'GET':
        print("refreshing")
        if os.path.exists(PATH_TO_LOCK_TMP):
            script_running = True
            print("program is already running")
        if not os.path.exists(PATH_TO_LOCK_TMP):
            script_running = False
            print("program has already stopped")
        # return render_template("index.html", robot_configuration=robot_configuration, RobotModel=RobotModel,
        #                        pr_running=script_running)
    return render_template("index.html", robot_configuration=robot_configuration, RobotModel=RobotModel,
                           pr_running=script_running, PATH_TO_LOCK_TMP=PATH_TO_LOCK_TMP)


@app.route('/debug', methods=['GET', 'POST'])
def dev():
    global PATH_TO_LOCK_TMP
    if request.method == 'POST':
        if request.form.get('command') == 'lockoff':
            if os.path.exists(PATH_TO_LOCK_TMP):
                os.remove(PATH_TO_LOCK_TMP)
    print(os.path.exists(PATH_TO_LOCK_TMP))
    return render_template("debug.html")

@app.route('/config', methods=['GET', 'POST'])
def config():
    global script_running
    if request.method == 'POST':
        if request.form.get('command') == 'Apply':
            for key in KEYS_LIST_OF_TYPE_INT:
                robot_configuration[key] = int(request.form.get(key))
            for key in KEYS_LIST_OF_TYPE_FLOAT:
                robot_configuration[key] = float(request.form.get(key))

            for i in range(len(robot_configuration["corners_robot"])):
                robot_configuration["corners_robot"][i][0] = float(request.form.get(f"y_edge_{i + 1}"))
                robot_configuration["corners_robot"][i][1] = float(request.form.get(f"x_edge_{i + 1}"))

            robot_configuration["camera_type"] = request.form.get("camera_type")
            print(request.form.get("camera_type"))

            robot_configuration["camera_position"] = request.form.get("camera_position")
            print(request.form.get("camera_position"))

            angles = ['O', 'A', 'T']
            for i in range(len(robot_configuration["orientation"])):
                robot_configuration["orientation"][i] = float(request.form.get(f"{angles[i]}"))

            coordinates_name_for_home = ['x_home', 'y_home', 'z_home', 'O_home', 'A_home', 'T_home']
            coordinates_name_for_photo = ['x_photo_position', 'y_photo_position', 'z_photo_position',
                                          'O_photo_position', 'A_photo_position', 'T_photo_position']
            coordinates_name_for_disk_check = ['x_disk_check', 'y_disk_check', 'z_disk_check', 'O_disk_check',
                                               'A_disk_check', 'T_disk_check']
            coordinates_name_for_inter_pos = ['x_inter', 'y_inter', 'z_inter', 'O_inter', 'A_inter', 'T_inter']
            for i in range(6):
                # set home position
                robot_configuration["home"][i] = float(request.form.get(f"{coordinates_name_for_home[i]}"))

                # set position for photo making
                robot_configuration["work_space_photo_position"][i] = float(
                    request.form.get(f"{coordinates_name_for_photo[i]}"))

                # set position for disk checking
                robot_configuration["check_disk_position"][i] = float(
                    request.form.get(f"{coordinates_name_for_disk_check[i]}"))

                # set intermediate position
                robot_configuration["intermediate_position"][i] = float(
                    request.form.get(f"{coordinates_name_for_inter_pos[i]}"))

            robot_configuration['robot_ip'] = request.form.get('robot_ip')
            robot_configuration['server_ip'] = request.form.get('server_ip')
            with open(PATH_TO_CONFIG, "w") as f:
                json.dump(robot_configuration, f)
            return render_template("config.html", robot_configuration=robot_configuration)
        elif request.form.get('command') == "Detect corners":
            print("CONFIGURE")
            return render_template("config.html", robot_configuration=robot_configuration, img_src="/static/Images/mask.jpeg")
    elif request.method == 'GET':
        pass
    return render_template("config.html", robot_configuration=robot_configuration, img_src="/static/Images/mask.jpeg", script_running=script_running)


def check_tcp_model_robot(ip, port=8888):
    tcpCliSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpCliSocket.settimeout(5)
    try:
        tcpCliSocket.connect((ip, port))
        recv_data = 0
        while not recv_data:
            recv_data = tcpCliSocket.recv(1024)
            if recv_data:
                recv_data = recv_data.decode('utf-8')
                # print(recv_data)
                tcpCliSocket.close()
                return recv_data
    except Exception:
        # print("No route to host")
        return


if __name__ == '__main__':
    app.run('192.168.40.130', port="9883")
