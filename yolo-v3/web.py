from flask import Flask, abort, request, jsonify, make_response
import json
import time

from model import yolov3
import tensorflow as tf
import numpy as np
import cv2
import os

from img_toHash import stringToHash, imgToHash
from utils.misc_utils import parse_anchors, read_class_names
from utils.nms_utils import gpu_nms
from utils.plot_utils import get_color_table, plot_one_box
import data_pro

from functools import wraps
from flask import make_response

app = Flask(__name__)

global sess
global arg


# 解决跨域问题
def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst

    return wrapper_fun


#图片识别接口
@app.route('/img/', methods=['GET'])
@allow_cross_domain
def get_task():
    if not request.args or 'img' not in request.args:
        return jsonify("{'err':'not found param: text'}")
    else:
        str = request.args['img']
        print(str)
        img = str.replace('http://localhost:9000', 'E:\\uploads')
        print(img)
        arg['input_image'] = img
        imgpath, img_hash = img_process()
        # return jsonify("{'result':'"+r+"'}")
        # return r
        imgpath = imgpath.replace('E:\\uploads', 'http://localhost:9000')
        result = {'result': imgpath,
                  'img_hash': img_hash,
                  'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
        return result


#统计数据接口
@app.route('/statistic_clear', methods=['GET'])
@allow_cross_domain
def statistic_clear():
    os.remove("E:\\uploads\\upload\\plt.png")
    result = {'messege': "清楚旧数据成功",
              'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    return result

#统计数据接口
@app.route('/statistic', methods=['GET'])
@allow_cross_domain
def statistic():
    #取出MAP
    dirname = "D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\checkpoint"
    filelist = os.listdir(dirname)
    file = filelist[0]
    oldpath = os.path.join(dirname, file)
    filename = os.path.splitext(file)[0]  # 文件名
    MAP = filename.split('_')[7]

    #统计图图片总数
    dirname = "D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\Annotations"
    filelist = os.listdir(dirname)
    sum = len(filelist)

    #统计每周新增数据数
    week_sum = 0
    filelist = os.listdir(dirname)
    for file in filelist:
        oldpath = os.path.join(dirname, file)
        filename = dirname + '/' + os.path.splitext(file)[0] + os.path.splitext(file)[1]  # 文件名
        file_time = os.path.getmtime(filename)
        now_time = time.time()
        if abs(now_time - file_time) < 604800:
            ++week_sum

    messege, img_path = data_pro.statistic()
    img_path =  img_path.replace('E:\\uploads', 'http://localhost:9000')
    result = {'messege': messege,
              'img_path': img_path,
              'sum': sum,
              'week_sum': week_sum,
              'MAP': MAP,
              'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    return result

def img_process():
    # 识别图像模块，计算图像hash值
    print(arg['input_image'])
    img_ori = cv2.imread(arg['input_image'])
    height_ori, width_ori = img_ori.shape[:2]  # 取彩色图的高宽
    img = cv2.resize(img_ori, tuple(arg['new_size']))  # 重定义图片大小
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.asarray(img, np.float32)  # 转换为numpy数组
    img = img[np.newaxis, :] / 255.  # 增加一个维度并除以255
    # go
    boxes_, scores_, labels_ = sess.run([boxes, scores, labels], feed_dict={input_data: img})

    # rescale the coordinates to the original image
    boxes_[:, 0] *= (width_ori / float(arg['new_size'][0]))
    boxes_[:, 2] *= (width_ori / float(arg['new_size'][0]))
    boxes_[:, 1] *= (height_ori / float(arg['new_size'][1]))
    boxes_[:, 3] *= (height_ori / float(arg['new_size'][1]))

    print("box coords:")
    print(boxes_)
    print('*' * 30)
    print("scores:")
    print(scores_)
    print('*' * 30)
    print("labels:")
    print(labels_)

    # plot box on image
    img_hash = {}
    for i in range(len(boxes_)):
        x0, y0, x1, y1 = boxes_[i]
        img_h = img_ori[int(y0):int(y1), int(x0):int(x1)]
        img_hash[arg['classes'][labels_[i]] + "-" + str(i)] = imgToHash(img_h)
        plot_one_box(img_ori, [x0, y0, x1, y1], label=arg['classes'][labels_[i]] + ',' + str(int(scores_[i]*100)) + '%',
                     color=color_table[labels_[i]])
    imgpath = arg['input_image']
    print(imgpath)
    # cv2.imshow('Detection result', img_ori)
    cv2.imwrite(imgpath, img_ori)
    # cv2.waitKey(0)
    return imgpath, img_hash


if __name__ == "__main__":
    # # 初始化参数
    arg = {'input_image': "",
           'anchor_path': 'D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data/anchors.txt',
           'new_size': [416, 416],
           'letterbox_resize': True,
           'class_name_path': 'D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\coco.names',
           'restore_path': 'D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\checkpoint'
                           '/best_model_Epoch_100_step_37672_mAP_0.7730_loss_7.2996_lr_1e-05',
           'save_video': True,
           'path': 'E:\\uploads\\upload\\img_process',
           'anchors': '',
           'classes': '',
           'num_class': ''
           }
    arg['anchors'] = parse_anchors(arg['anchor_path'])
    arg['classes'] = read_class_names(arg['class_name_path'])
    arg['num_class'] = len(arg['classes'])
    
    color_table = get_color_table(arg['num_class'])
   
    gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.333)
    config = tf.compat.v1.ConfigProto(gpu_options=gpu_options)
    config.gpu_options.allow_growth = True
    
    # 初始化tensorflow，打开session
    sess = tf.Session(config=config)
    input_data = tf.compat.v1.placeholder(tf.float32, [1, arg['new_size'][1], arg['new_size'][0], 3],
                                          name='input_data')
    yolo_model = yolov3(arg['num_class'], arg['anchors'])
    with tf.compat.v1.variable_scope('yolov3'):
        pred_feature_maps = yolo_model.forward(input_data, False)  # 取出头
    pred_boxes, pred_confs, pred_probs = yolo_model.predict(pred_feature_maps)  # 预测
    
    pred_scores = pred_confs * pred_probs
    
    # 过滤box，只选其一
    boxes, scores, labels = gpu_nms(pred_boxes, pred_scores, arg['num_class'], max_boxes=200,
                                     score_thresh=0.3, nms_thresh=0.45)
    
    saver = tf.compat.v1.train.Saver()
    saver.restore(sess, arg['restore_path'])

    # 将host设置为0.0.0.0，则外网用户也可以访问到这个服务
    app.run(host="0.0.0.0", port=5003, debug=True)
