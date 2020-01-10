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
#                           a dimention in CornerCircles to make it similar
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
# Function      : PrintCornerCircles
# Parameter     : CornerCircles - It stores information of the corner
#                                 circles detected.
# Description   : This function prints the corner circles on the image.
# Return        : FinalCornerCircles
################################################################################
def PrintCornerCircles(CornerCircles):
    for i in CornerCircles[0, :]:
        # draw the outer circle
        cv2.circle(InputImage, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(InputImage, (i[0], i[1]), 2, (0, 0, 255), 3)

    cv2.imshow('Detected Corner Circles', InputImage)


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
# Return        : -
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

    # Final coordinates of 4 corner circles in another image
    FinalPoints = np.float32([[0., 0.], [(M.Size - 1), 0.],\
                              [(M.Size - 1), (M.Size - 1)], [0., (M.Size - 1)]])

    # Applying projective transform
    ProjectiveMatrix = cv2.getPerspectiveTransform(InitialPoints, FinalPoints)
    OutputImage = cv2.warpPerspective(InputImage, ProjectiveMatrix, NewSize)

    return OutputImage


def ExtractAnswers(OMRImage):
    # All the coordinates of answers are stored in macros.py file.
    roi = OMRImage[51:511, 30:527]
    cv2.imshow("roi", roi)
    Image = cv2.rectangle(OMRImage, (30, 51), (526, 510), (0, 200, 0), 3)
    cv2.imshow("Image", Image)


################################################################################
# Function      : CropReqOMR
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
# Description   : This function calls suitable functions one by one for
#                 detecting circles, and the rearranging/resizing the OMR
#                 sheet so that then the answers can be found from OMR Sheet.
# Return        : -
################################################################################
def CropReqOMR():
    # Extract the corner four circle's centre point
    ## Apply Hough Circle Detection
    Circles = HoughCircleDetection()

    ## Filter circles according to their position. We are interested in corner circles only
    CornerCircles = FindCornerCircles(Circles)

    ## Print corner circles
    # PrintCornerCircles(CornerCircles)      # Uncomment to print corner circles

    # Applying Projective transformation.
    CroppedOMRSheetImage = ProjectiveTransform(CornerCircles)

    cv2.imshow("PerfectOMR", CroppedOMRSheetImage)

    # Extract different answers
    ExtractAnswers(CroppedOMRSheetImage)


# Crop the required OMR sheet for answer detection
CropReqOMR()

cv2.waitKey(0)
