# import cv2
#
# cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
#
# while True:
#         ret,frame = cap.read()
#         cv2.imshow("test",frame)
#         cv2.waitKey(1)
#
#
array = [[-17, -17, "succeeded"], [32, -34, "succeeded"], [-14, -11, "succeeded"], [2, -46, "failed"], [16, -38, "failed"], [12, -10, "succeeded"], [-7, -42, "failed"], [24, -29, "succeeded"], [21, 10, "succeeded"], [17, 0, "succeeded"], [0, -26, "succeeded"], [16, -5, "succeeded"], [8, -6, "succeeded"], [4, -10, "succeeded"], [8, -13, "succeeded"], [6, -27, "succeeded"], [18, -10, "succeeded"], [26, -26, "succeeded"], [-27, -25, "succeeded"], [6, -2, "succeeded"], [14, -15, "succeeded"], [-4, 1, "succeeded"], [-14, -11, "succeeded"], [0, -14, "succeeded"], [29, -13, "succeeded"], [-2, -16, "succeeded"], [14, -16, "succeeded"], [12, 2, "succeeded"], [9, -31, "succeeded"], [4, -7, "succeeded"], [15, -12, "succeeded"], [-12, 0, "succeeded"], [-3, 10, "succeeded"], [-2, 11, "succeeded"], [1, -15, "succeeded"], [11, -7, "succeeded"], [-10, -17, "succeeded"], [22, -31, "succeeded"], [12, -2, "succeeded"], [1, -6, "succeeded"], [13, -38, "failed"], [-4, -26, "succeeded"], [-27, -25, "succeeded"], [23, -17, "succeeded"], [14, -5, "succeeded"], [-6, -18, "succeeded"], [24, -13, "succeeded"], [22, -28, "succeeded"], [8, -35, "succeeded"], [12, -34, "succeeded"], [4, -46, "failed"], [-15, -34, "succeeded"], [28, -20, "succeeded"], [27, 4, "succeeded"], [0, -10, "succeeded"], [-20, -24, "succeeded"], [-30, -5, "succeeded"], [-22, -20, "succeeded"], [-16, -36, "failed"], [-28, 3, "failed"], [20, -9, "succeeded"], [19, 2, "succeeded"], [-8, -10, "succeeded"], [2, 3, "succeeded"], [9, -19, "succeeded"], [-20, -14, "succeeded"]]

for element in array:
        print(element[2], end=' ')
        # print(element[1], end=' ')
        print(" ")