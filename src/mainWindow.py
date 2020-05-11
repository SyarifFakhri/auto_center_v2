from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect

class MainWindow():
    def init_ui(self, mainWindow):

        self.centers = None

        self.layout = QGridLayout()
        self.layout.setSpacing(10)
        self.layout.setMargin(10)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(5,5,5,5)

        mainTitle = QLabel("Auto Center Tool")
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=18, weight=QtGui.QFont.Bold))
        mainTitle.setContentsMargins(0,0,0,10)

        menuFrame = QFrame()
        # menuFrame.setContentsMargins(0,0,0)
        menuFrame.setContentsMargins(0,0,0,0)
        # menuFrame.setStyleSheet(".QFrame{border-radius: 5px;background-color:#686868;}")

        innerMenuVbox = QVBoxLayout()
        innerMenuVbox.setContentsMargins(5,5,5,5)

        self.mainLabel = QLabel("Main")
        self.mainLabel.setStyleSheet("background-color: #4a4a4a")
        self.mainLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.mainLabel.setContentsMargins(5,5,10,5)

        self.statisticsLabel = QLabel("Statistics")
        self.statisticsLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.statisticsLabel.setContentsMargins(5,5,10,5)

        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.settingsLabel.setContentsMargins(5,5,10,5)

        innerMenuFrame = QFrame()
        innerMenuFrame.setContentsMargins(0,0,0,0)

        innerMenuVbox.addWidget(self.mainLabel)
        innerMenuVbox.addWidget(self.statisticsLabel)
        innerMenuVbox.addWidget(self.settingsLabel)
        # innerMenuVbox.addStretch(1)

        innerMenuFrame.setLayout(innerMenuVbox)
        innerMenuFrame.setStyleSheet("background-color:#373737;border-radius: 5px;")

        vbox.addWidget(mainTitle)
        vbox.addWidget(innerMenuFrame)
        vbox.addStretch(1)

        menuFrame.setLayout(vbox)

        centerVBox = QVBoxLayout()

        self.imageLabel = QLabel(mainWindow)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.statusLabel = QLabel("Machine Idle")
        self.statusLabel.setStyleSheet("background-color:#686868;border-radius: 5px")
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
        #rightVBox.setContentsMargins(5,5,5,5)

        xCenterTitle, self.xCenterLabel = self.infoWidget("Center X")
        yCenterTitle, self.yCenterLabel = self.infoWidget("Center Y")

        # line = QtGui.QFrame()
        # line.setFrameShape(QtGui.QFrame.HLine)
        # line.setFrameShadow(QtGui.QFrame.Sunken)

        rightVBox.addWidget(xCenterTitle)
        rightVBox.addWidget(yCenterTitle)

        rightVBox.addStretch(10)

        self.layout.addWidget(menuFrame, 0, 0)
        # self.layout.addWidget(menuDivider, 0,1)
        self.layout.addLayout(centerVBox, 0, 1)
        self.layout.addLayout(rightVBox, 0, 2)

        widget = QWidget()
        widget.setLayout(self.layout)
        mainWindow.setCentralWidget(widget)

    def infoWidget(self, title):
        roundedFrame = QFrame()
        roundedFrame.setStyleSheet(".QFrame{border-radius: 5px;background-color:#686868;}")
        roundedFrame.setContentsMargins(0,0,0,0)

        vBox = QVBoxLayout()
        # vBox.setSpacing(10)
        vBox.setContentsMargins(5,5,5,5)

        titleBox = QLabel(title)
        # titleBox.setStyleSheet("background-color:#1f1f1f;")
        # titleBox.setAlignment(Qt.AlignCenter)
        titleBox.setFont(QtGui.QFont("Lato", pointSize=20))
        titleBox.setContentsMargins(0,0,10,0)

        labelText = QLabel("0")
        labelText.setFont(QtGui.QFont("Lato", pointSize=20))
        labelText.setAlignment(Qt.AlignCenter)
        labelText.setStyleSheet("background-color:#373737;border-radius: 5px;color:#2AA1D3")
        labelText.setContentsMargins(10,10,10,10)
        vBox.addWidget(titleBox)
        vBox.addWidget(labelText)

        roundedFrame.setLayout(vBox)

        return roundedFrame, labelText


