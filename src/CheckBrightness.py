###############################################################################
# File          : CheckBrightness.py
# Created by    : Rahul Kedia
# Created on    : 20/03/2020
# Project       : ReadOMR
# Description   : It checks how bright a image is and accordingly stes the value 
#				  of upper range of "Value" in HSV scale for image masking for 
#				  black.
################################################################################


# Code is simple and selfexplanatory.

import cv2


def CheckBrightness(Image):
	Height, Width = Image.shape[:2]
	Sum = 0
	UpperLimitOfValue = 0

	GrayImage = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)

	for i in range(Height):
		for j in range(Width):
			Sum += GrayImage[i][j]

	Sum /= (Height*Width)

	if Sum >= 200:
		UpperLimitOfValue = 150
	elif Sum >= 175:
		UpperLimitOfValue = 130  
	else:
		UpperLimitOfValue = 100

	return UpperLimitOfValue