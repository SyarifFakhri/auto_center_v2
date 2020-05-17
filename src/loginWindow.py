from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,QScrollArea, QSlider,QLineEdit, QFrame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect


class LoginWindow():
    def init_ui(self, mainWindow):
        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(10)
        mainLayout.setContentsMargins(10, 10, 10, 10)

        menuFrame = QFrame()
        menuFrame.setContentsMargins(0, 0, 0, 0)
        # menuFrame.setStyleSheet("background-color: #4a4a4a")

        mainMenuTitleLayout = QVBoxLayout()
        mainLayout.addLayout(mainMenuTitleLayout)

        mainTitle = QLabel('Auto Center System')
        mainTitle.setFont(QtGui.QFont("Lato", pointSize=19, weight=QtGui.QFont.Bold))
        mainTitle.setAlignment(Qt.AlignCenter)
        mainMenuTitleLayout.addWidget(mainTitle)

        menuLayout = QHBoxLayout()
        menuLayout.setSpacing(20)
        menuLayout.setContentsMargins(15, 15, 25, 15)  # LTRB
        mainMenuTitleLayout.addLayout(menuLayout)

        self.mainLabel = QLabel("Main")
        self.mainLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.mainLabel.setAlignment(Qt.AlignCenter)
        menuLayout.addWidget(self.mainLabel)

        self.statisticsLabel = QLabel("Statistics")
        self.statisticsLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        # self.statisticsLabel.setContentsMargins(15,15,15,15)
        self.statisticsLabel.setAlignment(Qt.AlignCenter)
        menuLayout.addWidget(self.statisticsLabel)

        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setFont(QtGui.QFont("Lato", pointSize=10))
        self.settingsLabel.setStyleSheet("background-color: #4a4a4a; border-radius: 5px")
        self.settingsLabel.setContentsMargins(15, 10, 15, 10)
        self.settingsLabel.setAlignment(Qt.AlignCenter)
        menuLayout.addWidget(self.settingsLabel)

        loginFrame = QFrame()
        loginFrame.setFrameStyle(QFrame.Box)
        # loginFrame.setStyleSheet("background-color: black")
        # loginFrame.setColor(QtGui.QColor("black"))
        loginPrompt = QVBoxLayout()

        loginTitle = QLabel("Please enter your username and password: ")
        loginTitle.setAlignment(Qt.AlignCenter)

        userPrompt, self.userNameTextBox = self.labelWithTextEdit("Username")
        passPrompt, self.passNameTextBox = self.labelWithTextEdit("Password", password=True)

        self.loginButton = QPushButton("Login")

        self.helpText = QLabel("")  # Help text in case they get the password or username wrong
        self.helpText.setAlignment(Qt.AlignRight)

        loginPrompt.addStretch(1)
        loginPrompt.addWidget(loginTitle)
        loginPrompt.addLayout(userPrompt)
        loginPrompt.addLayout(passPrompt)
        loginPrompt.addWidget(self.loginButton)
        loginPrompt.addWidget(self.helpText)

        loginPrompt.addStretch(1)

        loginFrame.setLayout(loginPrompt)

        loginFrame.setContentsMargins(300, 50, 300, 50)  # l,t,r,b
        loginFrame.setMaximumSize(1000, 300)

        mainLayout.addWidget(loginFrame)
        mainLayout.addStretch(1)

        widget = QWidget()
        widget.setLayout(mainLayout)
        mainWindow.setCentralWidget(widget)

    def init_ui_2(self, mainWindow):
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