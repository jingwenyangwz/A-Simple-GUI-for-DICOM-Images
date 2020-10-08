# WE HAVE TO CHANGE THE valueChanged function as well as : setMinimum, setMaximum, setValue

import cv2
import pydicom

import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from PIL import Image
from PIL.ImageQt import ImageQt
import numpy as np


class MyDICOMdisplayer(QWidget):
   def __init__(self, filepath, parent = None):
      super(MyDICOMdisplayer, self).__init__(parent)
   
      # DATA
      self.dataset = pydicom.dcmread(sys.argv[1])
      self.original_pixel_array=self.dataset.pixel_array
      self.WindowWidth_value = int(self.dataset.WindowWidth)
      self.WindowCenter_value = int(self.dataset.WindowCenter)
      self.get_dicom_array() # get current_pixel_array

      # LAYOUT
      layout = QVBoxLayout() # lines up classes vertically
      self.image_frame = QLabel()
      self.image_frame.setAlignment(Qt.AlignCenter)
      # set image_frame so that we can show the image
      self.show_image() #
      layout.addWidget(self.image_frame)

      # LUMINOSITY SLIDER : beta
      self.slide_luminosity = QSlider(Qt.Horizontal)
      self.slide_luminosity.setTickInterval(1)
      self.slide_luminosity.setMinimum(-255)
      self.slide_luminosity.setMaximum(255)
      self.slide_luminosity.setValue(0)
      self.slide_luminosity.valueChanged.connect(self.valuechange)
      layout.addWidget(QLabel("Luminosity"))
      layout.addWidget(self.slide_luminosity)

      # CONTRAST SLIDER : alpha
      self.slide_contrast = QSlider(Qt.Horizontal)
      self.slide_contrast.setTickInterval(1)
      self.slide_contrast.setMinimum(0)
      self.slide_contrast.setMaximum(200)
      self.slide_contrast.setValue(100)
      self.slide_contrast.valueChanged.connect(self.valuechange)
      layout.addWidget(QLabel("Contrast"))
      layout.addWidget(self.slide_contrast)

      # METHOD: NAIVE, NORMALIZATION, WINDOWING SYSTEM
      self.button_naive = QtWidgets.QPushButton("NAIVE")
      self.button_normalize = QtWidgets.QPushButton("NORMALIZATION")
      self.button_windowing = QtWidgets.QPushButton("WINDOWING SYSTEM")

      #set the window width for the third method: windowing system 
      self.windowWidth = QLineEdit()
      self.windowWidth.setValidator(QIntValidator(0,200)) #set the valid range of input(window width)

      #set the window center for the third method: windowing system 
      self.windowCenter = QLineEdit()
      self.windowCenter.setValidator(QIntValidator(0,100)) #set the valid range of input(window center)

      row_width = QHBoxLayout()
      row_width.addWidget(QLabel("Set window width:"))
      row_width.addWidget(self.windowWidth)
      row_width.addWidget(QLabel("original width: " + str(self.WindowWidth_value)))
      row_width.addStretch()

      row_center = QHBoxLayout()
      row_center.addWidget(QLabel("Set window center:"))
      row_center.addWidget(self.windowCenter)
      row_center.addWidget(QLabel("original center:" + str(self.WindowCenter_value)))
      row_center.addStretch()

      # ADD in LAYOUT
      layout.addWidget(QLabel("Method"))      
      layout.addWidget(self.button_naive)
      layout.addWidget(self.button_normalize)
      layout.addWidget(self.button_windowing)
      layout.addLayout(row_width)
      layout.addLayout(row_center)

      self.setLayout(layout)
      self.setWindowTitle("DICOM dispayer")

      # Changes
      self.button_naive.clicked.connect(self.naivemethod)
      self.button_normalize.clicked.connect(self.normalizationmethod)
      self.button_windowing.clicked.connect(self.windowingmethod)
      
      self.windowWidth.textChanged.connect(self.check_state) #display red if the value is out of range, green if within range
      self.windowWidth.editingFinished.connect(self.changeWindow) 

      self.windowCenter.textChanged.connect(self.check_state)
      self.windowCenter.editingFinished.connect(self.changeWindow)

   # Load image info
   def get_dicom_array(self):
      # read image
      self.current_pixel_array = np.array(self.dataset.pixel_array)

   def show_image(self):
        #self.image = QtGui.QImage(self.pixel_array.repeat(4), self.pixel_array.shape[1], self.pixel_array.shape[0], QtGui.QImage.Format_RGB32)
        tmp_array = self.current_pixel_array.astype(np.uint8)
        self.image = QtGui.QImage(tmp_array, tmp_array.shape[1],
                             tmp_array.shape[0], tmp_array.shape[0], QtGui.QImage.Format_Indexed8)
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image))

   def valuechange(self):
      alpha = self.slide_contrast.value()
      beta = self.slide_luminosity.value()
      self.new_pixel_array = (((self.current_pixel_array/np.max(self.current_pixel_array)-0.5)*(alpha/100) + 0.5)*np.max(self.current_pixel_array)) + beta
      self.new_pixel_array = np.clip(self.new_pixel_array,0,255)
      self.new_pixel_array = self.new_pixel_array.astype(np.uint8)
#self.new_pixel_array=cv2.convertScaleAbs(self.current_pixel_array, alpha=alpha/100, beta=beta) # https://docs.opencv.org/3.4/d3/dc1/tutorial_basic_linear_transform.html
      #self.image = QtGui.QImage(self.new_pixel_array.repeat(4), self.new_pixel_array.shape[1], self.new_pixel_array.shape[0], QtGui.QImage.Format_RGB32)
      
      self.image = QtGui.QImage(self.new_pixel_array, self.new_pixel_array.shape[1],
                             self.new_pixel_array.shape[0], self.new_pixel_array.shape[0], QtGui.QImage.Format_Indexed8)
      self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image))
      
   def naivemethod(self):
      self.current_pixel_array = (self.original_pixel_array/256)
      self.current_pixel_array = np.clip(self.current_pixel_array, 0, 255).astype(np.uint8)
      self.valuechange() #update the luminosity& contrast settings
      print("using method: NAIVE METHOD")

   def normalizationmethod(self):
      the_min = np.min(self.original_pixel_array)
      the_max = np.max(self.original_pixel_array)
      self.current_pixel_array = (255*((self.original_pixel_array - the_min)/(the_max - the_min))).astype(np.uint8)
      self.valuechange() 
      print("using method: NORMALIZATION")


   def windowingmethod(self):
      WINDOW_WIDTH  = self.WindowWidth_value
      WINDOW_CENTER = self.WindowCenter_value
      lower_bound = WINDOW_CENTER - WINDOW_WIDTH/2
      upper_bound = WINDOW_CENTER + WINDOW_WIDTH/2
      self.current_pixel_array = np.clip(self.original_pixel_array, lower_bound, upper_bound)

      the_min = np.min(self.current_pixel_array)
      the_max = np.max(self.current_pixel_array)
      self.current_pixel_array = (255*(self.current_pixel_array - the_min)/(the_max - the_min)).astype(np.uint8)
      self.valuechange()
      print("using method: WINDOWING SYSTEM")


   def changeWindow(self):
      if self.windowWidth.text() != '':
         self.WindowWidth_value = int(self.windowWidth.text())
      if self.windowCenter.text() != '':
         self.WindowCenter_value = int(self.windowCenter.text())

      self.windowingmethod()
      print("the winter width is:", self.WindowWidth_value)
      print("the winter center is:", self.WindowCenter_value)

   #check if the two input numbers fit in the valid boundaries
   def check_state(self):
      sender = self.sender()
      validator = sender.validator()
      state = validator.validate(sender.text(),0)[0]
      if state == QtGui.QValidator.Acceptable:
         color = '#c4df9b' #green
      else:
         color = '#f6989d' #red
      sender.setStyleSheet('QLineEdit{ background-color: %s}'  %color)

def main():
   app = QApplication(sys.argv)
   displayer = MyDICOMdisplayer(sys.argv[1])
   displayer.show()
   sys.exit(app.exec_())
   #QWidget.update() 


if __name__ == '__main__':
   main()
