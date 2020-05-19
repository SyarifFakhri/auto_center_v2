from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap
import cv2
import time
import numpy as np
import math
from centerFinder import CenterFinder
import debugConfigs

class ImageCaptureThread(QtCore.QObject):
    changePixmap = pyqtSignal(QImage)
    rawPixmap = pyqtSignal(QImage)
    centerLabels = pyqtSignal(list)
    callImageCap = pyqtSignal()

    def __init__(self, settingsConfig):
        super(ImageCaptureThread, self).__init__()
        # self.screenCenterX = int(640/2)
        # self.screenCenterY = int(480/2)
        self.screenCenterX = settingsConfig['camera_true_center_x']
        self.screenCenterY = settingsConfig['camera_true_center_y']

        self.centerFinder = CenterFinder()
        self.absoluteCenters = []
        self.relativeCenters = []
        self.validImage = False

        self.roi = [settingsConfig['roi_x'],
                    settingsConfig['roi_y'],
                    settingsConfig['roi_w'],
                    settingsConfig['roi_h']
                    ] #x,w,y,h - right roi
        self.cameraStatus = ''


    @pyqtSlot()
    def cameraCapture(self):
        try:
            # counter = 0
            time.sleep(1)
            self.stopRunning = False
            self.isRunning = True
            cap = cv2.VideoCapture(debugConfigs.VIDEO_CAP_DEVICE + cv2.CAP_DSHOW)
            #cap.set(cv2.CAP_FFMPEG, True)
            #cap.set(cv2.CAP_PROP_FPS, 30)
            
            imageWidth = int(640 * 0.65)
            imageHeight = int(480 * 0.65)

            sizeMult = 1.5
            picWidth = int(640*sizeMult)
            picHeight = int(480*sizeMult)
            while not self.stopRunning:
                # counter += 1

                ret, frame = cap.read()

                if ret:
                    frame = cv2.resize(frame,(picWidth,picHeight))
                    
                    height, width = frame.shape[:2]
                    margin = 100
                    croppedRaw = frame[margin:height - margin, margin:width-margin]
                    rgbImage = cv2.cvtColor(croppedRaw, cv2.COLOR_BGR2RGB)
                    # rgbImage = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    rawImg = convertToQtFormat.scaled(imageWidth,imageHeight, Qt.KeepAspectRatio)

                    self.rawPixmap.emit(rawImg)
                    # print("Get image")
                    self.validImage = self.isValidImage(frame)

                    # self.centers = []
                    #find the center
                    #h, w, ch = frame.shape
                    #print(h,w)
                    roi, centers = self.centerFinder.findCentersOfCircles(frame,self.roi)

                    #should only return one center
                    # centers = centers[0]
                    self.absoluteCenters = centers
                    self.relativeCenters = self.getRelativeCenterPoints()

                    #Add centers of circles
                    cv2.rectangle(frame, (self.screenCenterX, 0), (self.screenCenterX, picHeight), (255,0,0), 1)
                    cv2.rectangle(frame, (0, self.screenCenterY), (picWidth, self.screenCenterY), (255, 0, 0), 1)

                    #cv2.putText(frame, self.cameraStatus, (20,300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),3 )

                    height, width = frame.shape[:2]
                    margin = 100
                    frame = frame[margin:height - margin, margin:width-margin]
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # rgbImage = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(imageWidth, imageHeight, Qt.KeepAspectRatio)

                    self.changePixmap.emit(p)
                    # print("EMIT CAP", counter)
                    if len(self.relativeCenters) == 1 and self.validImage == True: #only emit if it's a valid centerpoint
                        self.centerLabels.emit(self.relativeCenters)
                    else:
                        self.centerLabels.emit([])
                    # print("Done emitting")

            cap.release()
            print("Release camera")
            self.isRunning = False
        except Exception as e:
            print("Error at camera capture thread")
            print(e)

    def isValidImage(self, image):
        #Check if the image is too dark
        average = np.mean(image)
        if average < 20:
            #print("Invalid Image", average)
            return False
        return True

    def getRelativeCenterPoints(self):
        relativeCenterPoints = []
        # First get the position relative to the center
        for center in self.absoluteCenters:
            relativeCenterX = center[0] - self.screenCenterX
            relativeCenterY = center[1] - self.screenCenterY
            relativeCenterPoints.append([relativeCenterX, relativeCenterY])
        return relativeCenterPoints


    def programCenterPointRotAdjMethod(self, param):
        """
        Instead of getting the error by first programming, try to get the x, y, error by calculating the rotational error.
        This process is a little bit mathematically involved. To get a full explanation, look at testRotateMethod.py, where I test out this method
        :param param:
        :return:
        """

        if self.validImage == False:
            print("Invalid image")

        leftAngleCenterPoint = self.centers[0]
        rightAngleCenterPoint = self.centers[2]

        angle = self.getAngleBetweenTwoPoints(leftAngleCenterPoint, rightAngleCenterPoint)

        detectedCenterPoint = self.centers[1]
        targetCenterPoint = (self.screenCenterX, self.screenCenterY)

        convertedCenterPoint = self.rotatePointAroundCenter(detectedCenterPoint, targetCenterPoint, -angle)
        translationVector = [
            convertedCenterPoint[0] - detectedCenterPoint[0],
            convertedCenterPoint[1] - detectedCenterPoint[1]
        ]

        #the final translation vector is how much it needs to be programmed
        programX = translationVector[0]
        programY = translationVector[1]

        print(programX, programY)

    #some utility defs
    def getAngleBetweenTwoPoints(self, pointA, pointB):
        """point a is the reference in this case, referenced to the x axis"""
        xDist = pointA[0] - pointB[0]
        yDist = pointA[1] - pointB[1]

        return math.atan(yDist / xDist)

    def roundInt(self, num):
        return int(round(num))

    def rotatePointAroundCenter(self,pointCoord, centerCoord, angle):
        rotated_x = (math.cos(angle) * (pointCoord[0] - centerCoord[0]) - math.sin(angle) * (pointCoord[1] - centerCoord[1])) + centerCoord[0]
        rotated_y = (math.sin(angle) * (pointCoord[0] - centerCoord[0]) + math.cos(angle) * (pointCoord[1] - centerCoord[1])) + centerCoord[1]
        return (rotated_x, rotated_y)

    def stop(self):
        self.stopRunning = True
        # self.terminate()

class DebugImageThread(QtCore.QObject):
    """
    Primarily used for the settings window to view all the image settings
    """
    changePixmap = pyqtSignal(QImage)
    call_camera = pyqtSignal()
    centerLabels = pyqtSignal(list)

    def __init__(self, settings):
        super(DebugImageThread, self).__init__()
        self.settings = settings
        self.screenCenterX = settings['camera_true_center_x']
        self.screenCenterY = settings['camera_true_center_y']

        self.centerFinder = CenterFinder()
        self.absoluteCenters = []

    @pyqtSlot()
    def debugCameraCapture(self):
        try:
            time.sleep(1)
            self.stopRunning = False
            cap = cv2.VideoCapture(debugConfigs.VIDEO_CAP_DEVICE)
            sizeMult = 1.5
            picWidth = int(640*sizeMult)
            picHeight = int(480*sizeMult)
            while not self.stopRunning:
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame,(picWidth,picHeight))
                    x = self.settings['roi_x']
                    y = self.settings['roi_y']
                    w = self.settings['roi_w']
                    h = self.settings['roi_h']

                    #show the center of the center circle
                    roi, self.absoluteCenters = self.centerFinder.findCentersOfCircles(frame, [x,y,w,h])
                    self.relativeCenters = self.getRelativeCenterPoints()
                    cv2.rectangle(frame, (self.settings['camera_true_center_x'], 0), (self.settings['camera_true_center_x'], picHeight), (255, 0, 0), 1)
                    cv2.rectangle(frame, (0, self.settings['camera_true_center_y']), (picWidth, self.settings['camera_true_center_y']), (255, 0, 0), 1)

                    cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0),2)
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(400, 360, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)

                    if len(self.relativeCenters) == 1:  # only emit if it's a valid centerpoint
                        self.centerLabels.emit(self.relativeCenters)
                    else:
                        self.centerLabels.emit([])

            cap.release()
        except Exception as e:
            try:
                cap.release()
            except:
                pass
            print(e)

    def getRelativeCenterPoints(self):
        relativeCenterPoints = []
        # First get the position relative to the center
        for center in self.absoluteCenters:
            relativeCenterX = center[0] - self.screenCenterX
            relativeCenterY = center[1] - self.screenCenterY
            relativeCenterPoints.append([relativeCenterX, relativeCenterY])
        return relativeCenterPoints

    def stop(self):
        self.stopRunning = True
        # self.terminate()
