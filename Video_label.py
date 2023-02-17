from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import cv2
import os
import os.path as osp
import imutils
import numpy as np
import pandas as pd

def resize_img(img, size, padColor=0):
    h, w = img.shape[:2]
    sh, sw = size
    # interpolation method
    if h > sh or w > sw: # shrinking image
        interp = cv2.INTER_AREA
    else: # stretching image
        interp = cv2.INTER_CUBIC
    # aspect ratio of image
    aspect = w/h
    # compute scaling and pad sizing
    if aspect > 1: # horizontal image
        new_w = sw
        new_h = np.round(new_w/aspect).astype(int)
        pad_vert = (sh-new_h)/2
        pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
        pad_left, pad_right = 0, 0
    elif aspect < 1: # vertical image
        new_h = sh
        new_w = np.round(new_h*aspect).astype(int)
        pad_horz = (sw-new_w)/2
        pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
        pad_top, pad_bot = 0, 0
    else: # square image
        new_h, new_w = sh, sw
        pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0
    # set pad color
    if len(img.shape) == 3 and not isinstance(padColor, (list, tuple, np.ndarray)): # color image but only one color provided
        padColor = [padColor]*3
    # scale and pad
    scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interp)
    scaled_img = cv2.copyMakeBorder(scaled_img, pad_top, pad_bot, pad_left, pad_right, borderType=cv2.BORDER_CONSTANT, value=padColor)
    return scaled_img


class My_GUI(QMainWindow):
    def __init__(self):
        super(My_GUI, self).__init__()
        uic.loadUi('video_label1/video_label.ui', self)

        #--------------------------------------------------------------------------------------
        self.label_file = 'video_label1/Video_label.csv'
        # --------------------------------------------------------------------------------------
        self.video_path = ''

        self.frame_pos = 0
        self.A_frame = 0
        self.I1_Frame = 0
        self.I2_Frame = 0
        self.T_Frame = 0
        self.F_Frame = 0

        self.load_video_btn.clicked.connect(self.load_video)
        self.frame_no_slider.valueChanged.connect(self.frame_change)
        self.a_btn.clicked.connect(self.a_frame_set)
        self.t_btn.clicked.connect(self.t_frame_set)
        self.i1_btn.clicked.connect(self.i1_frame_set)
        self.i2_btn.clicked.connect(self.i2_frame_set)
        self.f_btn.clicked.connect(self.f_frame_set)
        self.save_btn.clicked.connect(self.save_data)


    def load_video(self):
        self.video_path = QtWidgets.QFileDialog.getOpenFileName(self,'Open video file', filter='Video files (*.mp4 *.mkv, *.avi)')[0]
        if len(self.video_path) == 0:
            return
        self.video = cv2.VideoCapture(self.video_path)
        self.total_frame = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        _, self.curr_frame = self.video.read()
        self.frame_no_slider.setRange(0, int(self.total_frame) - 1)
        self.frame_no_slider.setValue(0)
        self.image_set(self.curr_frame)
        self.A_frame = 0
        self.I1_frame = 0
        self.I2_frame = 0
        self.T_frame = 0
        self.F_frame = 0

        self.a_txt.setText(str(self.A_frame))
        self.t_txt.setText(str(self.T_frame))
        self.i1_txt.setText(str(self.I1_frame))
        self.i2_txt.setText(str(self.I2_frame))
        self.f_txt.setText(str(self.F_frame))

    def frame_change(self, value):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, value)
        _, frame = self.video.read()
        self.image_set(frame)
        self.frame_no_txt.setText(str(value))


    def image_set(self, image):
        # image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = resize_img(image, (900, 700))
        image_Qt = QImage(image, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(image_Qt))

    def a_frame_set(self):
        self.A_frame = self.frame_no_slider.value()
        self.a_txt.setText(str(self.A_frame))

    def t_frame_set(self):
        self.T_frame = self.frame_no_slider.value()
        self.t_txt.setText(str(self.T_frame))

    def i1_frame_set(self):
        self.I1_frame = self.frame_no_slider.value()
        self.i1_txt.setText(str(self.I1_frame))

    def i2_frame_set(self):
        self.I2_frame = self.frame_no_slider.value()
        self.i2_txt.setText(str(self.I2_frame))


    def f_frame_set(self):
        self.F_frame = self.frame_no_slider.value()
        self.f_txt.setText(str(self.F_frame))

    def save_data(self):
        data = {'VideoName': self.video_path.split('/')[-1],
                'Address Frame': [self.A_frame],
                'Top Frame': [self.T_frame],
                'Impact Start Frame': [self.I1_frame],
                'Impact End Frame': [self.I2_frame],
                'Finish Frame': [self.F_frame]}

        df = pd.DataFrame(data)
        df.to_csv(self.label_file,  mode='a', header=False, index=False)


def main():
    app = QApplication([])
    window = My_GUI()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
