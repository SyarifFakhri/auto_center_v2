from arduinoController import ArduinoController

arduinoController = ArduinoController()
arduinoController.onCamera()

while True:
    pass



# import time
#
# # from pymata4 import pymata4
# #
# #
# # board = pymata4.Pymata4()
# #
# # board.set_pin_mode_digital_input_pullup(12)
# #
# # controller.monitorReedSwitch()
# #
# # controller.board.shutdown()
#
# if __name__ == '__main__':
#     controller = ArduinoController()
#     # controller.releaseHydraulics()
#     # time.sleep(2)
#     # controller.engageHydraulics()
#     # time.sleep(2)
#     # controller.releaseHydraulics()
#     while True:
#         # controller.monitorButtons()
#         pass

# from flashTool import FlashTool
#
# flasher = FlashTool()
# flasher.alterCFGFileCameraOffset(0,0)
# out = flasher.testCreate()
# print("OUT:")
# print(out)
#
#
