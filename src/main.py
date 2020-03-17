###############################################################################
# File          : main.py
# Created by    : Rahul Kedia
# Created on    : 09/01/2020
# Project       : ReadOMR
# Description   : This file contains the main source code for the project.
################################################################################

import cv2
import macros as M
import GetAnswers as GA
from CropOMR import CropOMR
from ReadConfig import ReadConfig
import json


################################################################################
# Function      : ExtractAnswers
# Parameter     : AnswerDict - It is the answer dictionary for each question.
#                 AnsImages - It is the object of class Answers containing
#                             cropped images of answers for each question.
#                 {Rest all the parameters have their usual meanings as
#                 mentioned in macros.py file. Each of these parameter is
#                 for different question.}
# Description   : This function initialises objects for different questions
#                 and then calls suitable method to fnd answer and then
#                 stores the answers in a dictionary.
# Return        : AnswerDict
################################################################################
def ExtractAnswers(OMRImage):
    AnswerDict = {}

    AnswerDict = M.GetAnswerString(AnswerDict, OMRImage)

    return AnswerDict


################################################################################
# Function      : StoreInJSON
# Parameter     : AnswerDict - It is the answer dictionary for each question.
# Description   : This function stores the answers in a json file named
#                 "Answers.txt"
# Return        : -
################################################################################
def StoreInJSON(AnswerDict):
    with open('Answers.txt', 'w') as outfile:
        json.dump(AnswerDict, outfile, indent=4, sort_keys=False)


################################################################################
# Function      : main
# Parameter     : CroppedOMR - It is the image of cropped OMR Sheet. It is
#                              cropped in rectangle with the help of four
#                              printed corner circles of the OMR Sheet.
#                 AnswerDict - It is the answer dictionary for each question.
# Description   : This function calls suitable functions one by one for
#                 detecting circles, and the rearranging/resizing the OMR
#                 sheet and then the answers and found for each question.
# Return        : AnswerDict
################################################################################
def main(OMR_Name, InputImagePath):
    AnswerDict = {}

    # Read Input and resize it
    InputImage = cv2.imread(InputImagePath)
    InputImage = cv2.resize(InputImage, M.RESIZE_TO)
    
    # Crop OMR wrt bounding boxes
    CroppedOMR = CropOMR(InputImage)
    
    # Reading Config file
    NumOfQuestion, QuestionParam = ReadConfig(OMR_Name)

    for i in range(NumOfQuestion):
        Q = GA.FindAnswer(QuestionParam[i][1], QuestionParam[i][2], QuestionParam[i][3], QuestionParam[i][4], QuestionParam[i][5], QuestionParam[i][6], QuestionParam[i][7], QuestionParam[i][8], QuestionParam[i][9])
        AnswerDict[QuestionParam[i][0]] = Q.CropAnswer_MakeGrid_FindAnswer(CroppedOMR)

    # Extract different answers
    #AnswerDict = ExtractAnswers(CroppedOMR)
    print(AnswerDict)

    StoreInJSON(AnswerDict)
