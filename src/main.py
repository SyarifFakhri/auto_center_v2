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

import pyqtgraph as pg
import numpy as np

import cv2

class ProgramCamera(QtCore.QObject):
    callProgramCamera = pyqtSignal(list)

    @pyqtSlot(list)
    def programCenterPointDoubleProgramMethod(self, centers):
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

        # if self.validImage == False:
        #     print("Invalid image")
        print('start')
        relativeCenterPoints = centers

        # pass the center centerpoint
        centerPoints = relativeCenterPoints[1]  # 0: left center point, 1: center center point, 2: right center point

        # check if it's already center
        # if not self.isCenterPointValid(centerPoints):
        #     print("Already center! No point in centering.")
        #     return

        # self.stopRunning = True #temporarily pause the camera

        programX = -centerPoints[0]
        programY = -centerPoints[1]

        # programX = 0
        # programY = 0

        print("Value to Program X: " + str(programX))
        print("Value to Program Y: " + str(programY))

        # self.flashTool.alterCFGFileCameraOffset(programX, programY)
        # self.flashTool.createBinFileCmd()
        # self.flashTool.flashCameraCmd()

        # QThread.sleep(10) #sleep an amount of time
        # time.sleep(10)
        print("Finished programming.")

        # self.cameraCapture()

        #
        # relativeCenterPoints = self.getRelativeCenterPoints()
        #
        # centerPoints = relativeCenterPoints[1] #0: left center point, 1: center center point, 2: right center point
        #
        # programX = programX + centerPoints[0]
        # programY = programY + centerPoints[1]
        #
        # # self.flashTool.alterCFGFileCameraOffset(programX, programY)
        # # self.flashTool.createBinFileCmd()
        # # self.flashTool.flashCameraCmd()
        # print(self.centers)
        # time.sleep(1) #sleep just in case


class ImageCaptureThread(QtCore.QObject):
    changePixmap = pyqtSignal(QImage)
    centerLabels = pyqtSignal(list)
    callImageCap = pyqtSignal()

    def __init__(self, settingsConfig):
        super(ImageCaptureThread, self).__init__()
        # self.screenCenterX = int(640/2)
        # self.screenCenterY = int(480/2)
        self.screenCenterX = 342
        self.screenCenterY = 274

        self.centerFinder = CenterFinder()
        self.centers = []
        self.validImage = False

        self.roi = [settingsConfig['roi_x'],
                    settingsConfig['roi_y'],
                    settingsConfig['roi_w'],
                    settingsConfig['roi_h']
                    ] #x,w,y,h - right roi

    @pyqtSlot()
    def cameraCapture(self):
        try:
            # time.sleep(10)
            self.stopRunning = False
            self.isRunning = True
            cap = cv2.VideoCapture(1)
            cap.set(cv2.CAP_FFMPEG, True)
            cap.set(cv2.CAP_PROP_FPS, 30)
            while not self.stopRunning:
                ret, frame = cap.read()

                if ret:
                    # print("Get image")
                    self.validImage = self.isValidImage(frame)

                    # self.centers = []
                    #find the center
                    # for roi in self.rois:
                    roi, centers = self.centerFinder.findCentersOfCircles(frame,self.roi)

                    #should only return one center
                    # centers = centers[0]
                    self.centers = centers
                    self.centers = self.getRelativeCenterPoints()

                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # rgbImage = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                    self.centerLabels.emit(self.centers)
                    # print("Done emitting")

            cap.release()
            print("Release camera")
            self.isRunning = False
        except Exception as e:
            print("Error at main thread")
            print(e)

    def isValidImage(self, image):
        #Check if the image is too dark
        average = np.mean(image)
        if average < 50:
            return False
        return True

    def isCenterPointValid(self, centerPoints):
        """Check if the RELATIVE center points are valid"""
        if abs(centerPoints[0]) < 3:
            if abs(centerPoints[1]) < 3:
                return True
        return False

    def getRelativeCenterPoints(self):
        relativeCenterPoints = []
        # First get the position relative to the center
        for center in self.centers:
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

    def __init__(self, settings):
        super(DebugImageThread, self).__init__()
        self.settings = settings

    @pyqtSlot()
    def debugCameraCapture(self):
        self.stopRunning = False
        cap = cv2.VideoCapture(1)
        while not self.stopRunning:
            ret, frame = cap.read()
            if ret:
                x = self.settings['roi_x']
                y = self.settings['roi_y']
                w = self.settings['roi_w']
                h = self.settings['roi_h']
                cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0),2)
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

        cap.release()

    def stop(self):
        self.stopRunning = True
        # self.terminate()

class StatisticsWindow():
    def init_ui(self, mainWindow):
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

        totalAccepted = self.totalAcceptedChart()
        xAlignment = self.xAlignmentStats()
        yAlignment = self.yAlignmentStats()
        xyAlignment = self.xyAlignmentStats()


        vCharts.addWidget(totalAccepted)
        vCharts.addWidget(xAlignment)
        vCharts.addWidget(yAlignment)
        vCharts.addWidget(xyAlignment)

        #add scroll
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        # scroll.setEnabled(True)
        scroll.setMinimumHeight(500)
        widget = QWidget()
        widget.setLayout(vCharts)
        scroll.setWidget(widget)

        self.layout.addLayout(vbox, 0, 0)
        # layout.addWidget(totalAccepted, 0, 1)
        self.layout.addWidget(scroll, 0,1)

        widget = QWidget()
        widget.setLayout(self.layout)
        mainWindow.setCentralWidget(widget)

    def totalAcceptedChart(self):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(x=False, y=False)
        plot.setMinimumHeight(200)
        # plot.setMinimumWidth(640)
        plot.setBackground('w')
        plot.setTitle('G vs NG plot', size='20pt')

        pen = pg.mkPen(color=(255,0,0))
        y1 = np.linspace(0,20, num=2)
        x = np.arange(2)
        barGraph = pg.BarGraphItem(x=x, height=y1, width = 0.5, brush='r', pen=pen)

        plot.addItem(barGraph)
        return plot

    def xAlignmentStats(self):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(x=False, y=False)
        plot.setMinimumHeight(200)
        plot.setBackground('w')
        plot.setTitle('X alignment', size='20pt')

        pen = pg.mkPen(color=(209,0,59))
        y1 = np.linspace(0,20, num=2)
        x = np.arange(2)
        barGraph = pg.BarGraphItem(x=x, height=y1, width = 0.5, brush='#d1003b', pen=pen)

        plot.addItem(barGraph)
        return plot

    def yAlignmentStats(self):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(x=False, y=False)
        plot.setMinimumHeight(200)
        plot.setBackground('w')
        plot.setTitle('Y alignment', size='20pt')

        pen = pg.mkPen(color=(255,0,0))
        y1 = np.linspace(0,20, num=2)
        x = np.arange(2)
        barGraph = pg.BarGraphItem(x=x, height=y1, width = 0.5, brush='r', pen=pen)

        plot.addItem(barGraph)
        return plot

    def xyAlignmentStats(self):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(x=False, y=False)
        plot.setMinimumHeight(200)
        plot.setBackground('w')
        plot.setTitle('XY alignment', size='20pt')

        pen = pg.mkPen(color=(255,0,0))
        y1 = np.linspace(0,20, num=2)
        x = np.arange(2)
        barGraph = pg.BarGraphItem(x=x, height=y1, width = 0.5, brush='r', pen=pen)

        plot.addItem(barGraph)
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

        gridSettings = QGridLayout()
        roiXLabel = QLabel("ROI X: ")
        roiYLabel = QLabel("ROI Y: ")
        roiWLabel = QLabel("ROI W: ")
        roiHLabel = QLabel("ROI H: ")

        self.roiXLabelvalue = QLabel(str(settings['roi_x']))
        self.roiYLabelvalue = QLabel(str(settings['roi_y']))
        self.roiWLabelvalue = QLabel(str(settings['roi_w']))
        self.roiHLabelvalue = QLabel(str(settings['roi_h']))

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

        self.saveButton = QPushButton('Save Settings')

        gridSettings.addWidget(roiXLabel, 0, 0)
        gridSettings.addWidget(roiYLabel, 1, 0)
        gridSettings.addWidget(roiWLabel, 2, 0)
        gridSettings.addWidget(roiHLabel, 3, 0)

        gridSettings.addWidget(self.roiXSlider, 0,1)
        gridSettings.addWidget(self.roiYSlider, 1,1)
        gridSettings.addWidget(self.roiWSlider, 2,1)
        gridSettings.addWidget(self.roiHSlider, 3,1)

        gridSettings.addWidget(self.roiXLabelvalue, 0, 2)
        gridSettings.addWidget(self.roiYLabelvalue, 1, 2)
        gridSettings.addWidget(self.roiWLabelvalue, 2, 2)
        gridSettings.addWidget(self.roiHLabelvalue, 3, 2)

        gridSettings.addWidget(self.saveButton, 4,1)

        rightVBox = QVBoxLayout()
        rightVBox.setSpacing(10)


        xCenterLabel = QLabel('X:   0   ')
        xCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        yCenterLabel = QLabel('Y:   0   ')
        yCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        manualControlLabel = QLabel("Manual Control")
        manualControlLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        self.releaseButton = QPushButton("Release Hydraulics")
        self.engageButton = QPushButton("Engage Hydraulics")
        self.programOffsetButton = QPushButton("Manual Program")

        rightVBox.addStretch(1)
        rightVBox.addWidget(xCenterLabel)
        rightVBox.addWidget(yCenterLabel)
        rightVBox.addStretch(10)

        rightVBox.addWidget(manualControlLabel)
        rightVBox.addWidget(self.releaseButton)
        rightVBox.addWidget(self.engageButton)
        rightVBox.addWidget(self.programOffsetButton)

        layout.addLayout(vbox, 0, 0)
        layout.addLayout(rightVBox, 0, 2)
        layout.addWidget(self.imageLabel, 0, 1)
        layout.addLayout(gridSettings, 1,1)

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
        self.statisticsLabel = QLabel("Statistics")
        self.settingsLabel = QLabel("Settings")

        vbox.addWidget(mainTitle)
        vbox.addWidget(self.mainLabel)
        vbox.addWidget(self.statisticsLabel)
        vbox.addWidget(self.settingsLabel)
        vbox.addStretch(1)

        self.imageLabel = QLabel(mainWindow)

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

        self.xCenterLabel = QLabel('CCX:   0   ')
        self.xCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        self.yCenterLabel = QLabel('CCY:   0   ')
        self.yCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        self.xCenterLeftLabel = QLabel('CLX:   0   ')
        self.xCenterLeftLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        self.yCenterleftLabel = QLabel('CLY:   0   ')
        self.yCenterleftLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        self.xCenterRightLabel = QLabel('CRX:   0   ')
        self.xCenterRightLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        self.yCenterRightLabel = QLabel('CRY:   0   ')
        self.yCenterRightLabel.setFont(QtGui.QFont("Lato", pointSize=20))

        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)

        rightVBox.addStretch(1)
        rightVBox.addWidget(self.xCenterLeftLabel)
        rightVBox.addWidget(self.yCenterleftLabel)
        rightVBox.addWidget(self.xCenterLabel)
        rightVBox.addWidget(self.yCenterLabel)
        rightVBox.addWidget(self.xCenterRightLabel)
        rightVBox.addWidget(self.yCenterRightLabel)
        rightVBox.addWidget(line)

        rightVBox.addStretch(10)

        self.layout.addLayout(vbox, 0, 0)
        self.layout.addLayout(hbox, 1, 1)
        self.layout.addLayout(rightVBox, 0, 2)
        self.layout.addWidget(self.imageLabel, 0, 1)

        widget = QWidget()
        widget.setLayout(self.layout)
        mainWindow.setCentralWidget(widget)

class MasterWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MasterWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Auto Center Tool")
        self.flashTool = FlashTool()

        self.statsWindow = StatisticsWindow()
        self.settingsWindow = SettingsWindow()
        self.loginWindow = LoginWindow()

        # self.showStatsMenu(None)

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
            }, settingsConfigField.title == 'settingsConfig') #A good alternative is using contains instead

        if not self.settingsConfig.search(settingsConfigField.userTitle.exists()):
            self.settingsConfig.upsert({
                'userTitle': 'userDetail',
                'username': 'admin',
                'password': 'admin',
            }, settingsConfigField.userTitle == 'userDetail')  # A good alternative is using contains instead

        picSettings = self.settingsConfig.get(settingsConfigField.title == 'settingsConfig')

        self.capThread = QThread()
        self.capThread.start()
        self.imageCap = ImageCaptureThread(settingsConfig=picSettings)
        self.imageCap.moveToThread(self.capThread)

        self.programCam = ProgramCamera()
        self.programThread = QThread()
        self.programCam.moveToThread(self.programThread)
        self.programThread.start()

        self.settingsImageCap = DebugImageThread(picSettings)
        self.settingsThread = QThread()
        self.settingsImageCap.moveToThread(self.settingsThread)
        self.settingsThread.start()

        self.mainWindow = MainWindow()

        self.isAuthenticated = False

        self.showMainWindow(None)

    def programCamera(self, param):
        self.programCam.callProgramCamera.emit()

    @pyqtSlot(QImage)
    def setImageCap(self,image):
        self.mainWindow.imageLabel.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(QImage)
    def setSettingsImage(self,image):
        self.settingsWindow.imageLabel.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(list)
    def setLabelData(self, stringList):
        self.centers = stringList

        if len(stringList) >= 3:
            self.mainWindow.xCenterLeftLabel.setText("CLX: " + str(stringList[0][0]))
            self.mainWindow.yCenterleftLabel.setText("CLY: " + str(stringList[0][1]))

            self.mainWindow.xCenterLabel.setText("CCX: " + str(stringList[1][0]))
            self.mainWindow.yCenterLabel.setText("CCY: " + str(stringList[1][1]))

            self.mainWindow.xCenterRightLabel.setText("CRX: " + str(stringList[2][0]))
            self.mainWindow.yCenterRightLabel.setText("CRY: " + str(stringList[2][1]))

    def stopImageSettingsCap(self):
        try:
            self.settingsImageCap.changePixmap.disconnect()
        except Exception as e:
            print(e)

        self.settingsImageCap.stop()

    def stopImageCap(self):
        try:
            self.imageCap.changePixmap.disconnect()
        except Exception as e:
            print(e)
        self.imageCap.stop()

    def showMainWindow(self, event):
        # self.stopImageSettingsCap()
        # self.stopImageCap()

        #left context menu
        self.mainWindow.init_ui(self)
        self.mainWindow.statisticsLabel.mousePressEvent = self.showStatsMenu
        self.mainWindow.settingsLabel.mousePressEvent = self.showSettingsMenu

        #Connecting ui elements
        #image

        self.imageCap.changePixmap.connect(self.setImageCap)

        self.imageCap.callImageCap.connect(self.imageCap.cameraCapture)
        self.imageCap.callImageCap.emit()

        self.programCam.callProgramCamera.connect(self.programCam.programCenterPointDoubleProgramMethod)
        self.mainWindow.GLabel.mousePressEvent = self.programCamera

        #labels
        self.imageCap.centerLabels.connect(self.setLabelData)
        # self.showMinimized()
        self.setMaximumSize(self.mainWindow.layout.sizeHint())
        # self.showMaximized()
        self.show()

    def showStatsMenu(self, event):
        self.stopImageCap()
        self.stopImageSettingsCap()

        self.statsWindow.init_ui(self)
        self.statsWindow.mainLabel.mousePressEvent = self.showMainWindow
        self.statsWindow.settingsLabel.mousePressEvent = self.showSettingsMenu
        self.setMaximumSize(self.statsWindow.layout.sizeHint())
        self.show()

    def updateLabels(self):
        self.settingsWindow.roiXLabelvalue.setText(str(self.settingsWindow.roiXSlider.value()))
        self.settingsWindow.roiYLabelvalue.setText(str(self.settingsWindow.roiYSlider.value()))
        self.settingsWindow.roiWLabelvalue.setText(str(self.settingsWindow.roiWSlider.value()))
        self.settingsWindow.roiHLabelvalue.setText(str(self.settingsWindow.roiHSlider.value()))

        self.settingsImageCap.settings['roi_x'] = self.settingsWindow.roiXSlider.value()
        self.settingsImageCap.settings['roi_y'] = self.settingsWindow.roiYSlider.value()
        self.settingsImageCap.settings['roi_w'] = self.settingsWindow.roiWSlider.value()
        self.settingsImageCap.settings['roi_h'] = self.settingsWindow.roiHSlider.value()

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
            'camera_true_center_x': 640 / 2,
            'camera_true_center_y': 480 / 2,
        }, settingsConfigField.title == 'settingsConfig')  # A good alternative is using contains instead

        self.imageCap.roi[0] = self.settingsWindow.roiXSlider.value()
        self.imageCap.roi[1] = self.settingsWindow.roiYSlider.value()
        self.imageCap.roi[2] = self.settingsWindow.roiWSlider.value()
        self.imageCap.roi[3] = self.settingsWindow.roiHSlider.value()

    def showSettingsMenu(self, event):
        self.stopImageCap()
        self.stopImageSettingsCap()
        settings = self.settingsConfig.all()[0]
        self.isAuthenticated = True

        if not self.isAuthenticated:
            self.loginWindow.init_ui(self)
            self.loginWindow.mainLabel.mousePressEvent = self.showMainWindow
            self.loginWindow.statisticsLabel.mousePressEvent = self.showStatsMenu
            self.loginWindow.loginButton.clicked.connect(self.authenticate)
        else:
            self.initSettingsMenu()

        self.show()


    def initSettingsMenu(self):
        settings = self.settingsConfig.all()[0]

        self.settingsWindow.init_ui(self, settings)
        self.settingsWindow.mainLabel.mousePressEvent = self.showMainWindow
        self.settingsWindow.statisticsLabel.mousePressEvent = self.showStatsMenu

        self.settingsImageCap.changePixmap.connect(self.setSettingsImage)
        self.settingsImageCap.call_camera.connect(self.settingsImageCap.debugCameraCapture)
        self.settingsImageCap.call_camera.emit()

        self.settingsWindow.roiXSlider.valueChanged.connect(self.updateLabels)
        self.settingsWindow.roiYSlider.valueChanged.connect(self.updateLabels)
        self.settingsWindow.roiWSlider.valueChanged.connect(self.updateLabels)
        self.settingsWindow.roiHSlider.valueChanged.connect(self.updateLabels)

        self.updateLabels()

        self.settingsWindow.saveButton.clicked.connect(self.saveSettings)


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
                self.show()
            else:
                self.loginWindow.helpText.setText("Incorect Password")
        else:
            self.loginWindow.helpText.setText("Incorrect Username")

if __name__ == "__main__":

    db = TinyDB('database.json')
    # db.purge()
    title = Query()
    db.upsert({'title':'goodvsNotGoodStats','goodSample':5, 'badSample':6}, title.title == 'goodvsNotGoodStats')

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

    masterWindow = MasterWindow()

    sys.exit(app.exec_())