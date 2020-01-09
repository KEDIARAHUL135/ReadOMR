###############################################################################
# File          : main.py
# Created by    : Rahul Kedia
# Created on    : 09/01/2020
# Project       : ReadOMR
# Description   : This file contains the main source code for the project.
################################################################################

import cv2
import numpy as np


# Read Input and resize it
InputImage = cv2.imread("InputImages/Blank.jpeg")
NewSize = (800, 800)
InputImage = cv2.resize(InputImage, NewSize)

# Extract the corner four circle's centre point
## Apply Hough Circle Detection
GrayImage = cv2.cvtColor(InputImage, cv2.COLOR_BGR2GRAY)
BlurImage = cv2.medianBlur(GrayImage, 7)

Circles = cv2.HoughCircles(BlurImage, cv2.HOUGH_GRADIENT, 1.3, 20,
                            param1=50, param2=30, minRadius=9, maxRadius=20)
Circles = np.uint16(np.around(Circles))


## Filter circles according to their position. We are interested in corner circles only
CornerCircles = np.zeros((4,3), np.uint16())
NumOfCCFound = 0

for i in Circles[0]:
    if NumOfCCFound < 4:
        if ((i[0] <= 90) & (i[1] <= 90)).all():
            CornerCircles[NumOfCCFound] = i
            NumOfCCFound += 1
        elif ((i[0] <= 90) & (i[1] >= 710)).all():
            CornerCircles[NumOfCCFound] = i
            NumOfCCFound += 1
        elif ((i[0] >= 710) & (i[1] <= 90)).all():
            CornerCircles[NumOfCCFound] = i
            NumOfCCFound += 1
        elif ((i[0] >= 710) & (i[1] >= 710)).all():
            CornerCircles[NumOfCCFound] = i
            NumOfCCFound += 1
    else:
        break

FinalCornerCircles = np.zeros((1, 4, 3), np.uint16())
FinalCornerCircles[0] = CornerCircles


for i in FinalCornerCircles[0, :]:
    # draw the outer circle
    cv2.circle(BlurImage, (i[0], i[1]), i[2], (0, 255, 0), 2)
    # draw the center of the circle
    cv2.circle(BlurImage, (i[0], i[1]), 2, (0, 0, 255), 3)

cv2.imshow('detected circles', BlurImage)







# Show output image
cv2.imshow("Result", InputImage)
cv2.waitKey(0)
