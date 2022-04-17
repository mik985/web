from flask import Flask, render_template, request
import cv2
import os
import glob
import numpy as np


def insert_segment_in_image(img: np.ndarray, contour) -> np.ndarray:
    frame1 = np.zeros(img.shape[:-1], dtype=np.uint8)
    cv2.drawContours(frame1, contour, 0, (1, 1, 1), -1)
    frame2 = np.ones_like(frame1)
    frame2[frame1 == 1] = 0
    frames_list = [frame1, frame2]
    segment = np.zeros_like(img)
    for frame in frames_list:
        r = img[:, :, 0] * frame
        g = img[:, :, 1] * frame
        b = img[:, :, 2] * frame
        segment += np.dstack((r, g, b))
    return segment


app = Flask(__name__)
PARAMS = dict()
PARAMS['image_segments'] = dict()
PARAMS["cancelled_masks_list"] = []
PARAMS["cam_view_point_number"] = 0
list_of_view_points = [i for i in os.listdir('static/Images') if 'cam_view_point' in i]
directory_name = list_of_view_points[PARAMS["cam_view_point_number"]]
PARAMS['org_image_path'] = f"static/Images/{directory_name}/image_with_masks.jpeg"
PARAMS['img_original'] = cv2.imread(PARAMS['org_image_path'])

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if request.form.get('command') == 'next':
            PARAMS['img_original'] = cv2.imread(PARAMS['org_image_path'])
            PARAMS["cam_view_point_number"] += 1
            if PARAMS["cam_view_point_number"] >= len(list_of_view_points):
                PARAMS["cam_view_point_number"] = 0
            PARAMS['image_segments'] = dict()
            PARAMS["cancelled_masks_list"] = []

    directory_name = list_of_view_points[PARAMS["cam_view_point_number"]]
    PARAMS['org_image_path'] = f"static/Images/{directory_name}/image_with_masks.jpeg"

    masks_path_list = glob.glob(f'static/Images/{directory_name}/*.png')
    print(masks_path_list)
    contours_list = []
    for idx, path_to_mask in enumerate(masks_path_list):
        _, frame = cv2.threshold(cv2.cvtColor(cv2.imread(path_to_mask), cv2.COLOR_RGB2GRAY), 127, 255, 0)
        contours, _ = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        PARAMS['image_segments'][idx] = (','.join(str(val[0][0]) + ',' + str(val[0][1]) for val in contours[0]))
        contours_list.append(contours)

    target_idx = int(request.args.get('idx', -1))

    if target_idx >= 0:
        if target_idx in PARAMS["cancelled_masks_list"]:
            print(f'restore part {target_idx}')
            frame = insert_segment_in_image(PARAMS['img_original'], contours_list[target_idx])
            PARAMS["cancelled_masks_list"].remove(target_idx)
        else:
            print(f'remove part {target_idx}')
            frame = cv2.imread(PARAMS["org_image_path"])
            cv2.drawContours(frame, contours_list[target_idx], 0, (128, 128, 128), -1)
            PARAMS["cancelled_masks_list"].append(target_idx)
        print(PARAMS["org_image_path"])
        cv2.imwrite(f'/home/user/PycharmProjects/web/static/Images/{directory_name}/image_with_masks.jpeg', frame)

    return render_template("main.html", PARAMS=PARAMS)


if __name__ == '__main__':
    app.run('192.168.40.130', port="9999")