from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
import windowStyling

class MainWindow():
    def init_ui(self, mainWindow):
        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(10)
        mainLayout.setContentsMargins(10,10,10,10)

        menuFrame = QFrame()
        menuFrame.setContentsMargins(0,0,0,0)
        # menuFrame.setStyleSheet("background-color: #4a4a4a")

        mainMenuTitleLayout = QVBoxLayout()
        mainLayout.addLayout(mainMenuTitleLayout)

        mainTitle = QLabel('Camera Auto Center System')
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuTitleSize, weight=QtGui.QFont.Bold))
        mainTitle.setAlignment(Qt.AlignCenter)
        mainMenuTitleLayout.addWidget(mainTitle)

        menuLayout = QHBoxLayout()
        menuLayout.setSpacing(20)
        menuLayout.setContentsMargins(15,15,25,15)    #LTRB
        mainMenuTitleLayout.addLayout(menuLayout)

        self.mainLabel = QLabel("Main")
        self.mainLabel.setStyleSheet("background-color: #4a4a4a; border-radius: 5px")
        self.mainLabel.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuFontSize))
        self.mainLabel.setAlignment(Qt.AlignCenter)
        self.mainLabel.setContentsMargins(15,10,15,10) #LTRB
        menuLayout.addWidget(self.mainLabel)

        self.statisticsLabel = QLabel("Statistics")
        self.statisticsLabel.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuFontSize))
        # self.statisticsLabel.setContentsMargins(15,15,15,15)
        self.statisticsLabel.setAlignment(Qt.AlignCenter)
        menuLayout.addWidget(self.statisticsLabel)

        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuFontSize))
        # self.settingsLabel.setContentsMargins(15,15,15,15)
        self.settingsLabel.setAlignment(Qt.AlignCenter)
        menuLayout.addWidget(self.settingsLabel)


        #CENTER LABELS AND IMAGES
        centerLayout = QHBoxLayout() #Contains the images, as well as x and y labels
        mainLayout.addLayout(centerLayout)

        rawImageLayout = QVBoxLayout()
        self.rawImageLabel = QLabel(mainWindow)
        # self.rawImageLabel.setAlignment(Qt.AlignCenter)
        rawImageLayout.addWidget(self.rawImageLabel)

        rawLabel = QLabel("Raw Image")
        rawLabel.setFont(QtGui.QFont("Lato", pointSize=15))
        rawLabel.setAlignment(Qt.AlignCenter)
        
        rawImageLayout.addWidget(rawLabel )
        
        centerLayout.addLayout(rawImageLayout)

        processedImageLayout = QVBoxLayout()
        self.imageLabel = QLabel(mainWindow)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        processedImageLayout.addWidget(self.imageLabel)

        processedLabel = QLabel("Processed Image")
        processedLabel.setFont(QtGui.QFont("Lato", pointSize=15))
        processedLabel.setAlignment(Qt.AlignCenter)
        processedImageLayout.addWidget(processedLabel)
        
        centerLayout.addLayout(processedImageLayout)

        centerXYLabelLayout = QVBoxLayout()
        centerLayout.addLayout(centerXYLabelLayout)

        xCenterTitle, self.xCenterLabel = self.infoWidget("Center X")
        centerXYLabelLayout.addWidget(xCenterTitle)

        yCenterTitle, self.yCenterLabel = self.infoWidget("Center Y")
        centerXYLabelLayout.addWidget(yCenterTitle)

        mainLayout.addStretch(1)
        

        bottomLayout = QHBoxLayout()
        mainLayout.addLayout(bottomLayout)

        self.NGLabel = QLabel("NG")
        # NGLabel.setStyleSheet("background-color: #eb4034")
        self.NGLabel.setStyleSheet("background-color: #686868; border-radius: 5px")
        self.NGLabel.setAlignment(Qt.AlignCenter)
        self.NGLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))
        bottomLayout.addWidget(self.NGLabel)

        self.GLabel = QLabel("G")
        # self.GLabel.setStyleSheet("background-color: #22c928");
        self.GLabel.setStyleSheet("background-color: #686868; border-radius: 5px");
        self.GLabel.setAlignment(Qt.AlignCenter)
        self.GLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))
        bottomLayout.addWidget(self.GLabel)



        statusTitle, self.statusLabel = self.infoWidget("Machine Status")
        # self.statusLabel.setStyleSheet("background-color:#686868;border-radius: 5px")
        # self.statusLabel.setAlignment(Qt.AlignCenter)
        # self.statusLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))
        bottomLayout.addWidget(statusTitle)

        widget = QWidget()
        widget.setLayout(mainLayout)
        mainWindow.setCentralWidget(widget)


    def init_ui_2(self, mainWindow):

        self.layout = QGridLayout()
        self.layout.setSpacing(10)
        self.layout.setMargin(10)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(5,5,5,5)

        mainTitle = QLabel("Auto Center System")
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=19, weight=QtGui.QFont.Bold))
        mainTitle.setContentsMargins(0,0,0,10)

        menuFrame = QFrame()
        menuFrame.setContentsMargins(0,0,0,0)
        # menuFrame.setStyleSheet(".QFrame{border-radius: 5px;background-color:#686868;}")

        innerMenuVbox = QVBoxLayout()
        #innerMenuVbox.setContentsMargins(5,5,5,5)
        innerMenuVbox.setContentsMargins(0,0,0,0)
        
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
        #innerMenuFrame.setStyleSheet("background-color:#373737;border-radius: 5px;")

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
        #self.GLabel.setStyleSheet("background-color: #22c928");
        self.GLabel.setStyleSheet("background-color: #686868");
        self.GLabel.setAlignment(Qt.AlignCenter)
        self.GLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        self.NGLabel = QLabel("NG")
        #NGLabel.setStyleSheet("background-color: #eb4034")
        self.NGLabel.setStyleSheet("background-color: #686868")
        self.NGLabel.setAlignment(Qt.AlignCenter)
        self.NGLabel.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        hbox.addWidget(self.GLabel)
        hbox.addWidget(self.NGLabel)

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
        titleBox.setAlignment(Qt.AlignCenter)
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


