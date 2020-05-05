from pymata4 import pymata4
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot,QObject
from PyQt5.QtWidgets import QApplication
import time

class ArduinoController(QObject):
    bothButtonsPressed = pyqtSignal()

    #Board is based on pymata4 controller
    def __init__(self):
        super(ArduinoController, self).__init__()
        self.board = pymata4.Pymata4()
        self.setup()
        self.running = False

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
        self.board.set_pin_mode_digital_input_pullup(self.LEFT_BTN, callback=self.leftButtonCallback)
        self.board.set_pin_mode_digital_input_pullup(self.RIGHT_BTN, callback=self.rightButtonCallback)
        self.board.set_pin_mode_digital_input(self.REEDSW_CAM_HOLDER_RETRACT)
        self.board.set_pin_mode_digital_input(self.REEDSW_CAM_HOLDER_EXTEND)
        self.board.set_pin_mode_digital_input(self.REEDSW_POGOPIN_RETRACT)
        self.board.set_pin_mode_digital_input(self.REEDSW_POGOPIN_EXTEND)
        #setup all the pins
        print("Finished setup")

    def onLeds(self):
        self.board.digital_write(self.BACKLIGHT, 1)

    def offLeds(self):
        self.board.digital_write(self.BACKLIGHT, 0)

    def onCamera(self):
        self.board.digital_write(self.CAMERA_POWER, 1)

    def offCamera(self):
        self.board.digital_write(self.CAMERA_POWER, 0)

    def leftButtonCallback(self, data):
        # print("LEFT BUTTON PRESSED", self.board.digital_read(self.RIGHT_BTN)[0])
        self.monitorButtons()
        if self.running == False:
            if (self.board.digital_read(self.RIGHT_BTN)[0] == 0 and
                    self.board.digital_read(self.LEFT_BTN)[0] == 0):
                #right btn is also pressed
                self.bothButtonsPressed.emit()
                # print("TRIGGER")
                # self.engageHydraulics()

    def rightButtonCallback(self, data):
        # print("RIGHT BUTTON PRESSED", self.board.digital_read(self.LEFT_BTN)[0])
        self.monitorButtons()
        if self.running == False:
            if (self.board.digital_read(self.RIGHT_BTN)[0] == 0 and
                    self.board.digital_read(self.LEFT_BTN)[0] == 0):
                self.bothButtonsPressed.emit()
                # print("TRIGGER")
                # self.engageHydraulics()

    def monitorButtons(self):
        print("LEFT BUTTON PRESSED", self.board.digital_read(self.RIGHT_BTN)[0])
        print("RIGHT BUTTON PRESSED", self.board.digital_read(self.LEFT_BTN)[0])

    def engageHydraulics(self):
        self.running = True
        #engage hydraulics here
        #put into flash mode
        self.board.digital_write(self.VALVE_POGO_PIN, 0) #first make sure the pogo pin is not in the way
        self.waitUntilPogoPinsRetracted()

        self.board.digital_write(self.VALVE_CAM_HOLDER, 0) #retract engages the flash mode and camera
        self.waitUntilCamHolderRetracted()

        self.board.digital_write(self.VALVE_POGO_PIN, 1)
        self.waitUntilPogoPinsExtended()
        self.running = False

    def monitorReedSwitch(self):
        while True:
            pogoExtend, _ = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)
            pogoRetract, _ = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)
            camExtend, _ = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)
            camRetract, _ = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)

            print(pogoExtend, pogoRetract, camExtend, camRetract)


    def releaseHydraulics(self):
        self.running = True
        self.board.digital_write(self.VALVE_CAM_HOLDER, 0)
        self.waitUntilCamHolderRetracted()
        #release hydraulics here
        self.board.digital_write(self.VALVE_POGO_PIN, 0)
        self.waitUntilPogoPinsRetracted()

        self.board.digital_write(self.VALVE_CAM_HOLDER, 1)
        self.waitUntilCamHolderExtended()
        self.running = False

    def waitUntilPogoPinsRetracted(self):
        while True:
            reedswPogoExtended = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)[0]
            reedswPogoRetracted = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)[0]
            if reedswPogoExtended == 0 and reedswPogoRetracted == 1:
                break

            print("Waiting for pogo pins Retract")
    def waitUntilPogoPinsExtended(self):
        while True:
            reedswPogoExtended = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)[0]
            reedswPogoRetracted = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)[0]
            if reedswPogoExtended == 1 and reedswPogoRetracted== 0:
                break

            print("Waiting for pogo pins extend" + str(reedswPogoRetracted) + ' ' + str(reedswPogoExtended))

    def waitUntilCamHolderRetracted(self):
        while True:
            reedswCamExtended = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)[0]
            reedswCamRetracted = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)[0]
            if reedswCamExtended == 0 and reedswCamRetracted == 1:
                break

            print("Waiting for Cam Holder Retract")

    def waitUntilCamHolderExtended(self):
        while True:
            reedswCamExtended = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)[0]
            reedswCamRetracted = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)[0]
            if reedswCamExtended == 1 and reedswCamRetracted == 0:
                break

            print("Waiting for Cam Holder Extend")




