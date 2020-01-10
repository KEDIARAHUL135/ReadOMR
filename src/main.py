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


class Answers:
    def __init__(self, StN, MN, Class, Branch, BN, ScN, Section, FN, A_1t5, A_6t10,\
                 A_11t15, A_16t20, A_21t25, A_26t30, OMRImage):
        self.Img = OMRImage
        self.StN = self.Img[StN.C_Y:StN.C_Y + StN.Length, StN.C_X:StN.C_X + StN.Width]
        self.MN = self.Img[MN.C_Y:MN.C_Y + MN.Length, MN.C_X:MN.C_X + MN.Width]
        self.Class = self.Img[Class.C_Y:Class.C_Y + Class.Length, Class.C_X:Class.C_X + Class.Width]
        self.Branch = self.Img[Branch.C_Y:Branch.C_Y + Branch.Length, Branch.C_X:Branch.C_X + Branch.Width]
        self.BN = self.Img[BN.C_Y:BN.C_Y + BN.Length, BN.C_X:BN.C_X + BN.Width]
        self.ScN = self.Img[ScN.C_Y:ScN.C_Y + ScN.Length, ScN.C_X:ScN.C_X + ScN.Width]
        self.Section = self.Img[Section.C_Y:Section.C_Y + Section.Length, Section.C_X:Section.C_X + Section.Width]
        self.FN = self.Img[FN.C_Y:FN.C_Y + FN.Length, FN.C_X:FN.C_X + FN.Width]
        self.A_1t5 = self.Img[A_1t5.C_Y:A_1t5.C_Y + A_1t5.Length, A_1t5.C_X:A_1t5.C_X + A_1t5.Width]
        self.A_6t10 = self.Img[A_6t10.C_Y:A_6t10.C_Y + A_6t10.Length, A_6t10.C_X:A_6t10.C_X + A_6t10.Width]
        self.A_11t15 = self.Img[A_11t15.C_Y:A_11t15.C_Y + A_11t15.Length, A_11t15.C_X:A_11t15.C_X + A_11t15.Width]
        self.A_16t20 = self.Img[A_16t20.C_Y:A_16t20.C_Y + A_16t20.Length, A_16t20.C_X:A_16t20.C_X + A_16t20.Width]
        self.A_21t25 = self.Img[A_21t25.C_Y:A_21t25.C_Y + A_21t25.Length, A_21t25.C_X:A_21t25.C_X + A_21t25.Width]
        self.A_26t30 = self.Img[A_26t30.C_Y:A_26t30.C_Y + A_26t30.Length, A_26t30.C_X:A_26t30.C_X + A_26t30.Width]


def ExtractAnswers(OMRImage):
    AnsImages = Answers(M.StN, M.MN, M.Class, M.Branch, M.BN, M.ScN, M.Section, M.FN, M.A_1t5,\
                  M.A_6t10, M.A_11t15, M.A_16t20, M.A_21t25, M.A_26t30, OMRImage)


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
