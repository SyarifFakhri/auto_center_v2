"""
Roughly here's how I check

"""

import cv2
import numpy as np
import math

def rotatePointAroundCenter(point_x, point_y, center_x, center_y, angle):
    rotated_x = (math.cos(angle) * (point_x - center_x) - math.sin(angle) * (point_y - center_y)) + center_x
    rotated_y = (math.sin(angle) * (point_x - center_x) + math.cos(angle) * (point_y - center_y)) + center_y
    return (rotated_x, rotated_y)

def getAngleBetweenTwoPoints(point_a, point_b):
    x_dist = point_a[0] - point_b[0]
    y_dist = point_a[1] - point_b[1]

    return math.atan(y_dist/x_dist)

def roundInt(num):
    return int(round(num))


blank_image = np.zeros((500, 500, 3), np.uint8)

#these two pair
left_angle_center_point = (100,100)
right_angle_center_point = (400,150)

cv2.circle(blank_image, left_angle_center_point, 3, (255,255,255),-1)
cv2.circle(blank_image, right_angle_center_point, 3, (255,255,255), -1)

angle = getAngleBetweenTwoPoints(left_angle_center_point, right_angle_center_point) #angle here is calculated by the angle between the two points
print("Angle between two points",angle)

#these two pairs are going to be the target center and the detected center
detected_center_point = (200,200)
target_center_point = (246,228)

# translation_vector = (50,20) #this is the true translation vector (in the second coordinate space, not the main one) #try to reverse engineer this part
#if you're confused why there are two coordinate spaces
#one coordinate space is the screen
#the second coordinate space is the rotation of the pcb on the lens
#we work in the first coordinate space, but when manipulating x and y on the actual camera lens, it'll move according to the second coordinate space

blank_image = cv2.circle(blank_image, detected_center_point, 3, (255,0,0), -1)
blank_image = cv2.circle(blank_image, target_center_point, 3, (0,255,0), -1)


# for point_x in range(translation_vector[0]):
#     point_x = point_x + detected_center_point[0] #- translation_vector[0]
#
#     x_vector_coords = rotatePointAroundCenter(point_x, detected_center_point[1], detected_center_point[0], detected_center_point[1], angle)
#
#     blank_image = cv2.circle(blank_image, (point_x, detected_center_point[1]), 3, (255, 0, 0), -1)
#
#     blank_image = cv2.circle(blank_image, (roundInt(x_vector_coords[0]), roundInt(x_vector_coords[1])), 3, (255,255,0), -1)
#
#     cv2.imshow("blank_image", blank_image)
#     cv2.waitKey(10)
#
# for point_y in range(translation_vector[1]):
#     point_y = point_y + detected_center_point[1] + 1 #idk why you need + 1 here but if you don't you have one less in the final translation for some reason
#
#     y_vector_coords = rotatePointAroundCenter(detected_center_point[0] + translation_vector[0], point_y, detected_center_point[0], detected_center_point[1], angle)
#
#     blank_image = cv2.circle(blank_image, (detected_center_point[0] + translation_vector[0], point_y), 3, (255,0,0), -1)
#     blank_image = cv2.circle(blank_image, (roundInt(y_vector_coords[0]), roundInt(y_vector_coords[1])), 3, (255,255,0), -1)
#
#     cv2.imshow("blank_image", blank_image)
#     cv2.waitKey(10)
#
# print(y_vector_coords)

translation_vector = [0,0]
final_point_vector = rotatePointAroundCenter(target_center_point[0], target_center_point[1], detected_center_point[0], detected_center_point[0], -angle)
translation_vector[0] = final_point_vector[0] - detected_center_point[0]
translation_vector[1] = final_point_vector[1] - detected_center_point[1]
print(translation_vector)


# #rotate coord 1 around coord 2
# for angle in range(360):
#     angle = (angle)*(math.pi/180)
#     point = rotatePointAroundCenter(detected_center_point[0], detected_center_point[1], target_center_point[0], target_center_point[1], angle)
#
#     blank_image = cv2.circle(blank_image, point, 3, (0,0,255), -1)
#     cv2.imshow("blank_image", blank_image)
#     cv2.waitKey(10)

cv2.waitKey(0)
