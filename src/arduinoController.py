from pymata4 import pymata4
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot,QObject
from PyQt5.QtWidgets import QApplication

class ArduinoController(QObject):
    bothButtonsPressed = pyqtSignal()

    #Board is based on pymata4 controller
    def __init__(self):
        super(ArduinoController, self).__init__()
        self.board = pymata4.Pymata4()
        self.setup()

    def setup(self):
        self.VALVE_POGO_PIN = 2 #Low is retract
        self.VALVE_CAM_HOLDER = 3 #Low is retract
        self.CAMERA_POWER = 6
        self.BACKLIGHT = 13

        #Outputs
        self.board.set_pin_mode_digital_output(self.VALVE_POGO_PIN)
        self.board.set_pin_mode_digital_output(self.VALVE_CAM_HOLDER)
        self.board.set_pin_mode_digital_output(self.CAMERA_POWER)
        self.board.set_pin_mode_digital_output(self.BACKLIGHT)

        self.LEFT_BTN = 5
        self.RIGHT_BTN = 7
        self.REEDSW_CAM_HOLDER_RETRACT = 12
        self.REEDSW_CAM_HOLDER_EXTEND = 11
        self.REEDSW_POGOPIN_RETRACT = 10
        self.REEDSW_POGOPIN_EXTEND = 9

        #Inputs
        self.board.set_pin_mode_digital_input_pullup(self.LEFT_BTN, self.leftButtonCallback)
        self.board.set_pin_mode_digital_input_pullup(self.RIGHT_BTN, self.rightButtonCallback)
        self.board.set_pin_mode_digital_input(self.REEDSW_CAM_HOLDER_RETRACT)
        self.board.set_pin_mode_digital_input(self.REEDSW_CAM_HOLDER_EXTEND)
        self.board.set_pin_mode_digital_input(self.REEDSW_POGOPIN_RETRACT)
        self.board.set_pin_mode_digital_input(self.REEDSW_POGOPIN_EXTEND)
        #setup all the pins

    def leftButtonCallback(self):
        if (self.board.digital_read(self.RIGHT_BTN)):
            #right btn is also pressed
            self.bothButtonsPressed.emit()

    def rightButtonCallback(self):
        if (self.board.digital_read(self.LEFT_BTN)):
            self.bothButtonsPressed.emit()

    def engageHydraulics(self):
        #engage hydraulics here
        #put into flash mode
        self.board.digital_write(self.VALVE_POGO_PIN, 0) #first make sure the pogo pin is not in the way
        self.waitUntilPogoPinsRetracted()

        self.board.digital_write(self.VALVE_CAM_HOLDER, 0) #retract engages the flash mode and camera
        self.waitUntilCamHolderRetracted()

        self.board.digital_write(self.VALVE_POGO_PIN, 1)
        self.waitUntilPogoPinsExtended()

    def releaseHydraulics(self):
        #release hydraulics here
        self.board.digital_write(self.VALVE_POGO_PIN, 0)
        self.waitUntilPogoPinsRetracted()

        self.board.digital_write(self.VALVE_CAM_HOLDER, 1)
        self.waitUntilCamHolderExtended()

    def waitUntilPogoPinsRetracted(self):
        while not (self.board.digital_read(self.REEDSW_POGOPIN_EXTEND) == 0 and
            self.board.digital_read(self.REEDSW_POGOPIN_RETRACT) == 1): #ensure that the pogopins are fully retracted first
            QApplication.processEvents()
            print("Waiting for Pogo pin Retract")

    def waitUntilPogoPinsExtended(self):
        while not (self.board.digital_read(self.REEDSW_POGOPIN_EXTEND) == 1 and
            self.board.digital_read(self.REEDSW_POGOPIN_RETRACT) == 0): #ensure that the pogopins are fully retracted first
            QApplication.processEvents()
            print("Waiting for Pogo pin Extend")

    def waitUntilCamHolderRetracted(self):
        while not (self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND) == 0 or
            self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT) == 1): #ensure that the pogopins are fully retracted first
            QApplication.processEvents()
            print("Waiting for Cam Holder Retract")

    def waitUntilCamHolderExtended(self):
        while not (self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND) == 1 or
            self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT) == 0): #ensure that the pogopins are fully retracted first
            QApplication.processEvents()
            print("Waiting for Cam Holder Extend")




