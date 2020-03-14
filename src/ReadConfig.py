###############################################################################
# File          : ReadConfig.py
# Created by    : Rahul Kedia
# Created on    : 14/03/2020
# Project       : ReadOMR
# Description   : This file is used to read the configure file of the OMR Sheet.
################################################################################


import cv2
import numpy as np 


# Simple and self explanatory code. documentation not done.

def SortQuestionParam(ReadLines):
	NumOfQ = len(ReadLines)
	QuestionParam = []

	for Line in ReadLines:
		Line = Line.replace("[", "").replace("]", "").replace("\n", "").replace("\"", "").replace("'", "").replace(" ", "")
		Line = Line.split(",")
		LineArray = Line.copy()
		for i in range(1, 10):
			if i != 7:
				LineArray[i] = int(LineArray[i])

		QuestionParam.append(LineArray)

	return NumOfQ, QuestionParam


def ReadConfig(OMR_Name):
	global f
	# Reading OMR Config file.
	OMR_Path = "ConfigFiles/" + OMR_Name + "_Config.txt"
	f = open(OMR_Path, "r")

	ReadLines = f.readlines()
	
	return SortQuestionParam(ReadLines)
