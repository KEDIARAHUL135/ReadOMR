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
gimg = cv2.cvtColor(InputImage, cv2.COLOR_BGR2GRAY)
img = cv2.medianBlur(gimg,5)
#cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,
                            param1=50,param2=30,minRadius=0,maxRadius=20)

circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    # draw the outer circle
    cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)

cv2.imshow('detected circles',img)







# Show output image
cv2.imshow("Result", InputImage)
cv2.waitKey(0)
