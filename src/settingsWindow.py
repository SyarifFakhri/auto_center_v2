from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect

class SettingsWindow():
    def init_ui(self, mainWindow, settings):
        layout = QGridLayout()
        layout.setSpacing(20)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)

        mainTitle = QLabel("Auto Center Tool")
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        self.mainLabel = QLabel("Main")
        self.mainLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.statisticsLabel = QLabel("Statistics")
        self.statisticsLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.settingsLabel.setStyleSheet("background-color: #4a4a4a")

        vbox.addWidget(mainTitle)
        vbox.addWidget(self.mainLabel)
        vbox.addWidget(self.statisticsLabel)
        vbox.addWidget(self.settingsLabel)
        vbox.addStretch(1)

        self.imageLabel = QLabel(mainWindow)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        # scroll.setEnabled(True)
        # scroll.setMaximumHeight(200)
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
        self.resetCameraOffsetButton = QPushButton("Reset Camera Offset")
        self.programOffsetButton = QPushButton("Program Center")
        self.tareButton = QPushButton("Tare Center")
        buttonLayout,self.saveButton = self.bottomAlignedButton("Save Settings")
        # self.saveButton.setAlignment(Qt.AlignCenter)

        self.chooseCurrentCamera = QtGui.QComboBox()
        self.chooseCurrentCamera.addItem(settings['currentCameraType'])

        self.chooseCurrentCamera.addItem("d55l")
        self.chooseCurrentCamera.addItem("cp1p")

        self.statusLabel = QLabel("Machine Idle")
        self.statusLabel.setAlignment(Qt.AlignRight)

        self.xCenterLabel = QLabel("Center X: 0")
        self.xCenterLabel.setAlignment(Qt.AlignRight)
        self.yCenterLabel = QLabel("Center Y: 0")
        self.yCenterLabel.setAlignment(Qt.AlignRight)
        # rightVBox.addStretch(1)
        # rightVBox.addWidget(xCenterLabel)
        # rightVBox.addWidget(yCenterLabel)
        # rightVBox.addStretch(10)

        rightVBox.addWidget(manualControlLabel)
        rightVBox.addWidget(self.releaseButton)
        rightVBox.addWidget(self.engageButton)
        rightVBox.addWidget(self.resetCameraOffsetButton)
        rightVBox.addWidget(self.programOffsetButton)
        rightVBox.addWidget(self.tareButton)
        rightVBox.addWidget(self.chooseCurrentCamera)
        rightVBox.addWidget(self.statusLabel)
        rightVBox.addWidget(self.xCenterLabel)
        rightVBox.addWidget(self.yCenterLabel)
        rightVBox.addStretch(1)
        # rightVBox.addWidget(self.saveButton)
        # rightVBox.addLayout(buttonLayout)

        widget = QWidget()
        widget.setLayout(gridSettings)
        scroll.setWidget(widget)

        layout.addLayout(vbox, 0, 0)
        layout.addLayout(rightVBox, 0, 2)
        layout.addWidget(self.imageLabel, 0, 1)
        # layout.addLayout(gridSettings, 1,1)
        layout.addWidget(scroll, 1, 1)
        # layout.addWidget(self.saveButton, 1,2)
        layout.addLayout(buttonLayout, 1,2)


        widget = QWidget()
        widget.setLayout(layout)
        mainWindow.setCentralWidget(widget)

    def bottomAlignedButton(self, buttonText):
        hbox = QVBoxLayout()
        pushButton = QPushButton(buttonText)
        hbox.addStretch(1)
        hbox.addWidget(pushButton)
        return hbox, pushButton