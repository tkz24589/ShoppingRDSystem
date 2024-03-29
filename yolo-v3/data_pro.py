import os
import pandas
import shutil
import random

import cv2
import numpy as np
import xml.etree.ElementTree as ET

from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt

import datetime


# 这部分休要修改


class Data_preprocess(object):
    '''
    解析xml数据，统计个类别数目
    '''

    def __init__(self, data_path, path):
        self.data_path = data_path
        self.path = path
        self.image_size = 416
        self.batch_size = 32
        self.cell_size = 13
        self.classes = ["hat", "clothes", "skirt", "pant", "glasses", "package", "shoe"]
        self.num_classes = len(self.classes)
        self.box_per_cell = 5
        self.class_to_ind = dict(zip(self.classes, range(self.num_classes)))

        self.count = 0
        self.epoch = 1
        self.count_t = 0

        #统计数据
        self.map = {"hat": 0,
                    "clothes": 0,
                    "skirt": 0,
                    "pant": 0,
                    "glasses": 0,
                    "package": 0,
                    "shoe": 0
                    }

    def load_labels(self, model):
        if model == 'train':
            txtname = os.path.join(self.data_path, 'train.txt')
        if model == 'test':
            txtname = os.path.join(self.data_path, 'test.txt')

        if model == "val":
            txtname = os.path.join(self.data_path, 'val.txt')

        with open(txtname, 'r') as f:
            image_ind = [x.strip() for x in f.readlines()]  # 文件名去掉 .jpg

        my_index = 0
        for ind in image_ind:
            class_inds, x1s, y1s, x2s, y2s, img_width, img_height = self.load_data(ind)

            if len(class_inds) == 0:
                pass
            else:
                annotation_label = ""
                # box_x: label_index, x_min,y_min,x_max,y_max
                for label_i in range(len(class_inds)):
                    annotation_label += " " + str(class_inds[label_i])
                    annotation_label += " " + str(x1s[label_i])
                    annotation_label += " " + str(y1s[label_i])
                    annotation_label += " " + str(x2s[label_i])
                    annotation_label += " " + str(y2s[label_i])
                    # 统计各类别数目
                    self.map[self.classes[class_inds[label_i]]] += 1
                with open("./data/my_data/label/" + model + ".txt", "a") as f:
                    f.write(str(my_index) + " " + self.data_path + "/JPEGImages/" + ind + ".jpg" + " " + str(
                        img_width) + " " + str(img_height) + annotation_label + "\n")

                my_index += 1

            # print(my_index)
        #绘图
        x = np.arange(7)
        value = list(self.map.values())
        key = list(self.map.keys())

        plt.bar(x, value)
        plt.xticks(x, key)
        plt.savefig(self.path)
        plt.savefig('E:\\uploads\\upload\\' + 'plt.png')

    def load_data(self, index):
        label = np.zeros([self.cell_size, self.cell_size, self.box_per_cell, 5 + self.num_classes])
        filename = os.path.join(self.data_path, 'Annotations', index + '.xml')
        tree = ET.parse(filename)
        image_size = tree.find('size')
        image_width = int(float(image_size.find('width').text))
        image_height = int(float(image_size.find('height').text))
        # h_ratio = 1.0 * self.image_size / image_height
        # w_ratio = 1.0 * self.image_size / image_width

        objects = tree.findall('object')

        class_inds = []
        x1s = []
        y1s = []
        x2s = []
        y2s = []

        for obj in objects:
            box = obj.find('bndbox')
            x1 = int(float(box.find('xmin').text))
            y1 = int(float(box.find('ymin').text))
            x2 = int(float(box.find('xmax').text))
            y2 = int(float(box.find('ymax').text))
            # x1 = max(min((float(box.find('xmin').text)) * w_ratio, self.image_size), 0)
            # y1 = max(min((float(box.find('ymin').text)) * h_ratio, self.image_size), 0)
            # x2 = max(min((float(box.find('xmax').text)) * w_ratio, self.image_size), 0)
            # y2 = max(min((float(box.find('ymax').text)) * h_ratio, self.image_size), 0)
            if obj.find('name').text in self.classes:
                class_ind = self.class_to_ind[obj.find('name').text]
                # class_ind = self.class_to_ind[obj.find('name').text.lower().strip()]

                # boxes = [0.5 * (x1 + x2) / self.image_size, 0.5 * (y1 + y2) / self.image_size, np.sqrt((x2 - x1) / self.image_size), np.sqrt((y2 - y1) / self.image_size)]
                # cx = 1.0 * boxes[0] * self.cell_size
                # cy = 1.0 * boxes[1] * self.cell_size
                # xind = int(np.floor(cx))
                # yind = int(np.floor(cy))

                # label[yind, xind, :, 0] = 1
                # label[yind, xind, :, 1:5] = boxes
                # label[yind, xind, :, 5 + class_ind] = 1

                if x1 >= x2 or y1 >= y2:
                    pass
                else:
                    class_inds.append(class_ind)
                    x1s.append(x1)
                    y1s.append(y1)
                    x2s.append(x2)
                    y2s.append(y2)

        return class_inds, x1s, y1s, x2s, y2s, image_width, image_height


def data_split(img_path):
    '''
    数据分割
    '''

    files = os.listdir(img_path)

    test_part = random.sample(files, int(351 * 0.2))

    val_part = random.sample(test_part, int(int(351 * 0.2) * 0.5))

    val_index = 0
    test_index = 0
    train_index = 0
    for file in files:
        if file in val_part:

            with open("./data/my_data/val.txt", "a") as val_f:
                val_f.write(file[:-4] + "\n")

            val_index += 1

        elif file in test_part:
            with open("./data/my_data/test.txt", "a") as test_f:
                test_f.write(file[:-4] + "\n")

            test_index += 1

        else:
            with open("./data/my_data/train.txt", "a") as train_f:
                train_f.write(file[:-4] + "\n")

            train_index += 1

        # print(train_index, test_index, val_index)


def statistic():
    # 清空之前的文件
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\label\\test.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\label\\train.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\label\\val.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\\test.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\\train.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\\val.txt", 'r+') as file:
        file.truncate(0)

    # try:
    # 分割train, val, test
    img_path = "./data/my_data/JPEGImages"
    data_split(img_path)
    print("===========split data finish============")

    # 做YOLO V3需要的训练集,并统计数据
    base_path = os.getcwd()
    data_path = os.path.join(base_path, "data/my_data")  # 绝对路径

    path = 'E:\\uploads\\upload\\' + \
           str(datetime.datetime.now().year) + str(datetime.datetime.now().month) +\
           str(datetime.datetime.now().day) + str(datetime.datetime.now().hour) + \
           str(datetime.datetime.now().second) + str(datetime.datetime.now().minute) +\
           'plt.png'
    data_p = Data_preprocess(data_path, path)
    data_p.load_labels("train")
    data_p.load_labels("test")
    data_p.load_labels("val")
    print("==========data pro finish===========")
    return 'success', path
    # except:
    #     return 'something error', ''

if __name__ == "__main__":
    #清空之前的文件
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\label\\test.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\label\\train.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\label\\val.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\\test.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\\train.txt", 'r+') as file:
        file.truncate(0)
    with open("D:\ProgramData\YOLO-V3-Tensorflow-dev\YOLO-V3-Tensorflow-dev\data\my_data\\val.txt", 'r+') as file:
        file.truncate(0)

    # 分割train, val, test
    img_path = "./data/my_data/JPEGImages"
    data_split(img_path)
    print("===========split data finish============")

    # 做YOLO V3需要的训练集,并统计数据
    base_path = os.getcwd()
    data_path = os.path.join(base_path, "data/my_data")  # 绝对路径

    data_p = Data_preprocess(data_path, "")
    data_p.load_labels("train")
    data_p.load_labels("test")
    data_p.load_labels("val")
    print("==========data pro finish===========")
