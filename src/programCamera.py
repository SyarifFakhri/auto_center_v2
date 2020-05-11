from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtWidgets import QApplication
from flashTool import FlashTool
from arduinoController import ArduinoController
import time

class ProgramCamera(QtCore.QObject):
    callDoubleProgramCamera = pyqtSignal()
    callProgramCamera = pyqtSignal()
    statsData = pyqtSignal(list)

    callSimpleProgramCamera = pyqtSignal()

    callEngageHydraulics = pyqtSignal()
    callReleaseHydraulics = pyqtSignal()

    def __init__(self):
        super(ProgramCamera, self).__init__()
        self.flashTool = FlashTool()
        self.currentProgrammingStep = 'Machine Idle'
        self.relativeCenters = []
        self.currentCameraType = ''

        self.PROGRAMMING_TIME_THRESH = 3

        self.arduinoController = ArduinoController()
        self.arduinoController.bothButtonsPressed.connect(self.programCenterPointDoubleProgramMethod)
        self.arduinoController.onCamera()
        self.arduinoController.onLeds()

    @pyqtSlot()
    def simpleProgramCamera(self):
        #Doesn't do any fancy stuff, just programs the camera to what it currently detects as the center
        QApplication.processEvents()
        print('start')
        self.currentProgrammingStep = 'Alter CFG'
        # STEP 2.1 - Check if already center
        relativeCenterPoints = self.relativeCenters

        if relativeCenterPoints == []:
            print("Cannot Program. No centerpoint found")
            return

        # pass the center centerpoint
        centerPoints = relativeCenterPoints[0]  # 0: left center point, 1: center center point, 2: right center point IF using 3 points

        # check if it's already center
        if self.isCenterPointCenter(centerPoints):
            return

        # self.stopRunning = True #temporarily pause the camera

        programX = -centerPoints[0]  # The camera is mirrored on the x axis
        programY = centerPoints[1]

        programX = self.clipValue(programX)
        programY = self.clipValue(programY)

        # programX = 0
        # programY = 0

        print("Value to Program X: " + str(programX))
        print("Value to Program Y: " + str(programY))

        # self.flashTool.alterCFGFileCameraOffset(programX, programY)
        self.flashTool.alterCFGFileD55LCamera(programX, programY)
        self.currentProgrammingStep = 'Create Bin'
        self.flashTool.createBinFileCmd(self.currentCameraType)
        self.currentProgrammingStep = 'Flashing Camera 1 - DO NOT UNPLUG'

        tic = time.perf_counter()
        self.flashTool.flashCameraCmd()
        toc = time.perf_counter()

        timeTaken = toc - tic

        if (timeTaken < self.PROGRAMMING_TIME_THRESH):
            self.currentProgrammingStep = 'Programming failed. Check connection.'
            self.statsData.emit(['failed', centerPoints])
            time.sleep(5)
            self.currentProgrammingStep = ''
            # self.arduinoController.releaseHydraulics()
            return
        self.powerCycleCamera()
        self.currentProgrammingStep = 'Machine Idle'


    @pyqtSlot()
    def engageHydraulics(self):
        self.arduinoController.engageHydraulics()

    @pyqtSlot()
    def releaseHydraulics(self):
        self.arduinoController.releaseHydraulics()

    @pyqtSlot()
    def retractSliders(self):
        print("RELEASE HYDRAULICS")
        self.arduinoController.engageHydraulics()
        time.sleep(2)
        self.arduinoController.releaseHydraulics()

    @pyqtSlot(list)
    def updateRelativeCenters(self, cameraCenters):
        self.relativeCenters = cameraCenters

    @pyqtSlot()
    def resetCameraOffsets(self):
        self.arduinoController.onCamera()
        self.arduinoController.onLeds()
        self.isProgramming = True
        self.currentProgrammingStep = 'Alter CFG'

        programX = 0  # Very strange that this doesn't require a negative sign. Did I mess up somewhere?
        programY = 0

        programX = self.clipValue(programX)
        programY = self.clipValue(programY)

        print("Value to Program X: " + str(programX))
        print("Value to Program Y: " + str(programY))

        #self.flashTool.alterCFGFileCameraOffset(programX, programY)
        self.flashTool.alterCFGFileD55LCamera(programX, programY)
        self.currentProgrammingStep = 'Create Bin'
        self.flashTool.createBinFileCmd(self.currentCameraType)
        self.currentProgrammingStep = 'Resetting Camera Offsets'
        tic = time.perf_counter()
        self.flashTool.flashCameraCmd()
        toc = time.perf_counter()

        timeTaken = toc - tic

        if (timeTaken < self.PROGRAMMING_TIME_THRESH):
            self.currentProgrammingStep = 'Programming failed. Check connection.'
            time.sleep(3)
            self.currentProgrammingStep = 'Machine Idle'
            self.arduinoController.offLeds()
            return False

        self.powerCycleCamera()

        self.currentProgrammingStep = 'Machine Idle'
        print("Finished programming.")
        #self.arduinoController.offLeds()
        return True

    def powerCycleCamera(self):
        print("Power cycling camera")
        self.currentProgrammingStep = 'Power cycling camera'
        self.arduinoController.offCamera()
        time.sleep(1)
        self.arduinoController.onCamera()
        time.sleep(2)
        QApplication.processEvents()
        print("Camera reset")

    @pyqtSlot()
    def programCenterPointDoubleProgramMethod(self):
        """
        It's very likely we won't get the correct amount on the first try.
        So this method first programs it once, then calculates the offsets again, then adds that adjustment amount to the old amount
        and reprograms again

        Pros: simple
        cons: slow, because you have to reprogram twice
        :param param:
        :return:

        TODO:
        1. check if the camera is connected (Check if it's just a blank screen) - DONE
        2. check if the camera can be programmed/is detected (Based on timing)
        3. Check if  the new center point is correct
        """
        timeStart = time.perf_counter()

        self.arduinoController.onCamera()
        self.currentProgrammingStep = "Engaging Hydraulics"
        self.arduinoController.engageHydraulics()
        self.arduinoController.onLeds()

        QApplication.processEvents()
        time.sleep(3)

        if self.relativeCenters == []:
            print("No valid centerpoints")
            self.statsData.emit(['failed', []])
            # self.arduinoController.releaseHydraulics()
            return
        self.arduinoController.onLeds()
        relativeCenterPoints = self.relativeCenters
        centerPoints = relativeCenterPoints[0]
        initialCenterPoints = relativeCenterPoints[0]

        # check if it's already center
        #REENABLE BACK
        # if self.isCenterPointCenter(centerPoints):
        #     print("Camera Centered!")
        #     self.currentProgrammingStep = "Camera Centered"
        #     time.sleep(2)
        #     self.currentProgrammingStep = ''
        #     self.isProgramming = False
        #     self.statsData.emit(['success', initialCenterPoints])
        #     return

        #STEP 1 - RESET CAMERA OFFSETS
        succeeded = self.resetCameraOffsets() #succeeded means programming did not fail

        if not succeeded:
            self.statsData.emit(['failed', initialCenterPoints])
            # self.arduinoController.releaseHydraulics()
            return
        self.arduinoController.onLeds()

        #STEP 2 - PROGRAM FIRST CENTER POINT CORRECTION
        # for i in range(10):
        #     self.currentProgrammingStep = 'Restart cam: ' + str(10 - i)
        # self.powerCycleCamera()

        # if self.validImage == False:
        #     print("Invalid image")
        print('start')
        self.currentProgrammingStep = 'Alter CFG'
        #STEP 2.1 - Check if already center
        relativeCenterPoints = self.relativeCenters

        # pass the center centerpoint
        centerPoints = relativeCenterPoints[0]  # 0: left center point, 1: center center point, 2: right center point IF using 3 points

        # check if it's already center
        if self.isCenterPointCenter(centerPoints):
            self.statsData.emit(['succeeded', initialCenterPoints])
            return

        # self.stopRunning = True #temporarily pause the camera

        programX = -centerPoints[0] #The camera is mirrored on the x axis
        programY = centerPoints[1]

        programX = self.clipValue(programX)
        programY = self.clipValue(programY)

        # programX = 0
        # programY = 0

        print("Value to Program X: " + str(programX))
        print("Value to Program Y: " + str(programY))

        # self.flashTool.alterCFGFileCameraOffset(programX, programY)
        self.flashTool.alterCFGFileD55LCamera(programX, programY)
        self.currentProgrammingStep = 'Create Bin'
        self.flashTool.createBinFileCmd(self.currentCameraType)
        self.currentProgrammingStep = 'Flashing Camera 1 - DO NOT UNPLUG'

        tic = time.perf_counter()
        self.flashTool.flashCameraCmd()
        toc = time.perf_counter()

        timeTaken = toc - tic

        if (timeTaken < self.PROGRAMMING_TIME_THRESH):
            self.currentProgrammingStep = 'Programming failed. Check connection.'
            time.sleep(5)
            self.currentProgrammingStep = 'Machine Idle'
            self.arduinoController.releaseHydraulics()
            self.statsData.emit(['failed', initialCenterPoints])
            return


        self.currentProgrammingStep = 'Machine Idle'
        # QThread.sleep(10) #sleep an amount of time
        # time.sleep(10)
        self.powerCycleCamera()

        # for i in range(10):
        #     self.currentProgrammingStep = 'Restart cam: ' + str(10 - i)
        #     time.sleep(1)
        #     QApplication.processEvents()

        print("Relative centers: ", self.relativeCenters[0])
        ###Begin second camera flash
        relativeCenterPoints = self.relativeCenters
        centerPoints = relativeCenterPoints[0]

        # check if it's already center
        if self.isCenterPointCenter(centerPoints):
            self.statsData.emit(['succeeded', initialCenterPoints])
            return

        programX += -centerPoints[0]
        programY += centerPoints[1]

        programX = self.clipValue(programX)
        programY = self.clipValue(programY)

        # programX = 0
        # programY = 0

        print("Value to Program X: " + str(programX))
        print("Value to Program Y: " + str(programY))

        # self.flashTool.alterCFGFileCameraOffset(programX, programY)
        self.flashTool.alterCFGFileD55LCamera(programX, programY)
        self.currentProgrammingStep = 'Create Bin'
        self.flashTool.createBinFileCmd(self.currentCameraType)
        self.currentProgrammingStep = 'Flashing Camera 2 - DO NOT UNPLUG'
        self.flashTool.flashCameraCmd()
        self.currentProgrammingStep = 'Finished Programming'
        # print("Finished programming.")

        self.powerCycleCamera()

        #check if it succeeded
        relativeCenterPoints = self.relativeCenters
        centerPoints = relativeCenterPoints[0]

        if self.isCenterPointCenter(centerPoints):
            # self.currentProgrammingStep = 'Programming Suceeded'
            self.statsData.emit(['succeeded', initialCenterPoints])
            return

        else:
            self.currentProgrammingStep = 'Could not center'
            self.statsData.emit(['failed', initialCenterPoints])

        time.sleep(5)
        self.currentProgrammingStep = 'Releasing Hydraulics'
        self.arduinoController.releaseHydraulics()
        self.currentProgrammingStep = 'Machine Idle'
        timeEnd = time.perf_counter()

        print("Time taken: ", str(timeEnd - timeStart))

        self.arduinoController.running = False

    def clipValue(self, value, clipTo=35):
        if abs(value) > clipTo:
            if value > 0:
                value = clipTo
            if value < 0:
                value = -clipTo
            else:
                value = 0
        return value


    def isCenterPointCenter(self, centerPoints, threshold=1):
        """Check if the RELATIVE center points are valid"""
        if abs(centerPoints[0]) <= threshold:
            if abs(centerPoints[1]) <= threshold:
                print("Camera Centered!")
                self.currentProgrammingStep = "Camera Centered"
                time.sleep(5)
                self.currentProgrammingStep = 'Releasing Hydraulics'
                self.isProgramming = False
                # self.arduinoController.releaseHydraulics()
                self.arduinoController.releaseHydraulics()
                self.currentProgrammingStep = 'Machine Idle'
                return True
        return False
