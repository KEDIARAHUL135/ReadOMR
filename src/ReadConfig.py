###############################################################################
# File          : ReadConfig.py
# Created by    : Rahul Kedia
# Created on    : 14/03/2020
# Project       : ReadOMR
# Description   : This file is used to read the configure file of the OMR Sheet.
################################################################################

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
	FirstLine = ReadLines[0]
	FirstLine = FirstLine.replace("\n", "").replace("\"", "").replace("'", "")
	ExpandSideBy = int(FirstLine)
	
	NumOfQ, QuestionParam = SortQuestionParam(ReadLines[1:])
	return ExpandSideBy, NumOfQ, QuestionParam
