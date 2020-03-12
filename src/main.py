###############################################################################
# File          : main.py
# Created by    : Rahul Kedia
# Created on    : 09/01/2020
# Project       : ReadOMR
# Description   : This file contains the main source code for the project.
################################################################################

import cv2
import numpy as np
import src.macros as M
from src.FindBoundingRect import FindBoundingBoxes
import json

# Read Input and resize it
InputImage = cv2.imread(M.InputImagePath)
NewSize = (M.Size, M.Size)
InputImage = cv2.resize(InputImage, NewSize)


################################################################################
# Function      : SetCoordinatesOfCornerGuidingBoxes
# Parameter     : InitialCorners - It contains the initial coordinates of 4
#                             corners in clockwise order starting from top left.
#                 FinalCorners - It contains the final coordinates of the 4
#                           corners in the same order as that of InitialCorners.
# Description   : This sets the Initial and Final coordinates of the guiding
#                 corner boxes.
# Return        : InitialCorners, FinalCorners
################################################################################
def SetCoordinatesOfCornerGuidingBoxes(LeftGuidingBoxes, RightGuidingBoxes):
    InitialCorners = np.float32([[(LeftGuidingBoxes[0][0] + LeftGuidingBoxes[0][2])//2, (LeftGuidingBoxes[0][1] + LeftGuidingBoxes[0][3])//2],
                                 [(RightGuidingBoxes[0][0] + RightGuidingBoxes[0][2])//2, (RightGuidingBoxes[0][1] + RightGuidingBoxes[0][3])//2],
                                 [(RightGuidingBoxes[-1][0] + RightGuidingBoxes[-1][2])//2, (RightGuidingBoxes[-1][1] + RightGuidingBoxes[-1][3])//2],
                                 [(LeftGuidingBoxes[-1][0] + LeftGuidingBoxes[-1][2])//2, (LeftGuidingBoxes[-1][1] + LeftGuidingBoxes[-1][3])//2]])


    # Final coordinates of 4 corner circles in another image
    FinalCorners = np.float32([[0., 0.],
                               [(M.Size - 1), 0.],
                               [(M.Size - 1), (M.Size - 1)],
                               [0., (M.Size - 1)]])

    if M.EXPAND_INITIAL_POINTS:
        ExpandInitialCorners(InitialCorners)

    return InitialCorners, FinalCorners


################################################################################
# Function      : ExpandInitialCorners
# Parameter     : InitialCorners - It contains the initial coordinates of 4
#                             corners in clockwise order starting from top left.
# Description   : This function corrects the value of InitialCorners parameter
#                 if and as required to expand the image after corner detection
#                 for cropping.
# Return        : InitialCorners
################################################################################
def ExpandInitialCorners(InitialCorners):
    for k in range(4):
        if (k//2) == 0:
            InitialCorners[k % 4][k % 2] -= M.EXPAND_BY[k]
            InitialCorners[(k - 1) % 4][k % 2] -= M.EXPAND_BY[k]
        else:
            InitialCorners[k % 4][k % 2] += M.EXPAND_BY[k]
            InitialCorners[(k - 1) % 4][k % 2] += M.EXPAND_BY[k]

    return InitialCorners


################################################################################
# Function      : ProjectiveTransform
# Parameter     : CornerCircles - It stores information of the corner
#                                 circles detected.
#                 OutputImage - It is the image of cropped OMR Sheet. It is
#                               cropped in rectangle with the help of four
#                               printed corner circles of the OMR Sheet.
#                 InitialPoints - It contains the initial coordinates of
#                                 four corner circles in clockwise order
#                                 starting from top left.
#                 FinalPoints - It contains the final coordinates of
#                               four corner circles in clockwise order
#                               starting from top left.
# Description   : This function calls suitable functions one by one for
#                 detecting circles, and the rearranging/resizing the OMR
#                 sheet so that then the answers can be found from OMR Sheet.
# Return        : OutputImage
################################################################################
def ProjectiveTransform(InitialCorners, FinalCorners):
    # Applying projective transform
    ProjectiveMatrix = cv2.getPerspectiveTransform(InitialCorners, FinalCorners)
    OutputImage = cv2.warpPerspective(InputImage, ProjectiveMatrix, NewSize)
    cv2.imshow("Image", OutputImage)
    return OutputImage


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
        json.dump(AnswerDict, outfile, indent=4)


################################################################################
# Function      : CropOMR_FindAnswers
# Parameter     : Circles - It contains information of all the circles
#                           detected by HoughCircles function.
#                           Information is - [x-coordinate of centre,
#                              y-coordinate of centre, radius of circle].
#                 CornerCircles - It stores information of the corner
#                                 circles detected.
#                 CroppedOMRSheetImage - It is the image of cropped OMR Sheet.
#                                        It is cropped in rectangle with the
#                                        help of four printed corner circles
#                                        of the OMR Sheet.
#                 AnswerDict - It is the answer dictionary for each question.
# Description   : This function calls suitable functions one by one for
#                 detecting circles, and the rearranging/resizing the OMR
#                 sheet and then the answers and found for each question.
# Return        : AnswerDict
################################################################################
def CropOMR_FindAnswers():

    LeftGuidingBoxes, RightGuidingBoxes = FindBoundingBoxes(M.InputImagePath, NewSize)

    InitialCorners, FinalCorners = SetCoordinatesOfCornerGuidingBoxes(LeftGuidingBoxes, RightGuidingBoxes)
    # Applying Projective transformation.
    CroppedOMRSheetImage = ProjectiveTransform(InitialCorners, FinalCorners)

    # Extract different answers
    AnswerDict = ExtractAnswers(CroppedOMRSheetImage)

    print(AnswerDict)

    StoreInJSON(AnswerDict)


# Crop the required OMR sheet for answer detection
CropOMR_FindAnswers()
cv2.waitKey(0)
