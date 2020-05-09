import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap
import PyQt5 as qt
from tinydb import TinyDB, Query
import time
import math

from centerFinder import CenterFinder
from flashTool import FlashTool
from arduinoController import ArduinoController

import pyqtgraph as pg
import numpy as np

import cv2

class ProgramCamera(QtCore.QObject):
    callDoubleProgramCamera = pyqtSignal()
    callProgramCamera = pyqtSignal()
    statsData = pyqtSignal(list)

    callEngageHydraulics = pyqtSignal()
    callReleaseHydraulics = pyqtSignal()

    def __init__(self):
        super(ProgramCamera, self).__init__()
        self.flashTool = FlashTool()
        self.currentProgrammingStep = ''
        self.relativeCenters = []
        self.currentCameraType = ''

        self.PROGRAMMING_TIME_THRESH = 3

        # self.arduinoController = ArduinoController()
        # self.arduinoController.bothButtonsPressed.connect(self.programCenterPointDoubleProgramMethod)
        # self.arduinoController.onCamera()
        # self.arduinoController.onLeds()


    @pyqtSlot()
    def engageHydraulics(self):
        self.arduinoController.engageHydraulics()

    @pyqtSlot()
    def releaseHydraulics(self):
        self.arduinoController.releaseHydraulics()

    @pyqtSlot()
    def retractSliders(self):
        print("RELEASE HYDRAULICS")
        self.arduinoController.engageHydraulics()
        time.sleep(2)
        self.arduinoController.releaseHydraulics()

    @pyqtSlot(list)
    def updateRelativeCenters(self, cameraCenters):
        self.relativeCenters = cameraCenters

    @pyqtSlot()
    def resetCameraOffsets(self):
        self.arduinoController.onCamera()
        # self.arduinoController.onLeds()
        self.isProgramming = True
        self.currentProgrammingStep = 'Alter CFG'

        programX = 0  # Very strange that this doesn't require a negative sign. Did I mess up somewhere?
        programY = 0

        programX = self.clipValue(programX)
        programY = self.clipValue(programY)

        print("Value to Program X: " + str(programX))
        print("Value to Program Y: " + str(programY))

        #self.flashTool.alterCFGFileCameraOffset(programX, programY)
        self.flashTool.alterCFGFileD55LCamera(programX, programY)
        self.currentProgrammingStep = 'Create Bin'
        self.flashTool.createBinFileCmd(self.currentCameraType)
        self.currentProgrammingStep = 'Resetting Camera Offsets'
        tic = time.perf_counter()
        self.flashTool.flashCameraCmd()
        toc = time.perf_counter()

        timeTaken = toc - tic

        if (timeTaken < self.PROGRAMMING_TIME_THRESH):
            self.currentProgrammingStep = 'Programming failed. Check connection.'
            time.sleep(3)
            self.currentProgrammingStep = ''
            self.arduinoController.offLeds()
            return False

        self.powerCycleCamera()

        self.currentProgrammingStep = ''
        print("Finished programming.")
        self.arduinoController.offLeds()
        return True

    def powerCycleCamera(self):
        print("Power cycling camera")
        self.currentProgrammingStep = 'Power cycling camera'
        self.arduinoController.offCamera()
        time.sleep(1)
        self.arduinoController.onCamera()
        time.sleep(2)
        QApplication.processEvents()
        print("Camera reset")

    @pyqtSlot()
    def programCenterPointDoubleProgramMethod(self):
        """
        It's very likely we won't get the correct amount on the first try.
        So this method first programs it once, then calculates the offsets again, then adds that adjustment amount to the old amount
        and reprograms again

        Pros: simple
        cons: slow, because you have to reprogram twice
        :param param:
        :return:

        TODO:
        1. check if the camera is connected (Check if it's just a blank screen) - DONE
        2. check if the camera can be programmed/is detected (Based on timing)
        3. Check if  the new center point is correct
        """
        self.arduinoController.onCamera()
        self.currentProgrammingStep = "Engaging Hydraulics"
        self.arduinoController.engageHydraulics()
        # self.arduinoController.onLeds()

        QApplication.processEvents()
        time.sleep(3)

        if self.relativeCenters == []:
            print("No valid centerpoints")
            self.statsData.emit(['failed', []])
            # self.arduinoController.releaseHydraulics()
            return

        relativeCenterPoints = self.relativeCenters
        centerPoints = relativeCenterPoints[0]
        initialCenterPoints = relativeCenterPoints[0]


        # check if it's already center
        #REENABLE BACK
        # if self.isCenterPointCenter(centerPoints):
        #     print("Camera Centered!")
        #     self.currentProgrammingStep = "Camera Centered"
        #     time.sleep(2)
        #     self.currentProgrammingStep = ''
        #     self.isProgramming = False
        #     self.statsData.emit(['success', initialCenterPoints])
        #     return

        #STEP 1 - RESET CAMERA OFFSETS
        succeeded = self.resetCameraOffsets() #succeeded means programming did not fail

        if not succeeded:
            self.statsData.emit(['failed', initialCenterPoints])
            # self.arduinoController.releaseHydraulics()
            return

        #STEP 2 - PROGRAM FIRST CENTER POINT CORRECTION
        # for i in range(10):
        #     self.currentProgrammingStep = 'Restart cam: ' + str(10 - i)
        # self.powerCycleCamera()

        # if self.validImage == False:
        #     print("Invalid image")
        print('start')
        self.currentProgrammingStep = 'Alter CFG'
        #STEP 2.1 - Check if already center
        relativeCenterPoints = self.relativeCenters

        # pass the center centerpoint
        centerPoints = relativeCenterPoints[0]  # 0: left center point, 1: center center point, 2: right center point IF using 3 points

        # check if it's already center
        if self.isCenterPointCenter(centerPoints):
            print("Camera Centered!")
            self.currentProgrammingStep = "Camera Centered"
            time.sleep(5)
            self.currentProgrammingStep = ''
            self.isProgramming = False
            self.statsData.emit(['succeeded', initialCenterPoints])
            # self.arduinoController.releaseHydraulics()
            self.arduinoController.releaseHydraulics()
            return

        # self.stopRunning = True #temporarily pause the camera

        programX = centerPoints[0] #The camera is mirrored on the x axis
        programY = -centerPoints[1]

        programX = self.clipValue(programX)
        programY = self.clipValue(programY)

        # programX = 0
        # programY = 0

        print("Value to Program X: " + str(programX))
        print("Value to Program Y: " + str(programY))

        # self.flashTool.alterCFGFileCameraOffset(programX, programY)
        self.flashTool.alterCFGFileD55LCamera(programX, programY)
        self.currentProgrammingStep = 'Create Bin'
        self.flashTool.createBinFileCmd(self.currentCameraType)
        self.currentProgrammingStep = 'Flashing Camera 1 - DO NOT UNPLUG'

        tic = time.perf_counter()
        self.flashTool.flashCameraCmd()
        toc = time.perf_counter()

        timeTaken = toc - tic

        if (timeTaken < self.PROGRAMMING_TIME_THRESH):
            self.currentProgrammingStep = 'Programming failed. Check connection.'
            time.sleep(5)
            self.currentProgrammingStep = ''
            self.arduinoController.releaseHydraulics()
            return


        self.currentProgrammingStep = ''
        # QThread.sleep(10) #sleep an amount of time
        # time.sleep(10)
        self.powerCycleCamera()

        # for i in range(10):
        #     self.currentProgrammingStep = 'Restart cam: ' + str(10 - i)
        #     time.sleep(1)
        #     QApplication.processEvents()

        print("Relative centers: ", self.relativeCenters[0])
        ###Begin second camera flash
        relativeCenterPoints = self.relativeCenters
        centerPoints = relativeCenterPoints[0]

        # check if it's already center
        if self.isCenterPointCenter(centerPoints):
            print("Camera Centered!")
            self.currentProgrammingStep = "Camera Centered"
            time.sleep(5)
            self.currentProgrammingStep = ''
            self.statsData.emit(['succeeded', initialCenterPoints])
            self.arduinoController.releaseHydraulics()
            return

        programX += centerPoints[0]
        programY += -centerPoints[1]

        programX = self.clipValue(programX)
        programY = self.clipValue(programY)

        # programX = 0
        # programY = 0

        print("Value to Program X: " + str(programX))
        print("Value to Program Y: " + str(programY))

        # self.flashTool.alterCFGFileCameraOffset(programX, programY)
        self.flashTool.alterCFGFileD55LCamera(programX, programY)
        self.currentProgrammingStep = 'Create Bin'
        self.flashTool.createBinFileCmd(self.currentCameraType)
        self.currentProgrammingStep = 'Flashing Camera 2 - DO NOT UNPLUG'
        self.flashTool.flashCameraCmd()
        self.currentProgrammingStep = 'Finished Programming'
        print("Finished programming.")

        self.powerCycleCamera()

        #check if it succeeded
        relativeCenterPoints = self.relativeCenters
        centerPoints = relativeCenterPoints[0]

        if self.isCenterPointCenter(centerPoints):
            self.currentProgrammingStep = 'Programming Suceeded'
            self.statsData.emit(['succeeded', initialCenterPoints])

        else:
            self.currentProgrammingStep = 'Could not center'
            self.statsData.emit(['failed', initialCenterPoints])

        time.sleep(5)
        self.currentProgrammingStep = 'Releasing Hydraulics'
        self.arduinoController.releaseHydraulics()
        self.currentProgrammingStep = ''
        self.arduinoController.running = False

    def clipValue(self, value, clipTo=35):
        if abs(value) > clipTo:
            if value > 0:
                value = clipTo
            if value < 0:
                value = -clipTo
            else:
                value = 0
        return value

    def isCenterPointCenter(self, centerPoints, threshold=1):
        """Check if the RELATIVE center points are valid"""
        if abs(centerPoints[0]) <= threshold:
            if abs(centerPoints[1]) <= threshold:
                return True
        return False



class ImageCaptureThread(QtCore.QObject):
    changePixmap = pyqtSignal(QImage)
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
            time.sleep(1)
            self.stopRunning = False
            self.isRunning = True
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_FFMPEG, True)
            cap.set(cv2.CAP_PROP_FPS, 30)
            while not self.stopRunning:
                ret, frame = cap.read()

                if ret:
                    # print("Get image")
                    self.validImage = self.isValidImage(frame)

                    # self.centers = []
                    #find the center
                    roi, centers = self.centerFinder.findCentersOfCircles(frame,self.roi)

                    #should only return one center
                    # centers = centers[0]
                    self.absoluteCenters = centers
                    self.relativeCenters = self.getRelativeCenterPoints()

                    #Add centers of circles
                    cv2.rectangle(frame, (self.screenCenterX, 0), (self.screenCenterX, 480), (255,0,0), 1)
                    cv2.rectangle(frame, (0, self.screenCenterY), (640, self.screenCenterY), (255, 0, 0), 1)

                    cv2.putText(frame, self.cameraStatus, (20,300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),3 )

                    height, width = frame.shape[:2]
                    margin = 100
                    frame = frame[margin:height - margin, margin:width-margin]
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # rgbImage = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)

                    if len(self.relativeCenters) == 1: #only emit if it's a valid centerpoint
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
        if average < 50:
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
        time.sleep(1)
        self.stopRunning = False
        cap = cv2.VideoCapture(0)
        while not self.stopRunning:
            ret, frame = cap.read()
            if ret:
                x = self.settings['roi_x']
                y = self.settings['roi_y']
                w = self.settings['roi_w']
                h = self.settings['roi_h']

                #show the center of the center circle
                roi, self.absoluteCenters = self.centerFinder.findCentersOfCircles(frame, [x,y,w,h])
                self.relativeCenters = self.getRelativeCenterPoints()
                cv2.rectangle(frame, (self.settings['camera_true_center_x'], 0), (self.settings['camera_true_center_x'], 480), (255, 0, 0), 1)
                cv2.rectangle(frame, (0, self.settings['camera_true_center_y']), (640, self.settings['camera_true_center_y']), (255, 0, 0), 1)

                cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0),2)
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(480, 360, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

                if len(self.relativeCenters) == 1:  # only emit if it's a valid centerpoint
                    self.centerLabels.emit(self.relativeCenters)
                else:
                    self.centerLabels.emit([])

        cap.release()

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

class StatisticsWindow():
    def init_ui(self, mainWindow, database):
        self.layout = QGridLayout()
        self.layout.setSpacing(20)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)

        mainTitle = QLabel("Auto Center Tool")
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        self.mainLabel = QLabel("Main")
        self.statisticsLabel = QLabel("Statistics")
        self.statisticsLabel.setStyleSheet("background-color: #4a4a4a")
        self.settingsLabel = QLabel("Settings")

        vbox.addWidget(mainTitle)
        vbox.addWidget(self.mainLabel)
        vbox.addWidget(self.statisticsLabel)
        vbox.addWidget(self.settingsLabel)
        vbox.addStretch(1)

        vCharts = QVBoxLayout()

        statisticsTitle = QLabel("Lifetime Statistics")
        statisticsTitle.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        accepted = database['goodSample']
        rejected = database['rejectedSample']

        totalCameraLabel = QLabel("Total cameras Programmed: " + str(accepted + rejected))

        acceptedCameraLabel = QLabel("Accepted: " + str(accepted))
        rejectedCameraLabel = QLabel("Rejected: " + str(rejected))

        xyAlignment = self.xyAlignmentStats(database['xyAlignmentStats'])

        vCharts.addWidget(statisticsTitle)
        vCharts.addWidget(totalCameraLabel)
        vCharts.addWidget(acceptedCameraLabel)
        vCharts.addWidget(rejectedCameraLabel)
        vCharts.addWidget(xyAlignment)

        #add scroll
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        # scroll.setEnabled(True)
        scroll.setMinimumHeight(500)
        scroll.setMinimumWidth(750)
        widget = QWidget()
        widget.setLayout(vCharts)
        scroll.setWidget(widget)

        self.layout.addLayout(vbox, 0, 0)
        # layout.addWidget(totalAccepted, 0, 1)
        self.layout.addWidget(scroll, 0,1)

        widget = QWidget()
        widget.setLayout(self.layout)
        mainWindow.setCentralWidget(widget)

    def xyAlignmentStats(self,xyAlignmentStats):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(x=False, y=False)
        plot.setMinimumHeight(480)
        plot.setMinimumWidth(640)
        plot.setBackground('#353535')
        plot.setTitle('XY Alignment Distribution', size='20pt')

        pen = pg.mkPen(color=(255,0,0))

        x = [item[0] for item in xyAlignmentStats]
        y = [item[1] for item in xyAlignmentStats]

        scatterPlot = pg.ScatterPlotItem(pen=pen, symbol='x') #size=10, pen=pen, symbol='O',  brush=pg.mkBrush(255, 255, 255, 120)
        scatterPlot.addPoints(x, y)

        plot.addItem(scatterPlot)

        return plot

class LoginWindow():
    def init_ui(self, mainWindow):
        layout = QGridLayout()
        layout.setSpacing(20)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)

        mainTitle = QLabel("Auto Center Tool")
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        self.mainLabel = QLabel("Main")
        self.statisticsLabel = QLabel("Statistics")
        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setStyleSheet("background-color: #4a4a4a")

        vbox.addWidget(mainTitle)
        vbox.addWidget(self.mainLabel)
        vbox.addWidget(self.statisticsLabel)
        vbox.addWidget(self.settingsLabel)
        vbox.addStretch(1)

        loginFrame = QFrame()
        loginFrame.setFrameStyle(QFrame.Box)
        # loginFrame.setStyleSheet("background-color: black")
        # loginFrame.setColor(QtGui.QColor("black"))
        loginPrompt = QVBoxLayout()

        loginTitle = QLabel("Please enter your username and password: ")
        loginTitle.setAlignment(Qt.AlignCenter)

        userPrompt, self.userNameTextBox = self.labelWithTextEdit("Username")
        passPrompt, self.passNameTextBox = self.labelWithTextEdit("Password",password=True)

        self.loginButton = QPushButton("Login")

        self.helpText = QLabel("") #Help text in case they get the password or username wrong
        self.helpText.setAlignment(Qt.AlignRight)

        loginPrompt.addStretch(1)
        loginPrompt.addWidget(loginTitle)
        loginPrompt.addLayout(userPrompt)
        loginPrompt.addLayout(passPrompt)
        loginPrompt.addWidget(self.loginButton)
        loginPrompt.addWidget(self.helpText)

        loginPrompt.addStretch(1)

        loginFrame.setLayout(loginPrompt)

        loginFrame.setContentsMargins(300,50,300,50) #l,t,r,b
        loginFrame.setMaximumSize(1000,300)
        # loginFrame.setStyleSheet("background-color: black")

        layout.addLayout(vbox, 0, 0)
        layout.addWidget(loginFrame,0,1)

        widget = QWidget()
        widget.setLayout(layout)
        mainWindow.setCentralWidget(widget)

    def labelWithTextEdit(self, text, password=False):
        hbox = QHBoxLayout()
        label = QLabel(text)
        textBox = QLineEdit()
        textBox.setStyleSheet("QLineEdit {background: rgb(255, 255, 255); selection-background-color: rgb(100, 100, 100); color: black }")
        # textBox.setAlignment(Qt.AlignRight)
        textBox.setMaximumSize(170,100)

        if password:
            textBox.setEchoMode(QtGui.QLineEdit.Password)

        hbox.addWidget(label)
        hbox.addWidget(textBox)

        return hbox, textBox

class SettingsWindow():
    def init_ui(self, mainWindow, settings):
        layout = QGridLayout()
        layout.setSpacing(20)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)

        mainTitle = QLabel("Auto Center Tool")
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        self.mainLabel = QLabel("Main")
        self.statisticsLabel = QLabel("Statistics")
        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setStyleSheet("background-color: #4a4a4a")

        vbox.addWidget(mainTitle)
        vbox.addWidget(self.mainLabel)
        vbox.addWidget(self.statisticsLabel)
        vbox.addWidget(self.settingsLabel)
        vbox.addStretch(1)

        self.imageLabel = QLabel(mainWindow)

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        # scroll.setEnabled(True)
        scroll.setMaximumHeight(200)
        # scroll.setMinimumWidth(750)

        gridSettings = QGridLayout()
        roiXLabel = QLabel("ROI X: ")
        roiYLabel = QLabel("ROI Y: ")
        roiWLabel = QLabel("ROI W: ")
        roiHLabel = QLabel("ROI H: ")
        centerXLabel = QLabel("X Center: ")
        centerYLabel = QLabel("Y Center: ")

        self.roiXLabelvalue = QLabel(str(settings['roi_x']))
        self.roiYLabelvalue = QLabel(str(settings['roi_y']))
        self.roiWLabelvalue = QLabel(str(settings['roi_w']))
        self.roiHLabelvalue = QLabel(str(settings['roi_h']))
        self.centerXLabelValue = QLabel(str(settings['camera_true_center_x']))
        self.centerYLabelValue = QLabel(str(settings['camera_true_center_y']))

        self.roiXSlider = QSlider(Qt.Horizontal)
        self.roiXSlider.setMaximum(settings['camera_width'])
        self.roiXSlider.setValue(settings['roi_x'])

        self.roiYSlider = QSlider(Qt.Horizontal)
        self.roiYSlider.setMaximum(settings['camera_height'])
        self.roiYSlider.setValue(settings['roi_y'])

        self.roiWSlider = QSlider(Qt.Horizontal)
        self.roiWSlider.setMaximum(settings['camera_width'])
        self.roiWSlider.setValue(settings['roi_w'])

        self.roiHSlider = QSlider(Qt.Horizontal)
        self.roiHSlider.setMaximum(settings['camera_height'])
        self.roiHSlider.setValue(settings['roi_h'])

        self.centerXSlider = QSlider(Qt.Horizontal)
        self.centerXSlider.setMaximum(settings['camera_width'])
        self.centerXSlider.setValue(settings['camera_true_center_x'])

        self.centerYSlider = QSlider(Qt.Horizontal)
        self.centerYSlider.setMaximum(settings['camera_height'])
        self.centerYSlider.setValue(settings['camera_true_center_y'])

        self.saveButton = QPushButton('Save Settings')

        gridSettings.addWidget(roiXLabel, 0, 0)
        gridSettings.addWidget(roiYLabel, 1, 0)
        gridSettings.addWidget(roiWLabel, 2, 0)
        gridSettings.addWidget(roiHLabel, 3, 0)
        gridSettings.addWidget(centerXLabel, 4,0)
        gridSettings.addWidget(centerYLabel, 5,0)

        gridSettings.addWidget(self.roiXSlider, 0,1)
        gridSettings.addWidget(self.roiYSlider, 1,1)
        gridSettings.addWidget(self.roiWSlider, 2,1)
        gridSettings.addWidget(self.roiHSlider, 3,1)
        gridSettings.addWidget(self.centerXSlider, 4, 1)
        gridSettings.addWidget(self.centerYSlider, 5,1)

        gridSettings.addWidget(self.roiXLabelvalue, 0, 2)
        gridSettings.addWidget(self.roiYLabelvalue, 1, 2)
        gridSettings.addWidget(self.roiWLabelvalue, 2, 2)
        gridSettings.addWidget(self.roiHLabelvalue, 3, 2)
        gridSettings.addWidget(self.centerXLabelValue, 4,2)
        gridSettings.addWidget(self.centerYLabelValue,5,2)

        gridSettings.addWidget(self.saveButton, 6,1)

        rightVBox = QVBoxLayout()
        rightVBox.setSpacing(10)


        # xCenterLabel = QLabel('X:   0   ')
        # xCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))
        #
        # yCenterLabel = QLabel('Y:   0   ')
        # yCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        manualControlLabel = QLabel("Manual Control")
        manualControlLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        self.releaseButton = QPushButton("Release Hydraulics")
        self.engageButton = QPushButton("Engage Hydraulics")
        self.programOffsetButton = QPushButton("Manual Program")
        self.tareButton = QPushButton("Tare Center")

        self.chooseCurrentCamera = QtGui.QComboBox()
        self.chooseCurrentCamera.addItem(settings['currentCameraType'])

        self.chooseCurrentCamera.addItem("d55l")
        self.chooseCurrentCamera.addItem("cp1p")

        # rightVBox.addStretch(1)
        # rightVBox.addWidget(xCenterLabel)
        # rightVBox.addWidget(yCenterLabel)
        # rightVBox.addStretch(10)

        rightVBox.addWidget(manualControlLabel)
        rightVBox.addWidget(self.releaseButton)
        rightVBox.addWidget(self.engageButton)
        rightVBox.addWidget(self.programOffsetButton)
        rightVBox.addWidget(self.tareButton)
        rightVBox.addWidget(self.chooseCurrentCamera)
        rightVBox.addStretch(1)

        widget = QWidget()
        widget.setLayout(gridSettings)
        scroll.setWidget(widget)

        layout.addLayout(vbox, 0, 0)
        layout.addLayout(rightVBox, 0, 2)
        layout.addWidget(self.imageLabel, 0, 1)
        # layout.addLayout(gridSettings, 1,1)
        layout.addWidget(scroll, 1, 1)

        widget = QWidget()
        widget.setLayout(layout)
        mainWindow.setCentralWidget(widget)

class MainWindow():
    def init_ui(self, mainWindow):

        self.centers = None

        self.layout = QGridLayout()
        self.layout.setSpacing(20)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)

        mainTitle = QLabel("Auto Center Tool")
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        self.mainLabel = QLabel("Main")
        self.mainLabel.setStyleSheet("background-color: #4a4a4a")
        self.mainLabel.setFont(QtGui.QFont("Lato", pointSize=10))

        self.statisticsLabel = QLabel("Statistics")
        self.statisticsLabel.setFont(QtGui.QFont("Lato", pointSize=10))

        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setFont(QtGui.QFont("Lato", pointSize=10))

        vbox.addWidget(mainTitle)
        vbox.addWidget(self.mainLabel)
        vbox.addWidget(self.statisticsLabel)
        vbox.addWidget(self.settingsLabel)
        vbox.addStretch(1)

        self.imageLabel = QLabel(mainWindow)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        hbox = QHBoxLayout()

        self.GLabel = QLabel("G")
        self.GLabel.setStyleSheet("background-color: #4a4a4a");
        self.GLabel.setAlignment(Qt.AlignCenter)
        self.GLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        NGLabel = QLabel("NG")
        NGLabel.setStyleSheet("background-color: #4a4a4a")
        NGLabel.setAlignment(Qt.AlignCenter)
        NGLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        hbox.addWidget(self.GLabel)
        hbox.addWidget(NGLabel)

        rightVBox = QVBoxLayout()
        rightVBox.setSpacing(10)

        self.xCenterLabel = QLabel('Center X:   0   ')
        self.xCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        self.yCenterLabel = QLabel('Center Y:   0   ')
        self.yCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        # self.xCenterLeftLabel = QLabel('CLX:   0   ')
        # self.xCenterLeftLabel.setFont(QtGui.QFont("Lato", pointSize=20))
        #
        # self.yCenterleftLabel = QLabel('CLY:   0   ')
        # self.yCenterleftLabel.setFont(QtGui.QFont("Lato", pointSize=20))
        #
        # self.xCenterRightLabel = QLabel('CRX:   0   ')
        # self.xCenterRightLabel.setFont(QtGui.QFont("Lato", pointSize=20))
        #
        # self.yCenterRightLabel = QLabel('CRY:   0   ')
        # self.yCenterRightLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        self.resetCamButton = QPushButton('Reset camera Offset')

        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)

        rightVBox.addStretch(1)
        # rightVBox.addWidget(self.xCenterLeftLabel)
        # rightVBox.addWidget(self.yCenterleftLabel)
        rightVBox.addWidget(self.xCenterLabel)
        rightVBox.addWidget(self.yCenterLabel)
        # rightVBox.addWidget(self.xCenterRightLabel)
        # rightVBox.addWidget(self.yCenterRightLabel)
        rightVBox.addWidget(line)

        rightVBox.addWidget(self.resetCamButton)

        rightVBox.addStretch(10)

        self.layout.addLayout(vbox, 0, 0)
        self.layout.addLayout(hbox, 1, 1)
        self.layout.addLayout(rightVBox, 0, 2)
        self.layout.addWidget(self.imageLabel, 0, 1)

        widget = QWidget()
        widget.setLayout(self.layout)
        mainWindow.setCentralWidget(widget)

class MasterWindow(QMainWindow):
    def __init__(self, app):
        super(MasterWindow, self).__init__()
        self.setWindowTitle("Auto Center Tool")
        self.flashTool = FlashTool()

        self.statsWindow = StatisticsWindow()
        self.settingsWindow = SettingsWindow()
        self.loginWindow = LoginWindow()

        # self.showStatsMenu(None)

        #general flash settings
        self.settingsConfig = TinyDB('settings.json')
        settingsConfigField = Query()
        if not self.settingsConfig.search(settingsConfigField.title.exists()):
            self.settingsConfig.upsert({
                'title':'settingsConfig',
                'roi_x':0,
                'roi_y':0,
                'roi_w':0,
                'roi_h':0,
                'camera_width':640,
                'camera_height': 480,
                'camera_true_center_x':640/2,
                'camera_true_center_y':480/2,
                'currentCameraType':'d55l', #d55l or cp1p
            }, settingsConfigField.title == 'settingsConfig') #A good alternative is using contains instead
        #general user settings
        if not self.settingsConfig.search(settingsConfigField.userTitle.exists()):
            self.settingsConfig.upsert({
                'userTitle': 'userDetail',
                'username': 'admin',
                'password': 'admin',
            }, settingsConfigField.userTitle == 'userDetail')  # A good alternative is using contains instead

        #general database settings
        self.database = TinyDB('database.json')
        databaseField = Query()
        if not self.database.search(databaseField.title.exists()):
            self.database.upsert({
                'title': 'cameraStats',
                'd55l': {
                    'goodSample': 0,
                    'rejectedSample': 0,
                    'xyAlignmentStats': [],
                },
                'cp1p': {
                    'goodSample': 0,
                    'rejectedSample': 0,
                    'xyAlignmentStats': [],
                }
            }, settingsConfigField.title == 'cameraStats')

        picSettings = self.settingsConfig.get(settingsConfigField.title == 'settingsConfig')

        self.capThread = QThread()
        self.capThread.start()
        self.imageCap = ImageCaptureThread(settingsConfig=picSettings)
        self.imageCap.moveToThread(self.capThread)

        self.programCam = ProgramCamera()
        self.programThread = QThread()
        self.programCam.moveToThread(self.programThread)
        self.programThread.start()

        self.programCam.callDoubleProgramCamera.connect(self.programCam.programCenterPointDoubleProgramMethod)
        self.programCam.callProgramCamera.connect(self.programCam.resetCameraOffsets)
        self.programCam.statsData.connect(self.recordStatsInDatabase)
        self.programCam.callEngageHydraulics.connect(self.programCam.engageHydraulics)
        self.programCam.callReleaseHydraulics.connect(self.programCam.releaseHydraulics)

        self.programCam.currentCameraType = self.settingsConfig.all()[0]['currentCameraType']

        self.settingsImageCap = DebugImageThread(picSettings)
        self.settingsThread = QThread()
        self.settingsImageCap.moveToThread(self.settingsThread)
        self.settingsThread.start()

        self.mainWindow = MainWindow()

        self.isAuthenticated = False

        self.setMaximumWidth(1000)
        self.setMaximumHeight(600)

        self.showMainWindow(None)

        self.isRecordingStats = False

        app.aboutToQuit.connect(self.stopProgram)

    def stopProgram(self):
        print("Stop all")
        self.capThread.quit()
        self.settingsThread.quit()
        self.programThread.quit()

    def errorOutputWritten(self, text):
        self.normalOutputWritten("*** ERROR: " + text)


    @pyqtSlot(list)
    def recordStatsInDatabase(self, stats):
        #Stats is an array containing at index 0, success or fail
        #at index 1 the centerpoints

        if self.isRecordingStats:
            currentCameraType = self.programCam.currentCameraType
            database = self.database.all()[0][currentCameraType]

            currentGoodSample = database['goodSample']
            currentRejectedSample = database['rejectedSample']
            currentAlignmentStats = database['xyAlignmentStats']

            if stats[0] == 'failed':
                currentRejectedSample += 1

            if stats[0] == 'succeeded':
                currentGoodSample += 1

            if len(stats[1]) == 3:
                currentAlignmentStats.append(stats[1][1])


            databaseField = Query()
            self.settingsConfig.update({
                currentCameraType:{
                    'goodSample':currentGoodSample,
                    'rejectedSample':currentRejectedSample,
                    'xyAlignmentStats':currentAlignmentStats,
                }  # d55l or cp1p
            }, databaseField.title == 'cameraStats')  # A good alternative is using contains instead

    def programCamera(self, param):
        self.programCam.callDoubleProgramCamera.emit()

    def resetCamera(self, param):
        self.programCam.callProgramCamera.emit()

    @pyqtSlot(QImage)
    def setImageCap(self,image):
        self.imageCap.cameraStatus = self.programCam.currentProgrammingStep
        self.mainWindow.imageLabel.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(QImage)
    def setSettingsImage(self,image):
        self.imageCap.cameraStatus = self.programCam.currentProgrammingStep
        self.settingsWindow.imageLabel.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(list)
    def setLabelData(self, stringList):
        if len(stringList) >= 1:
            # self.mainWindow.xCenterLeftLabel.setText("CLX: " + str(stringList[0][0]))
            # self.mainWindow.yCenterleftLabel.setText("CLY: " + str(stringList[0][1]))

            self.mainWindow.xCenterLabel.setText("Center X: " + str(stringList[0][0]))
            self.mainWindow.yCenterLabel.setText("Center Y: " + str(stringList[0][1]))

            # self.mainWindow.xCenterRightLabel.setText("CRX: " + str(stringList[2][0]))
            # self.mainWindow.yCenterRightLabel.setText("CRY: " + str(stringList[2][1]))

    def stopImageSettingsCap(self):
        try:
            self.settingsImageCap.disconnect()
            pass
        except Exception as e:
            print(e)
        self.settingsImageCap.stop()

    def stopImageCap(self):
        try:
            self.imageCap.disconnect()
        except Exception as e:
            print(e)
        self.imageCap.stop()

    def showMainWindow(self, event):
        self.isRecordingStats = True

        self.stopImageSettingsCap()
        self.stopImageCap()

        #left context menu
        self.mainWindow.init_ui(self)
        self.mainWindow.statisticsLabel.mousePressEvent = self.showStatsMenu
        self.mainWindow.settingsLabel.mousePressEvent = self.showSettingsMenu

        #Connecting ui elements
        #image

        self.imageCap.changePixmap.connect(self.setImageCap)

        self.imageCap.callImageCap.connect(self.imageCap.cameraCapture)
        self.imageCap.callImageCap.emit()
        self.imageCap.centerLabels.connect(self.programCam.updateRelativeCenters)

        self.mainWindow.GLabel.mousePressEvent = self.programCamera
        self.mainWindow.resetCamButton.clicked.connect(self.resetCamera)

        #labels
        self.imageCap.centerLabels.connect(self.setLabelData)
        # self.showMinimized()
        # self.setMaximumSize(self.mainWindow.layout.sizeHint())
        # self.setMaximumSize()
        self.showMaximized()
        # self.show()

        # self.releaseHydraulics(None)

    def showStatsMenu(self, event):
        self.stopImageSettingsCap()
        self.stopImageCap()

        self.statsWindow.init_ui(self, self.database.all()[0][self.programCam.currentCameraType])
        self.statsWindow.mainLabel.mousePressEvent = self.showMainWindow
        self.statsWindow.settingsLabel.mousePressEvent = self.showSettingsMenu
        # self.setMaximumSize(self.statsWindow.layout.sizeHint())
        self.showMaximized()

    def updateLabels(self):
        #this is for the settings window only
        self.settingsWindow.roiXLabelvalue.setText(str(self.settingsWindow.roiXSlider.value()))
        self.settingsWindow.roiYLabelvalue.setText(str(self.settingsWindow.roiYSlider.value()))
        self.settingsWindow.roiWLabelvalue.setText(str(self.settingsWindow.roiWSlider.value()))
        self.settingsWindow.roiHLabelvalue.setText(str(self.settingsWindow.roiHSlider.value()))
        self.settingsWindow.centerXLabelValue.setText(str(self.settingsWindow.centerXSlider.value()))
        self.settingsWindow.centerYLabelValue.setText(str(self.settingsWindow.centerYSlider.value()))

        self.settingsImageCap.settings['roi_x'] = self.settingsWindow.roiXSlider.value()
        self.settingsImageCap.settings['roi_y'] = self.settingsWindow.roiYSlider.value()
        self.settingsImageCap.settings['roi_w'] = self.settingsWindow.roiWSlider.value()
        self.settingsImageCap.settings['roi_h'] = self.settingsWindow.roiHSlider.value()
        self.settingsImageCap.settings['camera_true_center_x'] = self.settingsWindow.centerXSlider.value()
        self.settingsImageCap.settings['camera_true_center_y'] = self.settingsWindow.centerYSlider.value()

    def saveSettings(self):
        settingsConfigField = Query()
        self.settingsConfig.upsert({
            'title': 'settingsConfig',
            'roi_x': self.settingsWindow.roiXSlider.value(),
            'roi_y': self.settingsWindow.roiYSlider.value(),
            'roi_w': self.settingsWindow.roiWSlider.value(),
            'roi_h': self.settingsWindow.roiHSlider.value(),
            'camera_width': 640,
            'camera_height': 480,
            'camera_true_center_x': self.settingsWindow.centerXSlider.value(),
            'camera_true_center_y': self.settingsWindow.centerYSlider.value(),
            'currentCameraType': self.settingsWindow.chooseCurrentCamera.currentText(),  # d55l or cp1p
        }, settingsConfigField.title == 'settingsConfig')  # A good alternative is using contains instead

        self.imageCap.roi[0] = self.settingsWindow.roiXSlider.value()
        self.imageCap.roi[1] = self.settingsWindow.roiYSlider.value()
        self.imageCap.roi[2] = self.settingsWindow.roiWSlider.value()
        self.imageCap.roi[3] = self.settingsWindow.roiHSlider.value()

        self.imageCap.screenCenterX = self.settingsWindow.centerXSlider.value()
        self.imageCap.screenCenterY = self.settingsWindow.centerYSlider.value()

        self.programCam.currentCameraType = self.settingsWindow.chooseCurrentCamera.currentText()


    def engageHydraulics(self, param):
        # try:
            #need to check if this causes the program to hang
            # self.programCam.arduinoController.engageHydraulics()
        self.programCam.callEngageHydraulics.emit()
        # except Exception as e:
        #     print(e)

    def releaseHydraulics(self, param):
        # self.programCam.arduinoController.releaseHydraulics()
        self.programCam.callReleaseHydraulics.emit()

    def showSettingsMenu(self, event):
        self.isRecordingStats = False

        self.stopImageCap()
        self.stopImageSettingsCap()
        # settings = self.settingsConfig.all()[0]
        self.isAuthenticated = True

        if not self.isAuthenticated:
            self.loginWindow.init_ui(self)
            self.loginWindow.mainLabel.mousePressEvent = self.showMainWindow
            self.loginWindow.statisticsLabel.mousePressEvent = self.showStatsMenu
            self.loginWindow.loginButton.clicked.connect(self.authenticate)
        else:
            self.initSettingsMenu()

        # self.show()
        self.showMaximized()

    def initSettingsMenu(self):
        settings = self.settingsConfig.all()[0]

        self.settingsWindow.init_ui(self, settings)
        self.settingsWindow.mainLabel.mousePressEvent = self.showMainWindow
        self.settingsWindow.statisticsLabel.mousePressEvent = self.showStatsMenu

        self.settingsImageCap.changePixmap.connect(self.setSettingsImage)
        self.settingsImageCap.call_camera.connect(self.settingsImageCap.debugCameraCapture)
        self.settingsImageCap.call_camera.emit()
        self.settingsImageCap.centerLabels.connect(self.programCam.updateRelativeCenters)

        self.settingsWindow.roiXSlider.valueChanged.connect(self.updateLabels)
        self.settingsWindow.roiYSlider.valueChanged.connect(self.updateLabels)
        self.settingsWindow.roiWSlider.valueChanged.connect(self.updateLabels)
        self.settingsWindow.roiHSlider.valueChanged.connect(self.updateLabels)

        self.settingsWindow.centerXSlider.valueChanged.connect(self.updateLabels)
        self.settingsWindow.centerYSlider.valueChanged.connect(self.updateLabels)

        self.updateLabels()

        self.settingsWindow.saveButton.clicked.connect(self.saveSettings)
        self.settingsWindow.tareButton.clicked.connect(self.tareCenter)

        self.settingsWindow.engageButton.clicked.connect(self.engageHydraulics)
        self.settingsWindow.releaseButton.clicked.connect(self.releaseHydraulics)

    def tareCenter(self, params):
        self.settingsImageCap.settings['camera_true_center_x'] = self.settingsImageCap.absoluteCenters[0][0]
        self.settingsImageCap.settings['camera_true_center_y'] = self.settingsImageCap.absoluteCenters[0][1]
        self.settingsWindow.centerXLabelValue.setText(str(self.settingsImageCap.absoluteCenters[0][0]))
        self.settingsWindow.centerYLabelValue.setText(str(self.settingsImageCap.absoluteCenters[0][1]))
        self.settingsWindow.centerXSlider.setValue(self.settingsImageCap.absoluteCenters[0][0])
        self.settingsWindow.centerYSlider.setValue(self.settingsImageCap.absoluteCenters[0][1])

    def authenticate(self):
        userName = self.loginWindow.userNameTextBox.text()
        password = self.loginWindow.passNameTextBox.text()

        settingsConfigField = Query()

        userDetail = self.settingsConfig.get(settingsConfigField.userTitle == 'userDetail')

        if userName == userDetail['username']:
            print("Correct username")
            if password == userDetail['password']:
                print("correct password")
                # self.isAuthenticated = False
                #Have to get the username and password correct
                self.initSettingsMenu()
                # self.setMaximumSize(1000, 600)
                self.setFixedSize(1000, 600)
                # self.showMaximized()
                self.show()
            else:
                self.loginWindow.helpText.setText("Incorect Password")
        else:
            self.loginWindow.helpText.setText("Incorrect Username")

if __name__ == "__main__":

    db = TinyDB('database.json')
    # db.purge()
    title = Query()

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)

    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)

    sys._excepthook = sys.excepthook


    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook

    masterWindow = MasterWindow(app)

    sys.exit(app.exec_())