import subprocess, shlex
from subprocess import PIPE, CalledProcessError, Popen
import sys
import os
import numpy as np
import win32console
import msvcrt

class FlashTool():
    def __init__(self):
        self.aptinaLocation = '\"C:\\Aptina Imaging\\bin\\flashtool.exe\"'

        #self.fcfgLocation = '\"C:\\Users\\Default.DESKTOP-CAOIVKO\PycharmProjects\\auto_center_v2\\src\\200102_cam 2_REFERENCE.fcfg\"'
        #self.binLocation = '\"C:\\Users\\Default.DESKTOP-CAOIVKO\PycharmProjects\\auto_center_v2\\src\\generated.bin\"'
        self.fcfgLocation = '\"C:\\Users\\LattePanda\\Documents\\Repos\\auto_center_v2\\src\\200102_cam 2_REFERENCE.fcfg\"'
        self.binLocation = '\"C:\\Users\\LattePanda\\Documents\\Repos\\auto_center_v2\\src\\generated.bin\"'
        self.running = False

        #list of sensor locations
        self.sdatLocation = {
            'cp1p': '\"C:\\Aptina Imaging\\sensor_data\\ASX350AT-REV3.xsdat\"',
            'd55l': '\"C:\\Aptina Imaging\\sensor_data\\ASX344AT-REV1.xsdat\"'
        }

    def alterCFGFileCameraOffset(self, cameraOffsetX, cameraOffsetY):
        readLocation = "C:\\Users\\LattePanda\\Documents\\Repos\\auto_center_v2\\src\\200102_cam 2_REFERENCE.fcfg"
        searchStrX = '0x12, CAM_FOV_CALIB_X_OFFSET,  8, 0x00,	# 0x5C'
        searchStrY = '0x12, CAM_FOV_CALIB_Y_OFFSET,  8, 0x00 	# 0x5D'

        with open(readLocation, 'r') as input_file, open('cfg_automatic.fcfg', 'w') as output_file:
            for line in input_file:
                if line.strip() == searchStrX:
                    output_file.write('0x12, CAM_FOV_CALIB_X_OFFSET,  8, ' + str(cameraOffsetX) + ', #Generated automatically\n')

                elif line.strip() == searchStrY:
                    output_file.write(
                        '0x12, CAM_FOV_CALIB_Y_OFFSET,  8, ' + str(cameraOffsetY) + ' #Generated automatically\n')
                else:
                    output_file.write(line)

    # def alterCFGOverlay(self  ):
    def alterCFGFileD55LCamera(self, cameraOffsetX, cameraOffsetY):
        readLocation = "C:\\Users\\LattePanda\\Documents\\Repos\\auto_center_v2\\src\\D55L_CFG_REF.fcfg"
        searchStrX = '0xC860, 8,	0x0,	#CAM_FOV_CALIB_X_OFFSET'
        searchStrY = '0xC861, 8,	0x0	#CAM_FOV_CALIB_Y_OFFSET'

        with open(readLocation, 'r') as input_file, open('cfg_automatic.fcfg', 'w') as output_file:
            for line in input_file:
                if line.strip() == searchStrX:
                    output_file.write(
                        '0xC860, 8, ' + str(cameraOffsetX) + ', #Generated automatically\n')


                elif line.strip() == searchStrY:
                    output_file.write(
                        '0xC861, 8, ' + str(cameraOffsetY) + ' #Generated automatically\n')
                else:
                    output_file.write(line)

    # def createBinFileD55LCmd(self, cameraType):
    #     #cmd = self.aptinaLocation + ' -1 -fcfg ' + 'cfg_automatic.fcfg' + ' -sdat ' + self.sdatLocation + ' -bin ' + self.binLocation
    #     #print(cmd)
    #
    #     if self.running == False:
    #         print("Start running")
    #         self.running = True
    #         args = shlex.split(self.aptinaLocation + ' -1 -fcfg ' + 'cfg_automatic_D55L.fcfg' + ' -sdat ' + self.sdatLocation[cameraType] + ' -bin ' + self.binLocation)
    #         print (args)
    #         subprocess.run(args)
    #         print("Done running")
    #         self.running = False

    def createBinFileCmd(self, cameraType):
        #cmd = self.aptinaLocation + ' -1 -fcfg ' + 'cfg_automatic.fcfg' + ' -sdat ' + self.sdatLocation + ' -bin ' + self.binLocation
        #print(cmd)

        if self.running == False:
            print("Start running")
            self.running = True
            args = shlex.split(self.aptinaLocation + ' -1 -fcfg ' + 'cfg_automatic.fcfg' + ' -sdat ' + self.sdatLocation[cameraType] + ' -bin ' + self.binLocation)
            print (args)
            subprocess.run(args)
            print("Done running")
            self.running = False

    def flashCameraCmd(self):
        if self.running == False:
            print("Start running")
            self.running = True
            flashBinCmd = self.aptinaLocation + ' -0 -bin ' + self.binLocation + ' -erase' + ' -pagesize 0x0100 -memory \"Standard\" -maxsize 0x20000'
            print (flashBinCmd)
            subprocess.run(shlex.split(flashBinCmd))
            self.running = False
            print("Done running")
