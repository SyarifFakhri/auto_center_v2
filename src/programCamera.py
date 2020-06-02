from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtWidgets import QApplication
from flashTool import FlashTool
from arduinoController import ArduinoController
from pcbOrientationDetection import PcbDetector
import cv2
import time
import debugConfigs

class ProgramCamera(QtCore.QObject):
    callDoubleProgramCamera = pyqtSignal()
    callProgramCamera = pyqtSignal()
    statsData = pyqtSignal(list)
    
    callSimpleProgramCamera = pyqtSignal()
    callEngageHydraulics = pyqtSignal()
    callReleaseHydraulics = pyqtSignal()

    stopAnalogCameraCapture = pyqtSignal()
    

    def __init__(self, settings, currentCameraType):
        super(ProgramCamera, self).__init__()
        self.flashTool = FlashTool()
        self.currentProgrammingStep = 'Machine Idle'
        self.relativeCenters = []
        self.currentCameraType = ''
        self.overlayOption = ''

        self.PROGRAMMING_TIME_THRESH = 7

        if not debugConfigs.DEBUGGING_WITHOUT_ARDUINO:
            self.arduinoController = ArduinoController()
            self.arduinoController.onCamera()
            self.arduinoController.onLeds()

        #AI STUFF HERE
        #print("setting up cam")
        #self.AICamera = cv2.VideoCapture(debugConfigs.SECONDARY_VIDEO_CAP_DEVICE)
        #print("done getting cam")
        self.detector = PcbDetector(settings[currentCameraType], currentCameraType)
        self.detector.loadModel()
        #print("done setup detector")
    def reloadDetector(self, currentCameraType):
        self.detector.classifierPath = '../assets/classifier' + currentCameraType
        self.detector.scalerPath = "../assets/scaler" + currentCameraType
        self.detector.loadModel()

    def stop(self):
        self.arduinoController.shutDown()

    @pyqtSlot()
    def simpleProgramCamera(self):

        withOverlay = self.shouldUseOverlay()
        #Doesn't do any fancy stuff, just programs the camera to what it currently detects as the center
        QApplication.processEvents()
        relativeCenterPoints = self.relativeCenters

        if relativeCenterPoints == []:
            self.currentProgrammingStep = 'No centerpoint found'
            return

        # pass the center centerpoint
        centerPoints = relativeCenterPoints[0]  # 0: left center point, 1: center center point, 2: right center point IF using 3 points
        programX, programY = self.determineXandYOffset(centerPoints)
        canProgram = self.programSteps(programX,programY, withOverlay=withOverlay)
        time.sleep(1)
        if canProgram:
            self.currentProgrammingStep = 'Machine Idle'
        else:
            self.currentProgrammingStep = "Could not connect to Camera"

    @pyqtSlot()
    def engageHydraulics(self):
        self.currentProgrammingStep = "Engaging Pneumatics"
        self.arduinoController.engageHydraulics()
        self.currentProgrammingStep = "Machine Idle"

    @pyqtSlot()
    def releaseHydraulics(self):
        self.currentProgrammingStep = "Releasing Pneumatics"
        self.arduinoController.releaseHydraulics()
        self.currentProgrammingStep = "Machine Idle"

    @pyqtSlot(list)
    def updateRelativeCenters(self, cameraCenters):
        self.relativeCenters = cameraCenters
        #print(self.relativeCenters)
        if self.relativeCenters != []:
            self.relativeCenters[0][0] = int(self.relativeCenters[0][0]/1.5)
            self.relativeCenters[0][1] = int(self.relativeCenters[0][1]/1.5)

    @pyqtSlot()
    def resetCameraOffsets(self):
        self.setupMachineForProgramming()

        programX = 0  
        programY = 0

        canConnectToCamera = self.programSteps(
            programX,programY,withOverlay=False
        )

        if canConnectToCamera:
            self.currentProgrammingStep = 'Machine Idle'
        else:
            self.currentProgrammingStep = "Could not connect to camera"

        return canConnectToCamera

    def powerCycleCamera(self):
        print("Power cycling camera")
        self.currentProgrammingStep = 'Power cycling camera'
        self.arduinoController.offCamera()
        time.sleep(1)
        self.arduinoController.onCamera()
        time.sleep(2)
        QApplication.processEvents()
        time.sleep(1)
        QApplication.processEvents()
        print("Camera reset")

    @pyqtSlot()
    def programCenterPointDoubleProgramMethodTest(self):
        while True:
            QApplication.processEvents()
            self.programCenterPointDoubleProgramMethodReal()
            QApplication.processEvents()
            time.sleep(10)
            QApplication.processEvents()

    def shouldUseOverlay(self):
        if self.overlayOption == 'Overlay Enabled':
            return True

        elif self.overlayOption == 'Overlay Disabled':
            return False

        else:
            assert 0, "You must choose between 'Overlay Enabled' and 'Overlay Disabled'"

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

        try:
            self.setupMachineForProgramming()

            withOverlay = self.shouldUseOverlay()
            
            QApplication.processEvents()
            time.sleep(2)
            QApplication.processEvents()
            time.sleep(2) #allows it to capture the image ca
            QApplication.processEvents()

            #STEP 1 - RESET CAMERA OFFSETS
            succeeded = self.resetCameraOffsets() #succeeded means programming did not fail

            if not succeeded:
                self.releaseMachineResourcesAndClose(
                    isSuccess=False,
                    timeStart=timeStart,
                    failureCode="Could not connect to Camera. Please check connection.",
                    initialCenterPoints=[],
                )
                return

            #STEP 2 - PROGRAM FIRST CENTER POINT CORRECTION
            relativeCenterPoints = self.relativeCenters

            if relativeCenterPoints == []: #check if there's a valid centerpoint
                self.releaseMachineResourcesAndClose(
                    isSuccess=False,
                    timeStart=timeStart,
                    failureCode="Could not get center points.",
                    initialCenterPoints = []
                )
                return
            
            #STEP 2.1 - Check if already center
            initialCenterPoints = relativeCenterPoints[0]
            # pass the center centerpoint
            centerPoints = relativeCenterPoints[0]  # 0: left center point, 1: center center point, 2: right center point IF using 3 points

            if abs(centerPoints[0]) > 35 or abs(centerPoints[1]) > 35:
                self.releaseMachineResourcesAndClose(
                    isSuccess=False,
                    timeStart=timeStart,
                    failureCode="XY Offset exceeds machine maximum allowable program.",
                    initialCenterPoints=initialCenterPoints
                )
                return

            programX, programY = self.determineXandYOffset(centerPoints)
            canConnectToCamera = self.programSteps(programX,programY,withOverlay=False)

            if not canConnectToCamera:
                self.releaseMachineResourcesAndClose(
                    isSuccess=False,
                    timeStart=timeStart,
                    initialCenterPoints=initialCenterPoints,
                    failureCode="Could not connect to camera. Please check Connection"
                )

            relativeCenterPoints = self.relativeCenters
            centerPoints = relativeCenterPoints[0]
            isCentered = self.isCenterPointCenter(centerPoints)

            if isCentered:
                #STEP 3: add and program an overlay if needed
                if self.currentCameraType =='cp1p' and withOverlay:
                    self.programSteps(programX,programY, withOverlay=True)

                self.releaseMachineResourcesAndClose(
                    isSuccess=True,
                    timeStart=timeStart,
                    initialCenterPoints=initialCenterPoints,
                )

            else: #failed, could not center
                self.releaseMachineResourcesAndClose(
                    isSuccess=False,
                    timeStart=timeStart,
                    initialCenterPoints=initialCenterPoints,
                    failureCode="Could not center Camera"
                )


        except Exception as e:
            print("ERROR IN PROGRAMMING THREAD: ")
            print(e)
            self.currentProgrammingStep = 'Machine Error. Please contact Engineering Team.'
            time.sleep(2)
            self.currentProgrammingStep = 'Releasing Hydraulics'
            self.arduinoController.releaseHydraulics()
            self.currentProgrammingStep = 'Machine Idle'
            timeEnd = time.perf_counter()
            timeTaken = timeEnd - timeStart
            self.currentProgrammingStep = 'Time taken ' + str(round(timeTaken,2)) + ' seconds'

    def determineXandYOffset(self, centerPoints):
        if self.currentCameraType == 'd55l':
            programX = -centerPoints[0]  # The camera is mirrored on the x axis
            programY = centerPoints[1]
        elif self.currentCameraType == 'cp1p':
            programX = centerPoints[0]  # The camera is mirrored on the x axis
            programY = -centerPoints[1]
        else:
            assert 0, "INVALID CAMERA TYPE. MUST BE CP1P or D55L" + self.currentCameraType

        return programX, programY

    def programSteps(self, programX, programY, withOverlay):
        programX = self.clipValue(programX)
        programY = self.clipValue(programY)

        if self.currentCameraType == 'd55l':
            self.flashTool.alterCFGFileD55LCamera(programX, programY)
        elif self.currentCameraType == 'cp1p':
            self.flashTool.alterCFGFileCameraOffset(programX, programY, withOverlay)
        else:
            assert 0, "INVALID CAMERA TYPE. MUST BE CP1P or D55L" + self.currentCameraType

        self.currentProgrammingStep = 'Create Bin'

        self.flashTool.createBinFileCmd(self.currentCameraType)

        self.currentProgrammingStep = 'Flashing ' + self.currentCameraType + ' Config'

        tic = time.perf_counter()
        self.flashTool.flashCameraCmd()
        self.currentProgrammingStep = 'Finished Programming'

        toc = time.perf_counter()
        timeTaken = toc-tic
        if (timeTaken < self.PROGRAMMING_TIME_THRESH):
            return False

        self.powerCycleCamera()
        return True

    def releaseMachineResourcesAndClose(self,isSuccess, initialCenterPoints, timeStart,  failureCode='Generic Failure'):
        timeEnd = time.perf_counter()
        timeTaken = timeEnd - timeStart

        if isSuccess:
            self.currentProgrammingStep = "Camera Centered"
            self.statsData.emit(['succeeded', initialCenterPoints, timeTaken])

        else: #fail
            self.currentProgrammingStep = failureCode
            self.statsData.emit(['failed', initialCenterPoints, timeTaken])
        self.stopAnalogCameraCapture.emit()
        time.sleep(2)
        self.currentProgrammingStep = 'Releasing Hydraulics'
        self.arduinoController.releaseHydraulics()
        time.sleep(1)
        self.currentProgrammingStep = 'Time taken ' + str(round(timeTaken,2)) + ' seconds'
        self.releaseResources()

    def releaseResources(self):
        # self.arduinoController.offLeds()
        self.arduinoController.running = False
        self.isProgramming = False

    def setupMachineForProgramming(self):
        self.isProgramming = True
        self.arduinoController.onCamera()
        self.currentProgrammingStep = "Engaging Hydraulics"
        self.arduinoController.engageHydraulics()
        self.arduinoController.onLeds()
        self.arduinoController.offGreenLed()
        self.arduinoController.offRedLed()

    def checkPCBOrientation(self):
        self.currentProgrammingStep = "Check PCB Orientation"
        self.arduinoController.onRedLed()
        self.arduinoController.onGreenLed()
        print("open cam")
        cap = cv2.VideoCapture(debugConfigs.SECONDARY_VIDEO_CAP_DEVICE)
        print("read frames")
        
        for i in range(5):
            ret, frame = cap.read()
        print("run inference")
            
        if ret:
            pred, labels = self.detector.runInferenceSingleImage(frame)
            print(labels[pred[0]])
        else:
            print("ERROR NO PIC")
        print("release")
        cap.release()
        print("done")

        self.arduinoController.offRedLed()
        self.arduinoController.offGreenLed()

        return labels[pred[0]]

    def releaseMachineResourcesWithoutStats(self):
        self.currentProgrammingStep = 'Releasing Hydraulics'
        self.arduinoController.releaseHydraulics()
        time.sleep(1)
        self.currentProgrammingStep = 'Machine Idle'
        self.arduinoController.offLeds()
        self.arduinoController.running = False
        self.isProgramming = False

    def clipValue(self, value, clipTo=35):
        if abs(value) > clipTo:
            if value > 0:
                value = clipTo
            if value < 0:
                value = -clipTo
            else:
                value = 0
        return value


    def isCenterPointCenter(self, centerPoints,threshold=1):
        """Check if the RELATIVE center points are valid"""
        if abs(centerPoints[0]) <= threshold and abs(centerPoints[1]) <= threshold:
            return True
        return False
