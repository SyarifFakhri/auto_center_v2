from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
import pyqtgraph as pg
import windowStyling

class StatisticsWindow():
    def init_ui(self, mainWindow, database, currentCameraType):
        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(10)
        mainLayout.setContentsMargins(10, 10, 10, 10)

        menuFrame = QFrame()
        menuFrame.setContentsMargins(0, 0, 0, 0)
        # menuFrame.setStyleSheet("background-color: #4a4a4a")

        mainMenuTitleLayout = QVBoxLayout()
        mainLayout.addLayout(mainMenuTitleLayout)

        mainTitle = QLabel('Auto Center System')
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuTitleSize, weight=QtGui.QFont.Bold))
        mainTitle.setAlignment(Qt.AlignCenter)
        mainMenuTitleLayout.addWidget(mainTitle)

        menuLayout = QHBoxLayout()
        menuLayout.setSpacing(20)
        menuLayout.setContentsMargins(15, 15, 25, 15)  # LTRB
        mainMenuTitleLayout.addLayout(menuLayout)

        self.mainLabel = QLabel("Main")
        # self.mainLabel.setStyleSheet("background-color: #4a4a4a; border-radius: 5px")
        self.mainLabel.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuFontSize))
        self.mainLabel.setAlignment(Qt.AlignCenter)
        # self.mainLabel.setContentsMargins(15, 10, 15, 10)  # LTRB
        menuLayout.addWidget(self.mainLabel)

        self.statisticsLabel = QLabel("Statistics")
        self.statisticsLabel.setStyleSheet("background-color: #4a4a4a; border-radius: 5px")
        self.statisticsLabel.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuFontSize))
        self.statisticsLabel.setContentsMargins(15,10,15,10)
        self.statisticsLabel.setAlignment(Qt.AlignCenter)
        menuLayout.addWidget(self.statisticsLabel)

        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuFontSize))
        # self.settingsLabel.setContentsMargins(15,15,15,15)
        self.settingsLabel.setAlignment(Qt.AlignCenter)
        menuLayout.addWidget(self.settingsLabel)

        vCharts = QVBoxLayout()

        statisticsTitle = QLabel("Lifetime Statistics for Camera " + str(currentCameraType.upper()))
        statisticsTitle.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        accepted = database['goodSample']
        rejected = database['rejectedSample']

        totalCameraLabel = QLabel("Total cameras Programmed: " + str(accepted + rejected))
        totalCameraLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        
        acceptedCameraLabel = QLabel("Accepted: " + str(accepted))
        acceptedCameraLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        
        rejectedCameraLabel = QLabel("Rejected: " + str(rejected))
        rejectedCameraLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        
        averageCycleTimeLabel = QLabel("Average Cycle Time: " + str(round(database['averageCycleTime'],2)) + " seconds")
        averageCycleTimeLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        
        xyAlignment = self.xyAlignmentStats(database['xyAlignmentStats'])

        vCharts.addWidget(statisticsTitle)
        vCharts.addWidget(totalCameraLabel)
        vCharts.addWidget(acceptedCameraLabel)
        vCharts.addWidget(rejectedCameraLabel)
        vCharts.addWidget(averageCycleTimeLabel)
        vCharts.addWidget(xyAlignment)

        # add scroll
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        # scroll.setEnabled(True)
        scroll.setMinimumHeight(400)
        scroll.setMinimumWidth(750)
        widget = QWidget()
        widget.setLayout(vCharts)
        scroll.setWidget(widget)

        mainLayout.addWidget(scroll)

        #FINAL QT LINE
        widget = QWidget()
        widget.setLayout(mainLayout)
        mainWindow.setCentralWidget(widget)

    def xyAlignmentStats(self,xyAlignmentStats):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(x=False, y=False)
        plot.setMinimumHeight(480)
        plot.setMinimumWidth(640)
        plot.setBackground('#353535')
        plot.setTitle('XY Alignment Distribution', size='20pt')
        plot.setXRange(-50,50)
        plot.setYRange(-50,50)
        

        succeeded, failed = self.parseXYAlignmentStats(xyAlignmentStats)

        failedX = [item[0] for item in failed]
        failedY = [item[1] for item in failed]

        succeededX = [item[0] for item in succeeded]
        succeededY = [item[1] for item in succeeded]
        
        pen = pg.mkPen(color=(0,255,0))
        successScatterPlot= pg.ScatterPlotItem(pen=pen, symbol='+') #size=10, pen=pen, symbol='O',  brush=pg.mkBrush(255, 255, 255, 120)
        successScatterPlot.addPoints(succeededX, succeededY)

        pen = pg.mkPen(color=(255, 0, 0))
        failedScatterPlot = pg.ScatterPlotItem(pen=pen, symbol='x')
        failedScatterPlot.addPoints(failedX, failedY)

        plot.addItem(successScatterPlot)
        plot.addItem(failedScatterPlot)

        return plot

    def parseXYAlignmentStats(self, xyAlignmentStats):
        succeeded = []
        failed = []
        for dataPoint in xyAlignmentStats:
            if dataPoint[2] == 'succeeded':
                succeeded.append([dataPoint[0], dataPoint[1]])
            elif dataPoint[2] == 'failed':
                failed.append([dataPoint[0], dataPoint[1]])
            else:
                assert 0, "Data point must be 'succeeded' or 'failed', is: " + dataPoint[2]
        print("Succceeded:", succeeded)
        print("Failed:", failed)
        return succeeded, failed


