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
import json

# Read Input and resize it
InputImage = cv2.imread(M.InputImagePath)
NewSize = (M.Size, M.Size)
InputImage = cv2.resize(InputImage, NewSize)


################################################################################
# Function      : HoughCircleDetection
# Parameter     : GrayImage - It contains gray scale image of Input Image
#                 BlurImage - It contains blur image of GrayImage
#                 Circles - It contains information of all the circles
#                           detected by HoughCircles function.
#                           Information is - [x-coordinate of centre,
#                              y-coordinate of centre, radius of circle]
# Description   : This function finds all the possible circles in the input
#                 image by using HoughCircles algorithm.
# Return        : Circles
################################################################################
def HoughCircleDetection():
    GrayImage = cv2.cvtColor(InputImage, cv2.COLOR_BGR2GRAY)
    BlurImage = cv2.medianBlur(GrayImage, 7)

    Circles = cv2.HoughCircles(BlurImage, cv2.HOUGH_GRADIENT, M.dp, 20,
                               param1=50, param2=30, minRadius=M.MinRadius, maxRadius=M.MaxRadius)
    Circles = np.uint16(np.around(Circles))

    return Circles


################################################################################
# Function      : FindCornerCircles
# Parameter     : Circles - It contains information of all the circles
#                           detected by HoughCircles function.
#                           Information is - [x-coordinate of centre,
#                              y-coordinate of centre, radius of circle]
#                 NumOfCCFound - It keeps the count of number of centre
#                                circles found in the image during
#                                filtering of circles.
#                 CornerCircles - It stores information of the corner
#                                 circles detected.
#                 FinalCornerCircles - It is a dummy variable used to add
#                           a dimension in CornerCircles to make it similar
#                           to the output circles array from HoughCircles algo.
# Description   : This function finds corner circles from the array of all
#                 the circles found by HoughCircleDetection.
# Return        : FinalCornerCircles
################################################################################
def FindCornerCircles(Circles):
    CornerCircles = np.zeros((4, 3), np.uint16())
    NumOfCCFound = 0

    for i in Circles[0]:
        if NumOfCCFound < 4:
            if ((i[0] <= M.ThreshLengthCC) & (i[1] <= M.ThreshLengthCC)).all():
                CornerCircles[NumOfCCFound] = i
                NumOfCCFound += 1
            elif ((i[0] <= M.ThreshLengthCC) & (i[1] >= (M.Size - M.ThreshLengthCC))).all():
                CornerCircles[NumOfCCFound] = i
                NumOfCCFound += 1
            elif ((i[0] >= (M.Size - M.ThreshLengthCC)) & (i[1] <= M.ThreshLengthCC)).all():
                CornerCircles[NumOfCCFound] = i
                NumOfCCFound += 1
            elif ((i[0] >= (M.Size - M.ThreshLengthCC)) & (i[1] >= (M.Size - M.ThreshLengthCC))).all():
                CornerCircles[NumOfCCFound] = i
                NumOfCCFound += 1
        else:
            break

    FinalCornerCircles = np.zeros((1, 4, 3), np.uint16())
    FinalCornerCircles[0] = CornerCircles

    return FinalCornerCircles


################################################################################
# Function      : ExpandInitialPoints
# Parameter     : InitialPoints - It contains the initial coordinates of
#                                 four corner circles in clockwise order
#                                 starting from top left.
# Description   : This function corrects the value of InitialPoints parameter
#                 if and as required to expand the image after corner detection
#                 for cropping.
# Return        : InitialPoints
################################################################################
def ExpandInitialPoints(InitialPoints):
    for k in range(4):
        if (k//2) == 0:
            InitialPoints[k % 4][k % 2] -= M.EXPAND_BY[k]
            InitialPoints[(k - 1) % 4][k % 2] -= M.EXPAND_BY[k]
        else:
            InitialPoints[k % 4][k % 2] += M.EXPAND_BY[k]
            InitialPoints[(k - 1) % 4][k % 2] += M.EXPAND_BY[k]

    return InitialPoints

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
def ProjectiveTransform(CornerCircles):
    # Finding initial coordinates of 4 corner circles
    InitialPoints = np.zeros((4, 2), np.float32)

    for i in CornerCircles[0]:
        # Top two
        if i[1] <= M.ThreshLengthCC:
            ## Top Left
            if i[0] <= M.ThreshLengthCC:
                InitialPoints[0][0] = i[0]
                InitialPoints[0][1] = i[1]
            ## Top Right
            else:
                InitialPoints[1][0] = i[0]
                InitialPoints[1][1] = i[1]

        # Bottom two
        else:
            ## Bottom Left
            if i[0] <= M.ThreshLengthCC:
                InitialPoints[3][0] = i[0]
                InitialPoints[3][1] = i[1]
            ## Bottom Right
            else:
                InitialPoints[2][0] = i[0]
                InitialPoints[2][1] = i[1]

    if M.EXPAND_INITIAL_POINTS == 1:
        ExpandInitialPoints(InitialPoints)

    # Final coordinates of 4 corner circles in another image
    FinalPoints = np.float32([[0., 0.], [(M.Size - 1), 0.],
                              [(M.Size - 1), (M.Size - 1)],
                              [0., (M.Size - 1)]])

    # Applying projective transform
    ProjectiveMatrix = cv2.getPerspectiveTransform(InitialPoints, FinalPoints)
    OutputImage = cv2.warpPerspective(InputImage, ProjectiveMatrix, NewSize)

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
    # Extract the corner four circle's centre point
    ## Apply Hough Circle Detection
    Circles = HoughCircleDetection()

    ## Filter circles according to their position. We are interested in corner circles only
    CornerCircles = FindCornerCircles(Circles)

    # Applying Projective transformation.
    CroppedOMRSheetImage = ProjectiveTransform(CornerCircles)

    # Extract different answers
    AnswerDict = ExtractAnswers(CroppedOMRSheetImage)

    print(AnswerDict)

    StoreInJSON(AnswerDict)


# Crop the required OMR sheet for answer detection
CropOMR_FindAnswers()
cv2.waitKey(0)
