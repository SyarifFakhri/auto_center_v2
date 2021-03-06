from pymata4 import pymata4
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication
import time


class ArduinoController(QObject):
        bothButtonsPressed = pyqtSignal()
        shutdownSignal = pyqtSignal()
        closeBoards = pyqtSignal()
        # Board is based on pymata4 controller
        rightButtonPressed = pyqtSignal()
        leftButtonPressed = pyqtSignal()

        sendPopup = pyqtSignal(str)
        #callMachineCalibrationCheck = pyqtSignal()
        callShutdownTimer = pyqtSignal()

        def __init__(self):
                super(ArduinoController, self).__init__()

                self.board = pymata4.Pymata4("COM9", arduino_instance_id=1)
                self.leonardoBoard = pymata4.Pymata4("COM10", arduino_instance_id=2)

                self.setupArduino()
                self.setupLeonardo()

                self.checkShutdown = False

                self.offGreenLed()
                self.offRedLed()

                self.callShutdownTimer.connect(self.startShutdownTimer)
                #The first couple of times the callbacks are triggered its very noisey, so I just throwaway the first few inital readings

                #self.callMachineCalibrationCheck.connect(self.runMachineCalibrationCheck)

        def connectCallBacks(self):
                self.running = False
                self.initialRun = False
                # self.leonardoBoard.set_pin_mode_digital_input_pullup(self.SHUTDOWN_PIN, callback=self.sendShutdownSignal)
                self.board.set_pin_mode_digital_input_pullup(self.LEFT_BTN, callback=self.leftButtonCallback)
                self.board.set_pin_mode_digital_input_pullup(self.RIGHT_BTN, callback=self.rightButtonCallback)

        def setupLeonardo(self):
                self.RED_LED = 23
                self.GREEN_LED = 22
                self.BUZZER = 3
                # self.SHUTDOWN_PIN = 10

                self.leonardoBoard.set_pin_mode_digital_output(self.RED_LED)
                self.leonardoBoard.set_pin_mode_digital_output(self.GREEN_LED)
                self.leonardoBoard.set_pin_mode_tone(self.BUZZER)
                # self.leonardoBoard.set_pin_mode_digital_input_pullup(self.SHUTDOWN_PIN)

        def setupArduino(self):
                self.VALVE_POGO_PIN = 2  # Low is retract
                self.VALVE_CAM_HOLDER = 3  # Low is retract
                self.CAMERA_POWER = 6
                self.BACKLIGHT = 13

                # Outputs
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

                # Inputs
                self.board.set_pin_mode_digital_input_pullup(self.LEFT_BTN)
                self.board.set_pin_mode_digital_input_pullup(self.RIGHT_BTN)
                self.board.set_pin_mode_digital_input(self.REEDSW_CAM_HOLDER_RETRACT)
                self.board.set_pin_mode_digital_input(self.REEDSW_CAM_HOLDER_EXTEND)
                self.board.set_pin_mode_digital_input(self.REEDSW_POGOPIN_RETRACT)
                self.board.set_pin_mode_digital_input(self.REEDSW_POGOPIN_EXTEND)
                # setup all the pins
                print("Finished setup")

        def sendShutdownSignal(self, data):
                # print("CALL BACK CALLED")
                # print(self.checkShutdown)
                if self.checkShutdown == False:
                        # print("SHUTDOWN BUTTON PRESSED", str(self.leonardoBoard.digital_read(self.SHUTDOWN_PIN))[0])
                        if self.leonardoBoard.digital_read(self.SHUTDOWN_PIN)[0] == 0:
                                # print("EMIT SHUTDOWN SIGNAL")
                                self.checkShutdown = True
                                self.shutdownSignal.emit()

        def playNGTone(self):
                for i in range(15):
                        self.leonardoBoard.play_tone(self.BUZZER, 1000, 80)
                        time.sleep(0.11)

        def playGTone(self):
                self.leonardoBoard.play_tone(self.BUZZER, 1000, 2000)

        def shutDown(self):
                self.leonardoBoard.shutdown()
                self.board.shutdown()
                pass

        def onGreenLed(self):
                self.leonardoBoard.digital_write(self.GREEN_LED, 1)

        def offGreenLed(self):
                self.leonardoBoard.digital_write(self.GREEN_LED, 0)

        def onRedLed(self):
                self.leonardoBoard.digital_write(self.RED_LED, 1)

        def offRedLed(self):
                self.leonardoBoard.digital_write(self.RED_LED, 0)

        def onLeds(self):
                print("BACKLIGHT")
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
                if not self.checkShutdown:
                        self.checkShutdown = True
                        print("call shutdown signal")
                        self.callShutdownTimer.emit()

                if self.initialRun == False:
                        if (self.board.digital_read(self.LEFT_BTN)[0] == 0):
                                self.initialRun = True
                                self.leftButtonPressed.emit()

                print("callback end")
                self.leftButtonPrevious = self.board.digital_read(self.LEFT_BTN)[0]

        def rightButtonCallback(self, data):
                self.monitorButtons()
                # print("RIGHT BUTTON PRESSED", self.board.digital_read(self.LEFT_BTN)[0])
                if not self.checkShutdown:
                        self.checkShutdown = True
                        print("call shutdown signal")
                        self.callShutdownTimer.emit()

                if self.initialRun == False:
                        if (self.board.digital_read(self.RIGHT_BTN)[0] == 0):
                                self.initialRun = True
                                self.rightButtonPressed.emit()

                self.rightButtonPrevious = self.board.digital_read(self.RIGHT_BTN)[0]

                print('callback end')

        def startShutdownTimer(self):
                willShutdown = False
                startTime = time.perf_counter()
                debounceCounter = 0
                previousButtonsState = False
        
                while (self.board.digital_read(self.RIGHT_BTN)[0] == 0 and self.board.digital_read(self.LEFT_BTN)[0] == 0) or debounceCounter < 2:
                        debounceCounter += 1
                        print("check shutdown")
                        self.monitorButtons()
                        QApplication.processEvents()
                        time.sleep(0.1)
                        currentTime = time.perf_counter()
                        elapsedTime = currentTime - startTime
                        if debounceCounter > 2:
                                print("SET PREVIOUS BUTTON STATE")
                                previousButtonsState = True
                        if elapsedTime > 5:
                                self.shutdownSignal.emit()
                                willShutdown = True
                                break

                self.checkShutdown = False
                print("stop checking shutdown")

                if willShutdown:
                        return

                if self.running == False:
                        if previousButtonsState: #if both were pressed previously
                                self.running = True
                                self.bothButtonsPressed.emit()
                                

        def monitorButtons(self):
                print("LEFT BUTTON PRESSED", self.board.digital_read(self.RIGHT_BTN)[0])
                print("RIGHT BUTTON PRESSED", self.board.digital_read(self.LEFT_BTN)[0])

        def engageHydraulics(self):
                # engage hydraulics here
                isPogoExtended = self.checkPogoPinExtended()
                isCamRetracted = self.checkCamHolderRetracted()

                if (isPogoExtended == True and isCamRetracted == True):
                        return

                # put into flash mode
                self.board.digital_write(self.VALVE_POGO_PIN, 0)  # first make sure the pogo pin is not in the way
                self.waitUntilPogoPinsRetracted()

                self.board.digital_write(self.VALVE_CAM_HOLDER, 0)  # retract engages the flash mode and camera
                self.waitUntilCamHolderRetracted()

                self.board.digital_write(self.VALVE_POGO_PIN, 1)
                self.waitUntilPogoPinsExtended()

        def monitorReedSwitch(self):
                while True:
                        pogoExtend, _ = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)
                        pogoRetract, _ = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)
                        camExtend, _ = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)
                        camRetract, _ = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)

                        print(pogoExtend, pogoRetract, camExtend, camRetract)

        def releaseHydraulics(self):

                isPogoRetracted = self.checkPogoPinRetracted()
                isCamExtended = self.checkCamHolderExtended()

                if (isPogoRetracted == True and isCamExtended == True):
                        return

                self.board.digital_write(self.VALVE_CAM_HOLDER, 0)
                self.waitUntilCamHolderRetracted()
                # release hydraulics here
                self.board.digital_write(self.VALVE_POGO_PIN, 0)
                self.waitUntilPogoPinsRetracted()

                self.board.digital_write(self.VALVE_CAM_HOLDER, 1)
                self.waitUntilCamHolderExtended()

        def checkPogoPinRetracted(self):
                reedswPogoExtended = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)[0]
                reedswPogoRetracted = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)[0]

                if reedswPogoExtended == 0 and reedswPogoRetracted == 1:
                        return True
                else:
                        return False

        def checkPogoPinExtended(self):
                reedswPogoExtended = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)[0]
                reedswPogoRetracted = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)[0]

                if reedswPogoExtended == 1 and reedswPogoRetracted == 0:
                        return True
                else:
                        return False

        def checkCamHolderRetracted(self):
                reedswCamExtended = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)[0]
                reedswCamRetracted = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)[0]
                if reedswCamExtended == 0 and reedswCamRetracted == 1:
                        return True
                else:
                        return False

        def checkCamHolderExtended(self):
                reedswCamExtended = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)[0]
                reedswCamRetracted = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)[0]
                if reedswCamExtended == 1 and reedswCamRetracted == 0:
                        return True
                else:
                        return False

        def waitUntilPogoPinsRetracted(self):
                print("Waiting for pogo pins Retract")
                while True:
                        QApplication.processEvents()
                        time.sleep(0.1)
                        reedswPogoExtended = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)[0]
                        reedswPogoRetracted = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)[0]
                        if reedswPogoExtended == 0 and reedswPogoRetracted == 1:
                                break
                print("Pogo pins Retracted")

        def waitUntilPogoPinsExtended(self):
                print("Waiting for pogo pins extend")
                while True:
                        QApplication.processEvents()
                        time.sleep(0.1)
                        reedswPogoExtended = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)[0]
                        reedswPogoRetracted = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)[0]
                        if reedswPogoExtended == 1 and reedswPogoRetracted == 0:
                                break
                print("Pogo pins Extended")

        def waitUntilCamHolderRetracted(self):
                print("Waiting for Cam Holder Retract")
                while True:
                        QApplication.processEvents()
                        time.sleep(0.1)
                        reedswCamExtended = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)[0]
                        reedswCamRetracted = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)[0]
                        if reedswCamExtended == 0 and reedswCamRetracted == 1:
                                break
                print("Cam Holder Retracted")

        def waitUntilCamHolderExtended(self):
                print("Waiting for Cam Holder Extend")
                while True:
                        QApplication.processEvents()
                        time.sleep(0.1)
                        reedswCamExtended = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)[0]
                        reedswCamRetracted = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)[0]
                        if reedswCamExtended == 1 and reedswCamRetracted == 0:
                                break
                print("Cam Holder Extended")

        ###Fine grain control stuff down here - Intended for use with machine calibration
        def isCamHolderPneumaticsWorking(self):
                statusEvents = []
                self.board.digital_write(self.VALVE_CAM_HOLDER, 1)  # first extend the pneumatics
                for i in range(6):
                        time.sleep(0.5)
                        QApplication.processEvents()
                reedswCamExtended = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)[0]
                reedswCamRetracted = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)[0]
                if reedswCamExtended != 1:
                        statusEvents.append("TEST FAIL: Cam holder reed switch extend reads 1 when Cam Holder Extend")
                else:
                        statusEvents.append("TEST PASS: Cam holder reed switch extend reads 1 when Cam Holder Extend")
                if reedswCamRetracted != 0:
                        statusEvents.append("TEST FAIL: Cam holder reed switch retract reads 0 when Cam Holder Extend")
                else:
                        statusEvents.append("TEST PASS: Cam holder reed switch retract reads 0 when Cam Holder Extend")

                self.board.digital_write(self.VALVE_CAM_HOLDER, 0)
                for i in range(6):
                        time.sleep(0.5)
                        QApplication.processEvents()
                reedswCamExtended = self.board.digital_read(self.REEDSW_CAM_HOLDER_EXTEND)[0]
                reedswCamRetracted = self.board.digital_read(self.REEDSW_CAM_HOLDER_RETRACT)[0]
                if reedswCamExtended != 0:
                        statusEvents.append("TEST FAIL: Cam holder reed switch extend reads 0 when Cam Holder retrac")
                else:
                        statusEvents.append("TEST PASS: Cam holder reed switch extend reads 0 when Cam Holder retract")
                if reedswCamRetracted != 1:
                        statusEvents.append("TEST FAIL: Cam holder reed switch retract reads 1 when Cam Holder retract")
                else:
                        statusEvents.append("TEST PASS: Cam holder reed switch retract reads 1 when Cam Holder retract")
                return statusEvents

        def isPogoPinPneumaticsWorking(self):
                statusEvents = []
                self.board.digital_write(self.VALVE_POGO_PIN, 1)  # first extend the pneumatics
                for i in range(6):
                        time.sleep(0.5)
                        QApplication.processEvents()
                reedswPogoExtended = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)[0]
                reedswPogoRetracted = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)[0]
                if reedswPogoExtended != 1:
                        statusEvents.append("TEST FAIL: Pogo pin reed switch retract reads 0 when Pogo pin Extend")
                else:
                        statusEvents.append("TEST PASS: Pogo pin reed switch extend reads 1 when Pogo pin Extend")
                if reedswPogoRetracted != 0:
                        statusEvents.append("TEST FAIL: Pogo pin reed switch retract reads 0 when Pogo pin Extend")
                else:
                        statusEvents.append("TEST PASS: Pogo pin reed switch retract reads 0 when Pogo pin Extend")

                self.board.digital_write(self.VALVE_POGO_PIN, 0)
                for i in range(6):
                        time.sleep(0.5)
                        QApplication.processEvents()
                reedswPogoExtended = self.board.digital_read(self.REEDSW_POGOPIN_EXTEND)[0]
                reedswPogoRetracted = self.board.digital_read(self.REEDSW_POGOPIN_RETRACT)[0]
                if reedswPogoExtended != 0:
                        statusEvents.append("TEST FAIL: Pogo pin reed switch extend reads 0 when Pogo pin retract")
                else:
                        statusEvents.append("TEST PASS: Pogo pin reed switch extend reads 0 when Pogo pin retract")
                if reedswPogoRetracted != 1:
                        statusEvents.append("TEST FAIL: Pogo pin reed switch retract reads 1 when Pogo pin retract")
                else:
                        statusEvents.append("TEST PASS: Pogo pin reed switch retract reads 1 when Pogo pin retract")

                return statusEvents

        def checkLeftButtonPress(self):
                for i in range(6):
                        time.sleep(0.5)
                        QApplication.processEvents()
                if self.board.digital_read(self.LEFT_BTN)[0] == 0:  # should be low cuz input pullup
                        return True
                return False

        def checkRightButtonPress(self):
                for i in range(6):
                        time.sleep(0.5)
                        QApplication.processEvents()
                if self.board.digital_read(self.RIGHT_BTN)[0] == 0:
                        return True
                return False
