from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, \
	QHBoxLayout, QScrollArea, QSlider, QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
import windowStyling


class SplashWindow():
	def init_ui(self, mainWindow):
		mainLayout = QVBoxLayout()
		mainLayout.setSpacing(10)
		mainLayout.setContentsMargins(10, 10, 10, 10)
		mainLayout.addStretch(1)

		menuFrame = QFrame()
		menuFrame.setContentsMargins(0, 0, 0, 0)
		# menuFrame.setStyleSheet("background-color: #4a4a4a")

		mainTitle = QLabel('Camera Auto Center System')
		mainTitle.setFont(QtGui.QFont("Lato", pointSize=40, weight=QtGui.QFont.Bold))
		mainTitle.setAlignment(Qt.AlignCenter)
		mainLayout.addWidget(mainTitle)

		# CENTER LABELS AND IMAGES
		centerLayout = QHBoxLayout()
		mainLayout.addLayout(centerLayout)
		mainLayout.addStretch(2)

		infoText = QLabel("Please choose the camera to program")
		infoText.setFont(QtGui.QFont("Lato", pointSize=20))
		infoText.setAlignment(Qt.AlignCenter)
		centerLayout.addWidget(infoText)

		centerBottomLayout = QHBoxLayout()
		mainLayout.addLayout(centerBottomLayout)

		d55lPic = QLabel()
		d55lPic.setPixmap(QtGui.QPixmap('../assets/camera.jpeg'))
		d55lPic.setScaledContents(True)
		d55lPic.setFixedSize(410,200)
		d55lPic.setAlignment(Qt.AlignCenter)
		centerBottomLayout.addWidget(d55lPic)

		cp1pPic = QLabel()
		cp1pPic.setPixmap(QtGui.QPixmap('../assets/camera_2.jpeg'))
		cp1pPic.setScaledContents(True)
		cp1pPic.setFixedSize(410,200)
		cp1pPic.setAlignment(Qt.AlignCenter)
		centerBottomLayout.addWidget(cp1pPic)

		bottomLayout = QHBoxLayout()
		mainLayout.addLayout(bottomLayout)

		self.chooseCp1p = QPushButton("Click the left button to choose CP1P")
		# self.chooseCp1p.setStyleSheet("padding: 20px")
		# self.chooseCp1p.setAlignment(Qt.AlignCenter)
		self.chooseCp1p.setFont(QtGui.QFont("Lato", pointSize=30, weight=QtGui.QFont.Bold))
		bottomLayout.addWidget(self.chooseCp1p)

		self.chooseD55l = QPushButton("click the right button to choose D55L")
		# self.chooseD55l.setStyleSheet("padding: 20px");
		# self.chooseD55l.setAlignment(Qt.AlignCenter)
		self.chooseD55l.setFont(QtGui.QFont("Lato", pointSize=30, weight=QtGui.QFont.Bold))
		bottomLayout.addWidget(self.chooseD55l)

		mainLayout.addStretch(2)
		widget = QWidget()
		widget.setLayout(mainLayout)
		mainWindow.setCentralWidget(widget)

	def infoWidget(self, title):
		roundedFrame = QFrame()
		roundedFrame.setStyleSheet(".QFrame{border-radius: 5px;background-color:#686868;}")
		roundedFrame.setContentsMargins(0, 0, 0, 0)

		vBox = QVBoxLayout()
		# vBox.setSpacing(10)
		vBox.setContentsMargins(5, 5, 5, 5)

		titleBox = QLabel(title)
		# titleBox.setStyleSheet("background-color:#1f1f1f;")
		# titleBox.setAlignment(Qt.AlignCenter)
		titleBox.setFont(QtGui.QFont("Lato", pointSize=20))
		titleBox.setContentsMargins(0, 0, 10, 0)

		labelText = QLabel("0")
		labelText.setFont(QtGui.QFont("Lato", pointSize=20))
		# labelText.setAlignment(Qt.AlignCenter)
		labelText.setStyleSheet("background-color:#373737;border-radius: 5px;color:#2AA1D3")
		labelText.setContentsMargins(10, 10, 10, 10)
		vBox.addWidget(titleBox)
		vBox.addWidget(labelText)

		roundedFrame.setLayout(vBox)

		return roundedFrame, labelText
