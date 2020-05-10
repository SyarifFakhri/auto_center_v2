from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
import pyqtgraph as pg

class StatisticsWindow():
    def init_ui(self, mainWindow, database, currentCameraType):
        self.layout = QGridLayout()
        self.layout.setSpacing(20)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)

        mainTitle = QLabel("Auto Center Tool")
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=20, weight=QtGui.QFont.Bold))

        self.mainLabel = QLabel("Main")
        self.mainLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.statisticsLabel = QLabel("Statistics")
        self.statisticsLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.statisticsLabel.setStyleSheet("background-color: #4a4a4a")
        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setFont(QtGui.QFont("Lato", pointSize=10))

        vbox.addWidget(mainTitle)
        vbox.addWidget(self.mainLabel)
        vbox.addWidget(self.statisticsLabel)
        vbox.addWidget(self.settingsLabel)
        vbox.addStretch(1)

        vCharts = QVBoxLayout()

        statisticsTitle = QLabel("Lifetime Statistics for Camera " + str(currentCameraType.upper()))
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