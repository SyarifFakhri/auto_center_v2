from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect

class MainWindow():
    def init_ui(self, mainWindow):

        self.centers = None

        self.layout = QGridLayout()
        # self.layout.setSpacing(20)
        # self.layout.setMargin(0)

        menuDivider = QFrame()
        menuDivider.setFrameShape(QtGui.QFrame.VLine)
        # menuDivider.setStyleSheet("border: 2px solid #1f1f1f")
        menuDivider.setFrameShadow(QtGui.QFrame.Sunken)

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

        # menuFrame.setLayout(vbox)

        centerVBox = QVBoxLayout()

        self.imageLabel = QLabel(mainWindow)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.statusLabel = QLabel("Machine Idle")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        hbox = QHBoxLayout()

        self.GLabel = QLabel("G")
        self.GLabel.setStyleSheet("background-color: #22c928");
        self.GLabel.setAlignment(Qt.AlignCenter)
        self.GLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        NGLabel = QLabel("NG")
        NGLabel.setStyleSheet("background-color: #eb4034")
        NGLabel.setAlignment(Qt.AlignCenter)
        NGLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        hbox.addWidget(self.GLabel)
        hbox.addWidget(NGLabel)

        centerVBox.addWidget(self.imageLabel)
        centerVBox.addWidget(self.statusLabel)
        centerVBox.addLayout(hbox)

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

        # self.resetCamButton = QPushButton('Reset camera Offset')

        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)

        # rightVBox.addStretch(1)
        # rightVBox.addWidget(self.xCenterLeftLabel)
        # rightVBox.addWidget(self.yCenterleftLabel)
        rightVBox.addWidget(self.xCenterLabel)
        rightVBox.addWidget(self.yCenterLabel)
        # rightVBox.addWidget(self.xCenterRightLabel)
        # rightVBox.addWidget(self.yCenterRightLabel)
        rightVBox.addWidget(line)

        # rightVBox.addWidget(self.resetCamButton)

        rightVBox.addStretch(10)

        self.layout.addLayout(vbox, 0, 0)
        # self.layout.addWidget(menuDivider, 0,1)
        self.layout.addLayout(centerVBox, 0, 1)
        self.layout.addLayout(rightVBox, 0, 2)

        widget = QWidget()
        widget.setLayout(self.layout)
        mainWindow.setCentralWidget(widget)