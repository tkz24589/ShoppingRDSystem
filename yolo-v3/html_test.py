#!/usr/bin/env python
from __future__ import division, print_function
from flask import Flask, render_template, Response
import cv2 as cv

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def gen():
    print("start")
    camera = cv.VideoCapture(0)
    while True:
        fps, img_ori = camera.read()
        if not fps:
            break
        _, frame = cv.imencode('.jpg', img_ori)
        frame = frame.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    print("yahu1")
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

