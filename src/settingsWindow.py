from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame, QCheckBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect

import windowStyling

class SettingsWindow():
	def init_ui(self, mainWindow, settings):

		cameraSetting = settings['currentCameraType']
		aiEnabled = settings['aiEnabled']
		settings = settings[cameraSetting]
		picWidth = 960
		picHeight = 720

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
		self.mainLabel.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuFontSize))
		self.mainLabel.setAlignment(Qt.AlignCenter)
		menuLayout.addWidget(self.mainLabel)

		self.statisticsLabel = QLabel("Statistics")
		self.statisticsLabel.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuFontSize))
		# self.statisticsLabel.setContentsMargins(15,15,15,15)
		self.statisticsLabel.setAlignment(Qt.AlignCenter)
		menuLayout.addWidget(self.statisticsLabel)

		self.settingsLabel = QLabel("Settings")
		self.settingsLabel.setFont(QtGui.QFont("Lato", pointSize=windowStyling.menuFontSize))
		self.settingsLabel.setStyleSheet("background-color: #4a4a4a; border-radius: 5px")
		self.settingsLabel.setContentsMargins(15,10,15,10)
		self.settingsLabel.setAlignment(Qt.AlignCenter)
		menuLayout.addWidget(self.settingsLabel)

		hMainLayout = QHBoxLayout()
		mainLayout.addLayout(hMainLayout)

		leftVBox = QVBoxLayout()
		hMainLayout.addLayout(leftVBox)

		self.imageLabel = QLabel(mainWindow)
		self.imageLabel.setAlignment(Qt.AlignCenter)
		self.imageLabel.setStyleSheet("background-color: black;")
		leftVBox.addWidget(self.imageLabel)

		scroll = self.circleRoiSettings(settings, picWidth, picHeight)
		ai_scroll = self.AIRoiSettings(settings, picWidth, picHeight)

		roiTabs = QtWidgets.QTabWidget()
		roiTabs.addTab(scroll, "Circle ROI")
		roiTabs.addTab(ai_scroll, "AI ROI")

		leftVBox.addWidget(roiTabs)
		# leftVBox.addWidget(scroll)

		rightVBox = QVBoxLayout()
		hMainLayout.addLayout(rightVBox)
		rightVBox.setSpacing(10)

		manualControlLabel = QLabel("Manual Control")
		manualControlLabel.setFont(QtGui.QFont("Lato", pointSize=20))

		self.releaseButton = QPushButton("Release Pneumatics")
		self.releaseButton.setStyleSheet("padding-left: 50px; padding-right: 50px;"
"padding-top: 5px; padding-bottom: 5px;")

		self.engageButton = QPushButton("Engage Pneumatics")
		self.resetCameraOffsetButton = QPushButton("Reset Camera Offset")
		self.programOffsetButton = QPushButton("Program Center")
		self.tareButton = QPushButton("Tare Center")
		self.resetStatistics = QPushButton("Reset Statistics")

		self.chooseCurrentCamera = QtGui.QComboBox()
		self.chooseCurrentCamera.addItem(cameraSetting)

		self.chooseCurrentCamera.addItem("d55l")
		self.chooseCurrentCamera.addItem("cp1p")

		self.overlayOption = QtGui.QComboBox()

		self.overlayOption.addItem(settings['overlayOption'])
		self.overlayOption.addItem("Overlay Enabled")
		self.overlayOption.addItem("Overlay Disabled")

		self.enableAiCheckbox = QtWidgets.QCheckBox("Enable PCB orientation detection")

		if aiEnabled == True:
			self.enableAiCheckbox.setChecked(True)
		else:
			self.enableAiCheckbox.setCheckable(True)

		self.statusLabel = QLabel("Machine Idle")
		self.statusLabel.setFont(QtGui.QFont("Lato", pointSize=15))
		self.statusLabel.setAlignment(Qt.AlignRight)

		self.xCenterLabel = QLabel("Center X: 0")
		self.xCenterLabel.setAlignment(Qt.AlignRight)
		self.xCenterLabel.setFont(QtGui.QFont("Lato", pointSize=15))

		self.yCenterLabel = QLabel("Center Y: 0")
		self.yCenterLabel.setFont(QtGui.QFont("Lato", pointSize=15))
		self.yCenterLabel.setAlignment(Qt.AlignRight)

		self.noteOnImage = QLabel("True image size is: " + str(picWidth) + ", " + str(picHeight))
		self.noteOnImage.wordWrap()

		# rightVBox.addWidget(manualControlLabel)
		rightVBox.addWidget(self.releaseButton)
		rightVBox.addWidget(self.engageButton)
		rightVBox.addWidget(self.resetCameraOffsetButton)
		rightVBox.addWidget(self.programOffsetButton)
		rightVBox.addWidget(self.tareButton)
		rightVBox.addWidget(self.resetStatistics)
		rightVBox.addWidget(self.chooseCurrentCamera)
		rightVBox.addWidget(self.overlayOption)
		rightVBox.addWidget(self.enableAiCheckbox)
		rightVBox.addWidget(self.statusLabel)
		rightVBox.addWidget(self.xCenterLabel)
		rightVBox.addWidget(self.yCenterLabel)
		rightVBox.addWidget(self.noteOnImage)

		self.saveButton = QPushButton("Save Settings")
		rightVBox.addWidget(self.saveButton)

		rightVBox.addStretch(1)

		widget = QWidget()
		widget.setLayout(mainLayout)
		mainWindow.setCentralWidget(widget)

	def AIRoiSettings(self, settings, picWidth, picHeight):
		scroll = QScrollArea()
		scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		scroll.setWidgetResizable(True)
		# scroll.setEnabled(True)
		# scroll.setMaximumHeight(200)
		# scroll.setMinimumWidth(750)

		gridSettings = QGridLayout()

		roiXLabel = QLabel("AI ROI X: ")
		roiYLabel = QLabel("AI ROI Y: ")
		roiWLabel = QLabel("AI ROI W: ")
		roiHLabel = QLabel("AI ROI H: ")

		self.AiRoiXLabelvalue = QLabel(str(settings['ai_roi_x']))
		self.AiRoiYLabelvalue = QLabel(str(settings['ai_roi_y']))
		self.AiRoiWLabelvalue = QLabel(str(settings['ai_roi_w']))
		self.AiRoiHLabelvalue = QLabel(str(settings['ai_roi_h']))

		self.AiRoiXSlider = QSlider(Qt.Horizontal)
		self.AiRoiXSlider.setMaximum(picWidth)
		self.AiRoiXSlider.setValue(settings['ai_roi_x'])

		self.AiRoiYSlider = QSlider(Qt.Horizontal)
		self.AiRoiYSlider.setMaximum(picHeight)
		self.AiRoiYSlider.setValue(settings['ai_roi_y'])

		self.AiRoiWSlider = QSlider(Qt.Horizontal)
		self.AiRoiWSlider.setMaximum(picWidth)
		self.AiRoiWSlider.setValue(settings['ai_roi_w'])

		self.AiRoiHSlider = QSlider(Qt.Horizontal)
		self.AiRoiHSlider.setMaximum(picHeight)
		self.AiRoiHSlider.setValue(settings['ai_roi_h'])

		gridSettings.addWidget(roiXLabel, 0, 0)
		gridSettings.addWidget(roiYLabel, 1, 0)
		gridSettings.addWidget(roiWLabel, 2, 0)
		gridSettings.addWidget(roiHLabel, 3, 0)

		gridSettings.addWidget(self.AiRoiXSlider, 0, 1)
		gridSettings.addWidget(self.AiRoiYSlider, 1, 1)
		gridSettings.addWidget(self.AiRoiWSlider, 2, 1)
		gridSettings.addWidget(self.AiRoiHSlider, 3, 1)

		gridSettings.addWidget(self.AiRoiXLabelvalue, 0, 2)
		gridSettings.addWidget(self.AiRoiYLabelvalue, 1, 2)
		gridSettings.addWidget(self.AiRoiWLabelvalue, 2, 2)
		gridSettings.addWidget(self.AiRoiHLabelvalue, 3, 2)

		widget = QWidget()
		widget.setLayout(gridSettings)
		scroll.setWidget(widget)
		return scroll

	def circleRoiSettings(self, settings, picWidth, picHeight):
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
		self.roiXSlider.setMaximum(picWidth)
		self.roiXSlider.setValue(settings['roi_x'])

		self.roiYSlider = QSlider(Qt.Horizontal)
		self.roiYSlider.setMaximum(picHeight)
		self.roiYSlider.setValue(settings['roi_y'])

		self.roiWSlider = QSlider(Qt.Horizontal)
		self.roiWSlider.setMaximum(picWidth)
		self.roiWSlider.setValue(settings['roi_w'])

		self.roiHSlider = QSlider(Qt.Horizontal)
		self.roiHSlider.setMaximum(picHeight)
		self.roiHSlider.setValue(settings['roi_h'])

		self.centerXSlider = QSlider(Qt.Horizontal)
		self.centerXSlider.setMaximum(picWidth)
		self.centerXSlider.setValue(settings['camera_true_center_x'])

		self.centerYSlider = QSlider(Qt.Horizontal)
		self.centerYSlider.setMaximum(picHeight)
		self.centerYSlider.setValue(settings['camera_true_center_y'])

		gridSettings.addWidget(roiXLabel, 0, 0)
		gridSettings.addWidget(roiYLabel, 1, 0)
		gridSettings.addWidget(roiWLabel, 2, 0)
		gridSettings.addWidget(roiHLabel, 3, 0)
		gridSettings.addWidget(centerXLabel, 4, 0)
		gridSettings.addWidget(centerYLabel, 5, 0)

		gridSettings.addWidget(self.roiXSlider, 0, 1)
		gridSettings.addWidget(self.roiYSlider, 1, 1)
		gridSettings.addWidget(self.roiWSlider, 2, 1)
		gridSettings.addWidget(self.roiHSlider, 3, 1)
		gridSettings.addWidget(self.centerXSlider, 4, 1)
		gridSettings.addWidget(self.centerYSlider, 5, 1)

		gridSettings.addWidget(self.roiXLabelvalue, 0, 2)
		gridSettings.addWidget(self.roiYLabelvalue, 1, 2)
		gridSettings.addWidget(self.roiWLabelvalue, 2, 2)
		gridSettings.addWidget(self.roiHLabelvalue, 3, 2)
		gridSettings.addWidget(self.centerXLabelValue, 4, 2)
		gridSettings.addWidget(self.centerYLabelValue, 5, 2)

		widget = QWidget()
		widget.setLayout(gridSettings)
		scroll.setWidget(widget)
		return scroll


	#
	# def init_ui_2(self, mainWindow, settings):
	#     layout = QGridLayout()
	#     layout.setSpacing(20)
	#
	#     vbox = QVBoxLayout()
	#     vbox.setSpacing(0)
	#     vbox.setContentsMargins(5,5,5,5)
	#
	#     mainTitle = QLabel("Auto Center Tool")
	#     mainTitle.setFont(QtGui.QFont("Lato", pointSize=19, weight=QtGui.QFont.Bold))
	#     mainTitle.setContentsMargins(0,0,0,10)
	#
	#     menuFrame = QFrame()
	#     menuFrame.setContentsMargins(0,0,0,0)
	#     # menuFrame.setStyleSheet(".QFrame{border-radius: 5px;background-color:#686868;}")
	#
	#     innerMenuVbox = QVBoxLayout()
	#     #innerMenuVbox.setContentsMargins(5,5,5,5)
	#     innerMenuVbox.setContentsMargins(0,0,0,0)
	#
	#     self.mainLabel = QLabel("Main")
	#
	#     self.mainLabel.setFont(QtGui.QFont("Lato", pointSize=10))
	#     self.mainLabel.setContentsMargins(5,5,10,5)
	#
	#     self.statisticsLabel = QLabel("Statistics")
	#     self.statisticsLabel.setFont(QtGui.QFont("Lato", pointSize=10))
	#     self.statisticsLabel.setContentsMargins(5,5,10,5)
	#
	#     self.settingsLabel = QLabel("Settings")
	#     self.settingsLabel.setFont(QtGui.QFont("Lato", pointSize=10))
	#     self.settingsLabel.setStyleSheet("background-color: #4a4a4a")
	#     self.settingsLabel.setContentsMargins(5,5,10,5)
	#
	#     innerMenuFrame = QFrame()
	#     innerMenuFrame.setContentsMargins(0,0,0,0)
	#
	#     innerMenuVbox.addWidget(self.mainLabel)
	#     innerMenuVbox.addWidget(self.statisticsLabel)
	#     innerMenuVbox.addWidget(self.settingsLabel)
	#     # innerMenuVbox.addStretch(1)
	#
	#     innerMenuFrame.setLayout(innerMenuVbox)
	#     #innerMenuFrame.setStyleSheet("background-color:#373737;border-radius: 5px;")
	#
	#     vbox.addWidget(mainTitle)
	#     vbox.addWidget(innerMenuFrame)
	#     vbox.addStretch(1)
	#
	#     menuFrame.setLayout(vbox)
	#
	#     self.imageLabel = QLabel(mainWindow)
	#     self.imageLabel.setAlignment(Qt.AlignCenter)
	#
	#     scroll = QScrollArea()
	#     scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
	#     scroll.setWidgetResizable(True)
	#     # scroll.setEnabled(True)
	#     # scroll.setMaximumHeight(200)
	#     # scroll.setMinimumWidth(750)
	#
	#     gridSettings = QGridLayout()
	#     roiXLabel = QLabel("ROI X: ")
	#     roiYLabel = QLabel("ROI Y: ")
	#     roiWLabel = QLabel("ROI W: ")
	#     roiHLabel = QLabel("ROI H: ")
	#     centerXLabel = QLabel("X Center: ")
	#     centerYLabel = QLabel("Y Center: ")
	#
	#     self.roiXLabelvalue = QLabel(str(settings['roi_x']))
	#     self.roiYLabelvalue = QLabel(str(settings['roi_y']))
	#     self.roiWLabelvalue = QLabel(str(settings['roi_w']))
	#     self.roiHLabelvalue = QLabel(str(settings['roi_h']))
	#     self.centerXLabelValue = QLabel(str(settings['camera_true_center_x']))
	#     self.centerYLabelValue = QLabel(str(settings['camera_true_center_y']))
	#
	#     self.roiXSlider = QSlider(Qt.Horizontal)
	#     self.roiXSlider.setMaximum(settings['camera_width'])
	#     self.roiXSlider.setValue(settings['roi_x'])
	#
	#     self.roiYSlider = QSlider(Qt.Horizontal)
	#     self.roiYSlider.setMaximum(settings['camera_height'])
	#     self.roiYSlider.setValue(settings['roi_y'])
	#
	#     self.roiWSlider = QSlider(Qt.Horizontal)
	#     self.roiWSlider.setMaximum(settings['camera_width'])
	#     self.roiWSlider.setValue(settings['roi_w'])
	#
	#     self.roiHSlider = QSlider(Qt.Horizontal)
	#     self.roiHSlider.setMaximum(settings['camera_height'])
	#     self.roiHSlider.setValue(settings['roi_h'])
	#
	#     self.centerXSlider = QSlider(Qt.Horizontal)
	#     self.centerXSlider.setMaximum(settings['camera_width'])
	#     self.centerXSlider.setValue(settings['camera_true_center_x'])
	#
	#     self.centerYSlider = QSlider(Qt.Horizontal)
	#     self.centerYSlider.setMaximum(settings['camera_height'])
	#     self.centerYSlider.setValue(settings['camera_true_center_y'])
	#
	#
	#     gridSettings.addWidget(roiXLabel, 0, 0)
	#     gridSettings.addWidget(roiYLabel, 1, 0)
	#     gridSettings.addWidget(roiWLabel, 2, 0)
	#     gridSettings.addWidget(roiHLabel, 3, 0)
	#     gridSettings.addWidget(centerXLabel, 4,0)
	#     gridSettings.addWidget(centerYLabel, 5,0)
	#
	#     gridSettings.addWidget(self.roiXSlider, 0,1)
	#     gridSettings.addWidget(self.roiYSlider, 1,1)
	#     gridSettings.addWidget(self.roiWSlider, 2,1)
	#     gridSettings.addWidget(self.roiHSlider, 3,1)
	#     gridSettings.addWidget(self.centerXSlider, 4, 1)
	#     gridSettings.addWidget(self.centerYSlider, 5,1)
	#
	#     gridSettings.addWidget(self.roiXLabelvalue, 0, 2)
	#     gridSettings.addWidget(self.roiYLabelvalue, 1, 2)
	#     gridSettings.addWidget(self.roiWLabelvalue, 2, 2)
	#     gridSettings.addWidget(self.roiHLabelvalue, 3, 2)
	#     gridSettings.addWidget(self.centerXLabelValue, 4,2)
	#     gridSettings.addWidget(self.centerYLabelValue,5,2)
	#
	#     rightVBox = QVBoxLayout()
	#     rightVBox.setSpacing(10)
	#
	#
	#     # xCenterLabel = QLabel('X:   0   ')
	#     # xCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))
	#     #
	#     # yCenterLabel = QLabel('Y:   0   ')
	#     # yCenterLabel.setFont(QtGui.QFont("Lato", pointSize=20))
	#
	#     manualControlLabel = QLabel("Manual Control")
	#     manualControlLabel.setFont(QtGui.QFont("Lato", pointSize=20))
	#
	#     self.releaseButton = QPushButton("Release Hydraulics")
	#     self.engageButton = QPushButton("Engage Hydraulics")
	#     self.resetCameraOffsetButton = QPushButton("Reset Camera Offset")
	#     self.programOffsetButton = QPushButton("Program Center")
	#     self.tareButton = QPushButton("Tare Center")
	#     buttonLayout,self.saveButton = self.bottomAlignedButton("Save Settings")
	#     # self.saveButton.setAlignment(Qt.AlignCenter)
	#
	#     self.chooseCurrentCamera = QtGui.QComboBox()
	#     self.chooseCurrentCamera.addItem(settings['currentCameraType'])
	#
	#     self.chooseCurrentCamera.addItem("d55l")
	#     self.chooseCurrentCamera.addItem("cp1p")
	#
	#     self.statusLabel = QLabel("Machine Idle")
	#     self.statusLabel.setAlignment(Qt.AlignRight)
	#
	#     self.xCenterLabel = QLabel("Center X: 0")
	#     self.xCenterLabel.setAlignment(Qt.AlignRight)
	#     self.yCenterLabel = QLabel("Center Y: 0")
	#     self.yCenterLabel.setAlignment(Qt.AlignRight)
	#     # rightVBox.addStretch(1)
	#     # rightVBox.addWidget(xCenterLabel)
	#     # rightVBox.addWidget(yCenterLabel)
	#     # rightVBox.addStretch(10)
	#
	#     rightVBox.addWidget(manualControlLabel)
	#     rightVBox.addWidget(self.releaseButton)
	#     rightVBox.addWidget(self.engageButton)
	#     rightVBox.addWidget(self.resetCameraOffsetButton)
	#     rightVBox.addWidget(self.programOffsetButton)
	#     rightVBox.addWidget(self.tareButton)
	#     rightVBox.addWidget(self.chooseCurrentCamera)
	#     rightVBox.addWidget(self.statusLabel)
	#     rightVBox.addWidget(self.xCenterLabel)
	#     rightVBox.addWidget(self.yCenterLabel)
	#     rightVBox.addStretch(1)
	#     # rightVBox.addWidget(self.saveButton)
	#     # rightVBox.addLayout(buttonLayout)
	#
	#     widget = QWidget()
	#     widget.setLayout(gridSettings)
	#     scroll.setWidget(widget)
	#
	#     layout.addWidget(menuFrame, 0, 0)
	#     layout.addLayout(rightVBox, 0, 2)
	#     layout.addWidget(self.imageLabel, 0, 1)
	#     # layout.addLayout(gridSettings, 1,1)
	#     layout.addWidget(scroll, 1, 1)
	#     # layout.addWidget(self.saveButton, 1,2)
	#     layout.addLayout(buttonLayout, 1,2)
	#
	#
	#     widget = QWidget()
	#     widget.setLayout(layout)
	#     mainWindow.setCentralWidget(widget)

	def bottomAlignedButton(self, buttonText):
		hbox = QVBoxLayout()
		pushButton = QPushButton(buttonText)
		hbox.addStretch(1)
		hbox.addWidget(pushButton)
		return hbox, pushButton
