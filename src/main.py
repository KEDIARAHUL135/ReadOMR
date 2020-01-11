###############################################################################
# File          : main.py
# Created by    : Rahul Kedia
# Created on    : 09/01/2020
# Project       : ReadOMR
# Description   : This file contains the main source code for the project.
################################################################################

import cv2
import numpy as np
#import matplotlib as plt
import src.macros as M


# Read Input and resize it
InputImage = cv2.imread(M.InputImagePath)
NewSize = (M.Size, M.Size)
InputImage = cv2.resize(InputImage, NewSize)


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


class GetAnswer:
    Alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',\
                    'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',\
                    'Y', 'Z']

    def __init__(self, Image, NumOfRows, NumOfCols, By_CorR, Alp_or_Num):
        self.Image = Image
        self.NumOfRows = NumOfRows
        self.NumOfCols = NumOfCols
        self.By_CorR = By_CorR
        self.Alp_or_Num = Alp_or_Num
        self.HistogramMatrix = np.zeros((NumOfRows, NumOfCols), dtype=int)

    def ThresholdImage(self):
        self.Image = cv2.cvtColor(self.Image, cv2.COLOR_BGR2GRAY)
        ret, self.Image = cv2.threshold(self.Image, 75, 255, cv2.THRESH_BINARY)

        cv2.imshow("Thresholded", self.Image)


    def FindHistogram(self, i, j, WidthOfGrid, HeightOfGrid):
        GridImage = self.Image[j:j+HeightOfGrid, i:i+WidthOfGrid]
        Height, Width = GridImage.shape[:2]
        NumOfWhite = NumOfBlack = 0

        for i in range(Width):
            for j in range(Height):
                if GridImage[j, i] == 255:
                    NumOfWhite += 1
                else:
                    NumOfBlack += 1

        return NumOfWhite, NumOfBlack

    def FindFinalAnswer(self, HistMatrix):
        AnswerString = ""

        # Finding max index for all col/row in HistMatrix
        MaxIndex = np.zeros(HistMatrix.shape[1], dtype=int)

        for i in range(self.NumOfCols):
            IndexOfMax = Max = 0
            for j in range(self.NumOfRows):
                if Max < HistMatrix[j, i]:
                    Max = HistMatrix[j, i]
                    IndexOfMax = j
            MaxIndex[i] = IndexOfMax

        print(MaxIndex)

        print(AnswerString)


    def MakeGrid(self):
        self.ThresholdImage()

        Height, Width = self.Image.shape[:2]
        WidthOfGrid = (Width//self.NumOfCols)
        HeightOfGrid = (Height//self.NumOfRows)
        RemainderOfWidth = ((Width/self.NumOfCols) - WidthOfGrid)
        RemainderOfHeight = ((Height/self.NumOfRows) - HeightOfGrid)
        WidthPixelSkipped = 0
        HeightPixelSkipped = 0
        HistMatrix = np.zeros((self.NumOfRows, self.NumOfCols), dtype=int)
        HistMatrix_i = HistMatrix_j = 0


        for i in range(0, Width, WidthOfGrid):
            WidthPixelSkipped += RemainderOfWidth
            while (WidthPixelSkipped >= 1):
                WidthPixelSkipped -= 1
                i += 1

            HistMatrix_j = 0
            for j in range(0, Height, HeightOfGrid):
                HeightPixelSkipped += RemainderOfHeight
                while (HeightPixelSkipped >= 1):
                    HeightPixelSkipped -= 1
                    j += 1

                #cv2.rectangle(self.Image, (i, j), (i+WidthOfGrid, j+HeightOfGrid), (0, 255, 0), 1)
                NumOfWhite, NumOfBlack = self.FindHistogram(i, j, WidthOfGrid, HeightOfGrid)

                HistMatrix[HistMatrix_j, HistMatrix_i] = NumOfBlack

                HistMatrix_j += 1

                if HistMatrix_j >= self.NumOfRows:
                    break

            HistMatrix_i += 1
            if HistMatrix_i >= self.NumOfCols:
                break

        self.FindFinalAnswer(HistMatrix)

        cv2.imshow("GridImage", self.Image)
        cv2.waitKey(0)





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
# Function      : PrintImages
# Parameter     : CornerCircles - It stores information of the corner
#                                 circles detected.
#                 PrintCC - It is a flag for printing Corner Circles
#                 AnsImages - It is a object of class Answers passed
#                             to this function
# Description   : This function prints the images as required.
# Return        : -
################################################################################
def PrintImages(CornerCircles = None, PrintCC = None, AnsImages = None):
    # Printing corner circles
    if PrintCC != None:
        for i in CornerCircles[0, :]:
            # draw the outer circle
            cv2.circle(InputImage, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(InputImage, (i[0], i[1]), 2, (0, 0, 255), 3)

        cv2.imshow('Detected Corner Circles', InputImage)

    # Printing Answer Images
    if AnsImages != None:
        cv2.imshow("1", AnsImages.StN)
        cv2.imshow("2", AnsImages.MN)
        cv2.imshow("3", AnsImages.Class)
        cv2.imshow("4", AnsImages.Branch)
        cv2.imshow("5", AnsImages.BN)
        cv2.imshow("6", AnsImages.ScN)
        cv2.imshow("7", AnsImages.Section)
        cv2.imshow("8", AnsImages.FN)
        cv2.imshow("9", AnsImages.A_1t5)
        cv2.imshow("10", AnsImages.A_6t10)
        cv2.imshow("11", AnsImages.A_11t15)
        cv2.imshow("12", AnsImages.A_16t20)
        cv2.imshow("13", AnsImages.A_21t25)
        cv2.imshow("14", AnsImages.A_26t30)


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
    AnsImages = Answers(M.StN, M.MN, M.Class, M.Branch, M.BN, M.ScN, M.Section, M.FN, M.A_1t5,\
                  M.A_6t10, M.A_11t15, M.A_16t20, M.A_21t25, M.A_26t30, OMRImage)

    #PrintImages(AnsImages= AnsImages)    # Uncomment to see all the answer images

    StN = GetAnswer(AnsImages.StN, 26, 25, 'C', 0)
    MN = GetAnswer(AnsImages.MN, 10, 10, 'C', 1)
    Class = GetAnswer(AnsImages.Class, 1, 7, 'R', 1)
    Section = GetAnswer(AnsImages.Section, 2, 7, 'R', 0)
    A_1t5 = GetAnswer(AnsImages.A_1t5, 5, 4, 'R', 0)
    A_6t10 = GetAnswer(AnsImages.A_6t10, 5, 4, 'R', 0)
    A_11t15 = GetAnswer(AnsImages.A_11t15, 5, 4, 'R', 0)
    A_16t20 = GetAnswer(AnsImages.A_16t20, 5, 4, 'R', 0)
    A_21t25 = GetAnswer(AnsImages.A_21t25, 5, 4, 'R', 0)
    A_26t30 = GetAnswer(AnsImages.A_26t30, 5, 4, 'R', 0)

    StN.MakeGrid()
    MN.MakeGrid()
    Class.MakeGrid()
    Section.MakeGrid()
    A_1t5.MakeGrid()
    A_6t10.MakeGrid()
    A_11t15.MakeGrid()
    A_16t20.MakeGrid()
    A_21t25.MakeGrid()
    A_26t30.MakeGrid()


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
    # PrintImages(CornerCircles, True)      # Uncomment to print corner circles

    # Applying Projective transformation.
    CroppedOMRSheetImage = ProjectiveTransform(CornerCircles)

    cv2.imshow("PerfectOMR", CroppedOMRSheetImage)

    # Extract different answers
    ExtractAnswers(CroppedOMRSheetImage)


# Crop the required OMR sheet for answer detection
CropReqOMR()

cv2.waitKey(0)
