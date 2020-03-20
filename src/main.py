###############################################################################
# File          : main.py
# Created by    : Rahul Kedia
# Created on    : 09/01/2020
# Project       : ReadOMR
# Description   : This file contains the main source code for the project.
################################################################################

import cv2
import os
import macros as M
import GetAnswers as GA
from CropOMR import CropOMR
from ReadConfig import ReadConfig
import json


################################################################################
# Function      : StoreInJSON
# Parameter     : AnswerDict - It is the answer dictionary for the questions.
# Description   : This function stores the answers in a json file named
#                 "Answers.txt"
# Return        : -
################################################################################
def StoreInJSON(AnswerDict):
    with open('Answers.txt', 'a') as outfile:
        json.dump(AnswerDict, outfile, indent=4, sort_keys=False)


################################################################################
# Function      : main
# Parameter     : OMR_Name - It is the name of omr type.
#                 CroppedOMR - It is the image of cropped OMR Sheet. It is
#                              cropped in rectangle with the help of four
#                              printed corner circles of the OMR Sheet.
#                 AnswerDict - It is the answer dictionary for the questions.
#                 ExpandSideBy - List of 2 variable which denotes the length 
#                                by which we want to expand side.
#                 NumOfQuestion - Number of questions to be detected.
#                 QuestionParam - List of parameters of the question of an OMR 
#                                 with which we can operate and extract answers 
#                                 for that question from the OMR.
# Description   : This function calls suitable functions one by one for reading  
#                 the config file, cropping the OMR, and the rearranging/resizing 
#                 the OMR sheet and then the answers are found for each question.
# Return        : -
################################################################################
def main(OMR_Name, InputImageFolderPath):
    AnswerDict = {}

    for ImageName in os.listdir(InputImageFolderPath):
        # Read Input and resize it
        InputImage = cv2.imread(InputImageFolderPath + "/" + ImageName)
        InputImage = cv2.resize(InputImage, M.RESIZE_TO)
    
        # Reading Config file
        ExpandSideBy, NumOfQuestion, QuestionParam = ReadConfig(OMR_Name)

        # Crop OMR wrt bounding boxes   
        CroppedOMR, _ = CropOMR(InputImage, ExpandSideBy=ExpandSideBy)
    
        # Extract different answers    
        for i in range(NumOfQuestion):
            Q = GA.FindAnswer(QuestionParam[i][1], QuestionParam[i][2], QuestionParam[i][3],\
                              QuestionParam[i][4], QuestionParam[i][5], QuestionParam[i][6],\
                              QuestionParam[i][7], QuestionParam[i][8], QuestionParam[i][9])
            AnswerDict[QuestionParam[i][0]] = Q.FindAnswer(CroppedOMR)

        #print(AnswerDict)

        StoreInJSON(AnswerDict)
    
    #cv2.waitKey(0)
