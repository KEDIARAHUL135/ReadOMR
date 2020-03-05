###############################################################################
# File          : macros.py
# Created by    : Rahul Kedia
# Created on    : 10/01/2020
# Project       : ReadOMR
# Description   : This file contains the modifiable macros (variables)
#                 used in the main source code. By playing with these
#                 variables only, one can modify the main source code
#                 to adapt to different types of OMR Sheets and we can
#                 also enhance the output of the code.
################################################################################

import numpy as np
import src.GetAnswers as GA

# Input Image Path
InputImagePath = "InputImages/Filled1.1.jpeg"

# Size of OMR Sheet - square of length -> Size
Size = 800  # DONOT CHANGE THIS


# Thershold length of corner circle
## It means that the corner circle must be present at what max distance from the boundary(Keep this value small).
ThreshLengthCC = 90


# Macros for HoughCircle
dp = 1.3
MinRadius = 0
MaxRadius = 20


# Threshold Image at this value:
ThresholdImageAt = 75


# Rectangle Top Left Corner's Coordinates, length, and width for different answers.
class ROI_Answer:
    def __init__(self, Corner_X, Corner_Y, Width, Length):
        self.C_X = Corner_X
        self.C_Y = Corner_Y
        self.Width = Width
        self.Length = Length


StN = ROI_Answer(28, 49, 501, 464)              # Student's Name
MN = ROI_Answer(547, 236, 213, 182)             # Mobile Number
Class = ROI_Answer(586, 446, 155, 17)           # Class
Branch = ROI_Answer(82, 634, 649, 29)           # Branch
BN = ROI_Answer(549, 27, 213, 129)              # Booklet Number
ScN = ROI_Answer(125, 602, 606, 31)             # School's Name
Section = ROI_Answer(613, 478, 148, 38)         # Section
FN = ROI_Answer(124, 664, 607, 29)              # Father's Name
A_1t5 = ROI_Answer(64, 720, 85, 80)             # Answers - 1 to 5
A_6t10 = ROI_Answer(188, 722, 80, 80)           # Answers - 6 to 10
A_11t15 = ROI_Answer(309, 721, 79, 81)          # Answers - 11 to 15
A_16t20 = ROI_Answer(429, 721, 79, 81)          # Answers - 16 to 20
A_21t25 = ROI_Answer(549, 721, 80, 81)          # Answers - 21 to 25
A_26t30 = ROI_Answer(671, 722, 81, 80)          # Answers - 26 to 30


# List of alphabets and numbers
## Last character is '_' for empty answer(Blank space/No answer).
Alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',\
                    'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',\
                    'Y', 'Z', '_']
Numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_']


StN = GA.FindAnswer(28, 49, 501, 464, 25, 25, 'C', 0)              # Student's Name
MN = GA.FindAnswer(547, 236, 213, 182, 10, 10, 'C', 1)             # Mobile Number
Class = GA.FindAnswer(586, 446, 155, 17, 1, 7, 'R', 1, 4)           # Class
#Branch = GA.FindAnswer(82, 634, 649, 29)                           # Branch
#BN = GA.FindAnswer(549, 27, 213, 129)                              # Booklet Number
#ScN = GA.FindAnswer(125, 602, 606, 31)                             # School's Name
Section = GA.FindAnswer(613, 478, 148, 38, 2, 7, 'R', 0)           # Section
#FN = GA.FindAnswer(124, 664, 607, 29)                              # Father's Name
A_1t5 = GA.FindAnswer(64, 720, 85, 80, 5, 4, 'R', 0)               # Answers - 1 to 5
A_6t10 = GA.FindAnswer(188, 722, 80, 80, 5, 4, 'R', 0)             # Answers - 6 to 10
A_11t15 = GA.FindAnswer(309, 721, 79, 81, 5, 4, 'R', 0)            # Answers - 11 to 15
A_16t20 = GA.FindAnswer(429, 721, 79, 81, 5, 4, 'R', 0)            # Answers - 16 to 20
A_21t25 = GA.FindAnswer(549, 721, 80, 81, 5, 4, 'R', 0)            # Answers - 21 to 25
A_26t30 = GA.FindAnswer(671, 722, 81, 80, 5, 4, 'R', 0)            # Answers - 26 to 30


def GetAnswerString(AnswerDict, OMRImage):
    AnswerDict["Student's Name"] = StN.CropAnswer_MakeGrid_FindAnswer(OMRImage)
    AnswerDict["Mobile Number"] = MN.CropAnswer_MakeGrid_FindAnswer(OMRImage)
    AnswerDict["Class"] = Class.CropAnswer_MakeGrid_FindAnswer(OMRImage)
    AnswerDict["Section"] = Section.CropAnswer_MakeGrid_FindAnswer(OMRImage)
    AnswerDict["Answers 1-5"] = A_1t5.CropAnswer_MakeGrid_FindAnswer(OMRImage)
    AnswerDict["Answers 6-10"] = A_6t10.CropAnswer_MakeGrid_FindAnswer(OMRImage)
    AnswerDict["Answers 11-15"] = A_11t15.CropAnswer_MakeGrid_FindAnswer(OMRImage)
    AnswerDict["Answers 16-20"] = A_16t20.CropAnswer_MakeGrid_FindAnswer(OMRImage)
    AnswerDict["Answers 21-25"] = A_21t25.CropAnswer_MakeGrid_FindAnswer(OMRImage)
    AnswerDict["Answers 26-30"] = A_26t30.CropAnswer_MakeGrid_FindAnswer(OMRImage)

    return AnswerDict