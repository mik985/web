import time
from flask import Flask, flash, request, redirect, url_for
import requests
import json
import io

# <div id="images">
#   <p><label>Detected corners:</label></p>
#   <p><img id="corners" src="/static/Images/mask.jpeg" width="100%"></p>
#   <p><label>Masks with all detected metal parts:</label></p>
#   <p><img id="mask" src="/static/Images/mask.jpeg" width="100%"></p>
#   <p><label>Generated trajectory:</label></p>
#   <p><img id="trajectory" src="/static/Images/trajectory.jpeg" width="100%"></p>
# </div

# global ls
# ls = []
# ls.append("<div id='images'> \n")

# writer(label='Detected corners', id='corners', src='/home/user/PycharmProjects/web/static/Images/mask.jpeg')

def writer(label, id, src):
    global ls
    ls.append(f"<p><label>{label}:</label></p> \n <p><img id='{id}' src='{src}' width='100%'></p> \n")
    ls_copy = ls.copy()
    # ls_copy.append("</div>")

    text = ls_copy[0]
    for i in range(1, len(ls_copy)):
        text += ls_copy[i]

    with open("/home/user/PycharmProjects/web/static/ajax_img_visualization.txt", "w") as f:
        f.write(text)



dictToSend = {"corners": "/static/Images/mask.jpeg"}
response = requests.post("http://192.168.40.130:9882/", json=dictToSend)
response = requests.get("http://192.168.40.130:9882/")


import psutil
import os
import time

with open("/home/jetson/ManipulatorProject/log.txt", "a") as f:
    f.write("check")

def verification():
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == "python3" and len(p.cmdline()) > 1 and "test.py" in p.cmdline()[1]:
            with open("/home/jetson/ManipulatorProject/log.txt", "a") as f:
                f.write("script is run")
            print("script is run")
            return False
    print("script is not run")
    with open("/home/jetson/ManipulatorProject/log.txt", "a") as f:
        f.write("script is not run")
    return True

if verification():
    os.system("python3 test.py")

