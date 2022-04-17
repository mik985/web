from flask import Flask, render_template, request
import os


app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    # with open('/home/user/PycharmProjects/web/static/js/id_list.json') as f:
    #     text = f.read()
    # img_src_list = request.get_json()
    # print(img_src_list)
    return render_template('test.html')


if __name__ == '__main__':
    app.run('192.168.40.130', port="9882")
