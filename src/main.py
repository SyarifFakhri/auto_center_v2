import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QImage, QPixmap
from tinydb import TinyDB, Query
import time
import math

from centerFinder import CenterFinder
from flashTool import FlashTool
from arduinoController import ArduinoController
from programCamera import ProgramCamera
from mainWindow import MainWindow
from settingsWindow import SettingsWindow
from statisticsWindow import StatisticsWindow
from imageCapture import ImageCaptureThread, DebugImageThread
from loginWindow import LoginWindow

import numpy as np

import cv2

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

        
        self.programCam.arduinoController.bothButtonsPressed.connect(self.programCamera)
        self.programCam.callDoubleProgramCamera.connect(self.programCam.programCenterPointDoubleProgramMethod)
        self.programCam.callProgramCamera.connect(self.programCam.resetCameraOffsets)
        self.programCam.statsData.connect(self.recordStatsInDatabase)
        self.programCam.callEngageHydraulics.connect(self.programCam.engageHydraulics)
        self.programCam.callReleaseHydraulics.connect(self.programCam.releaseHydraulics)
        self.programCam.callSimpleProgramCamera.connect(self.programCam.simpleProgramCamera)

        self.programCam.currentCameraType = self.settingsConfig.all()[0]['currentCameraType']

        self.settingsImageCap = DebugImageThread(picSettings)
        self.settingsThread = QThread()
        self.settingsImageCap.moveToThread(self.settingsThread)
        self.settingsThread.start()

        self.mainWindow = MainWindow()

        self.isAuthenticated = False

        self.setMaximumWidth(1024)
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

    @pyqtSlot()
    def simpleProgramCamera(self):
        self.programCam.callSimpleProgramCamera.emit()

    @pyqtSlot(list)
    def recordStatsInDatabase(self, stats):
        #Stats is an array containing at index 0, success or fail
        #at index 1 the centerpoints
        self.isRecordingStats = True
        print("recording stats callback")
        if self.isRecordingStats:
            print("entering stats recording", stats)
            currentCameraType = self.programCam.currentCameraType
            database = self.database.all()[0][currentCameraType]

            currentGoodSample = database['goodSample']
            currentRejectedSample = database['rejectedSample']
            currentAlignmentStats = database['xyAlignmentStats']
            
            if stats[0] == 'failed':
                self.mainWindow.NGLabel.setStyleSheet("background-color: #eb4034")
                currentRejectedSample += 1

            if stats[0] == 'succeeded':
                self.mainWindow.GLabel.setStyleSheet("background-color: #22c928");
                currentGoodSample += 1

            

            else:
                assert 0, "Error, camera stats not in list"
            print("len stats:", len(stats[1]))
            if len(stats[1]) == 2:
                if len(currentAlignmentStats) < 1000:
                    print("Appending stats")
                    currentAlignmentStats.insert(0,stats[1])
                else:
                    currentAlignmentStats.pop()
                    currentAlignmentStats.insert(0,stats[1])
            print("current alignment stats:",currentAlignmentStats)
            cycleTime = 45

            databaseField = Query()
            self.database.update({
                currentCameraType:{
                    'goodSample':currentGoodSample,
                    'rejectedSample':currentRejectedSample,
                    'xyAlignmentStats':currentAlignmentStats,
                    'averageCyleTime': cycleTime
                }  # d55l or cp1p
            }, databaseField.title == 'cameraStats')  # A good alternative is using contains instead

    @pyqtSlot()
    def programCamera(self):
        self.mainWindow.GLabel.setStyleSheet("background-color: #686868");
        self.mainWindow.NGLabel.setStyleSheet("background-color: #686868")
        self.programCam.callDoubleProgramCamera.emit()

    @pyqtSlot()
    def resetCamera(self):
        self.programCam.callProgramCamera.emit()

    @pyqtSlot(QImage)
    def setImageCap(self,image):
        # print("SET IMAGE")
        self.mainWindow.statusLabel.setText(self.programCam.currentProgrammingStep)
        self.mainWindow.imageLabel.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(QImage)
    def setSettingsImage(self,image):
        # self.imageCap.cameraStatus = self.programCam.currentProgrammingStep
        self.settingsWindow.statusLabel.setText(self.programCam.currentProgrammingStep)
        self.settingsWindow.imageLabel.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(list)
    def setLabelData(self, stringList):
        # print("SET LABEL DATA", stringList)
        if len(stringList) >= 1:
            # self.mainWindow.xCenterLeftLabel.setText("CLX: " + str(stringList[0][0]))
            # self.mainWindow.yCenterleftLabel.setText("CLY: " + str(stringList[0][1]))

            self.mainWindow.xCenterLabel.setText(str(stringList[0][0]))
            self.mainWindow.yCenterLabel.setText(str(stringList[0][1]))

            # self.mainWindow.xCenterRightLabel.setText("CRX: " + str(stringList[2][0]))
            # self.mainWindow.yCenterRightLabel.setText("CRY: " + str(stringList[2][1]))
    @pyqtSlot(list)
    def setSettingsLabelData(self, stringList):
        if len(stringList) >= 1:
            # self.mainWindow.xCenterLeftLabel.setText("CLX: " + str(stringList[0][0]))
            # self.mainWindow.yCenterleftLabel.setText("CLY: " + str(stringList[0][1]))

            self.settingsWindow.xCenterLabel.setText("Center X: " + str(stringList[0][0]))
            self.settingsWindow.yCenterLabel.setText("Center Y: " + str(stringList[0][1]))

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

        # self.mainWindow.GLabel.mousePressEvent = self.programCamera

        #labels
        self.imageCap.centerLabels.connect(self.setLabelData)
        # self.showMinimized()
        # self.setMaximumSize(self.mainWindow.layout.sizeHint())
        # self.setMaximumSize()
        # self.showMaximized()
        self.showFullScreen()
        # self.show()
        # QApplication.processEvents()
        self.releaseHydraulics()

    def showStatsMenu(self, event):
        self.stopImageSettingsCap()
        self.stopImageCap()

        self.statsWindow.init_ui(self, self.database.all()[0][self.programCam.currentCameraType], self.programCam.currentCameraType)
        self.statsWindow.mainLabel.mousePressEvent = self.showMainWindow
        self.statsWindow.settingsLabel.mousePressEvent = self.showSettingsMenu
        # self.setMaximumSize(self.statsWindow.layout.sizeHint())
        # self.showMaximized()
        self.showFullScreen()

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

    def releaseHydraulics(self):
        # self.programCam.arduinoController.releaseHydraulics()
        self.programCam.callReleaseHydraulics.emit()

    def showSettingsMenu(self, event):
        self.isRecordingStats = True

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
        # self.showMaximized()
        self.showFullScreen()

    def initSettingsMenu(self):
        settings = self.settingsConfig.all()[0]

        self.settingsWindow.init_ui(self, settings)
        self.settingsWindow.mainLabel.mousePressEvent = self.showMainWindow
        self.settingsWindow.statisticsLabel.mousePressEvent = self.showStatsMenu

        self.settingsImageCap.changePixmap.connect(self.setSettingsImage)
        self.settingsImageCap.call_camera.connect(self.settingsImageCap.debugCameraCapture)
        self.settingsImageCap.call_camera.emit()
        self.settingsImageCap.centerLabels.connect(self.programCam.updateRelativeCenters)
        self.settingsImageCap.centerLabels.connect(self.setSettingsLabelData)

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

        self.settingsWindow.resetCameraOffsetButton.clicked.connect(self.resetCamera)
        self.settingsWindow.programOffsetButton.clicked.connect(self.simpleProgramCamera)

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
