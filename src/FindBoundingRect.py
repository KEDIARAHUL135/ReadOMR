###############################################################################
# File          : FindBoundingRect.py
# Created by    : Rahul Kedia
# Created on    : 06/03/2020
# Project       : ReadOMR
# Description   : This file aims to find the alternative of the corner circles
#                 with reference to which we do projective transform on the
#                 image. It is seen that in most of the cases, corner circles
#                 are not provided but instead we have horizontal small blocks
#                 along both of the verticle edges of the OMR Sheet.
################################################################################

import numpy as np
import cv2
from matplotlib import pyplot as plt


# Read and resize Input OMR Image
Image = cv2.imread("InputImages/Blank3.jpeg")
Image = cv2.resize(Image, (int(Image.shape[1]*0.8), int(Image.shape[0]*0.8)))
cv2.imshow("Input", Image)


################################################################################
# Function      : MaskImage
# Parameter     : Image - It contains Input OMR Image.
#                 HSVImage - It contains HSV of input OMR image.
#                 LowerRange, UpperRange - They mention the range used to
#                         extract horizontal block near the edges(Black colour).
#                 MaskedImage - It contains the Masked Image.
# Description   : This function masks the input OMR image for black colour.
# Return        : MaskedImage
################################################################################
def MaskImage(Image):
    HSVImage = cv2.cvtColor(Image, cv2.COLOR_BGR2HSV)

    LowerRange = np.array([0, 0, 0])
    UpperRange = np.array([255, 255, 100])

    MaskedImage = cv2.inRange(HSVImage, LowerRange, UpperRange)

    MaskedBlurImage = cv2.GaussianBlur(MaskedImage, (3, 3), 0)

    cv2.imshow("Masked", MaskedBlurImage)

    return MaskedBlurImage

################################################################################
# Function      : TemplateMatching
# Parameter     : MaskedImage - It contains the Masked Image.
#                 TemplateImage - It contains template image of horizontal
#                                 rectangles to be found.
#                 OMRImage - It contains input OMR Image.
#                 RectCoordinates - It contains the coordinates of top left
#                                   corner and bottom right corner of the
#                                   rectangles as a list of list.
#                 {Rest all the parameters ate copied from the link given
#                 and are self explanatory.}
# Description   : This function matches the template image o the masked Image
#                 to find the horizontal rectangles and returns the list of
#                 rectangles detected.
# Return        : RectCoordinates
################################################################################
def TemplateMatching(MaskedImage, TemplateImage, OMRImage):
    RectCoordinates = []

    # Code copied from -
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html

    if (len(MaskedImage.shape)) == 3:
        img_gray = cv2.cvtColor(MaskedImage, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = MaskedImage

    if len(TemplateImage.shape) == 3:
        template = cv2.cvtColor(TemplateImage, cv2.COLOR_BGR2GRAY)
    else:
        template = TemplateImage


    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        RectCoordinates.append([pt[0], pt[1], (pt[0] + w), (pt[1] + h)])
        #cv2.rectangle(OMRImage, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

    return RectCoordinates


################################################################################
# Function      : IntersectingArea
# Parameter     : {Self explanatory}
# Description   : This function checks if there is some intersecting area
#                 between 2 rectangles.
# Return        : True - If intersecting area is present.
#                 False - If intersecting area is absent.
################################################################################
def IntersectingArea(Rect1, Rect2):
    Diff_X = min(Rect1[2], Rect2[2]) - max(Rect1[0], Rect2[0])
    Diff_Y = min(Rect1[3], Rect2[3]) - max(Rect1[1], Rect2[1])
    if Diff_X >= 0 and Diff_Y >= 0:
        return True
    else:
        return False


################################################################################
# Function      : FilterRectCoordinates
# Parameter     : RectCoordinates - It contains the coordinates of top left
#                                   corner and bottom right corner of the
#                                   rectangles as a list of list.
#                 LengthOfRectCoordinates - Stores the length of RectCoordinates.
#                 FoundIntersectingArea - Flag of whether Intersecting area is
#                                         found or not.
#                 Rect1, Rect2 - Stores 2 rectangles to be compared.
#                 FinalRectCoordinates - Final list of rectangles which donot
#                                        have any intersecting rectangles.
# Description   : This function finds the intersecting area of 2 rectangles
#                 from the list RectCoordinates and if no intersecting rectangle
#                 is found, it stores the rectangle in FinalRectCoordinates.
# Return        : FinalRectCoordinates
################################################################################
def FilterRectCoordinates(RectCoordinates):
    FinalRectCoordinates = []

    LengthOfRectCoordinates = len(RectCoordinates)

    for I in range(LengthOfRectCoordinates):
        FoundIntersectingArea = 0
        Rect1 = RectCoordinates[I].copy()

        for J in range(I+1, LengthOfRectCoordinates):
            Rect2 = RectCoordinates[J].copy()

            if IntersectingArea(Rect1, Rect2) is True:
                FoundIntersectingArea = 1
                break

        if FoundIntersectingArea == 0:
            FinalRectCoordinates.append(RectCoordinates[I])

    return FinalRectCoordinates


################################################################################
# Function      : FindGuidingBoxes
# Parameter     : RectCoordinates - It contains the coordinates of top left
#                                   corner and bottom right corner of the
#                                   rectangles as a list of list.
#                 GuidingBoxes - It contains coordinates of top left
#                                corner and bottom right corner of the four
#                                corner rectangles as a list of list in the
#                                clockwise fashion starting from top left
#                                rectangle.
# Description   : This function finds the 4 corner rectangle coordinates from
#                 RectCoordinates list.
# Return        : GuidingBoxes
################################################################################
def FindGuidingBoxes(RectCoordinates):
    # Sorting wrt y coordinate of top left corner so that top values are for rectangles
    # at the top and last values depict value for rectangles at the bottom.
    sorted(RectCoordinates, key=lambda l:l[1])

    # In this loop it is made sure that first 2 values are for top 2 rectangles
    # (left and right) and last 2 values are for bottom 2 rectangles(left and right).
    while 1:
        # For first 2 values
        if -10 <= (RectCoordinates[0][0] - RectCoordinates[1][0]) <= 10:
            del RectCoordinates[1]
        # For last 2 values
        elif -10 <= (RectCoordinates[-1][0] - RectCoordinates[-2][0]) <= 10:
            del RectCoordinates[-2]
        # Break if done
        else:
            break

    # GuidingBoxes value is set by filtering rectangles in a cyclic
    # order starting from top left rectangle.
    if RectCoordinates[0][0] < RectCoordinates[1][0]:
        if RectCoordinates[-1][0] < RectCoordinates[-2][0]:
            GuidingBoxes = [RectCoordinates[0], RectCoordinates[1],
                            RectCoordinates[-2], RectCoordinates[-1]]
        else:
            GuidingBoxes = [RectCoordinates[0], RectCoordinates[1],
                            RectCoordinates[-1], RectCoordinates[-2]]
    else:
        if RectCoordinates[-1][0] < RectCoordinates[-2][0]:
            GuidingBoxes = [RectCoordinates[1], RectCoordinates[0],
                            RectCoordinates[-2], RectCoordinates[-1]]
        else:
            GuidingBoxes = [RectCoordinates[1], RectCoordinates[0],
                            RectCoordinates[-1], RectCoordinates[-2]]

    return GuidingBoxes


################################################################################
# Function      : CenterOfGuidingBoxes
# Parameter     : GuidingBoxesCenter - It contains the coordinates of centre of
#                                   guiding/corner rectangles found.
#                 GuidingBoxes - It contains coordinates of top left
#                                corner and bottom right corner of the four
#                                corner rectangles as a list of list in the
#                                clockwise fashion starting from top left
#                                rectangle.
# Description   : This function finds the centre of 4 corner rectangle found.
# Return        : GuidingBoxesCenter
################################################################################
def CenterOfGuidingBoxes(GuidingBoxes):
    GuidingBoxesCenter = []

    for i in GuidingBoxes:
        Center = ((i[0] + i[2])//2, (i[1] + i[3])//2)
        GuidingBoxesCenter.append(Center)

    return GuidingBoxesCenter


#=======================================================================================
MaskedImage = MaskImage(Image)

# Finds the template image. This needs to be changed at last.
TempImage = cv2.imread("TemplateImage.png")
cv2.imshow("TemplateImage", TempImage)
TemplateSize = TempImage.shape

for i in range(3):
    TempImage = cv2.resize(TempImage, (TemplateSize[1]+i, TemplateSize[0]+i))
    RectCoordinates = TemplateMatching(MaskedImage, TempImage, Image)

    FinalRectCoordinates = FilterRectCoordinates(RectCoordinates)

    #GuidingBoxes = FindGuidingBoxes(RectCoordinates)

    print(FinalRectCoordinates)
    for i in FinalRectCoordinates:
        cv2.rectangle(Image, (i[0], i[1]), (i[2], i[3]), (0, 0, 255), 1)
        #print(i)

    #GuidingBoxesCenter = CenterOfGuidingBoxes(GuidingBoxes)

    #for i in GuidingBoxesCenter:
        #cv2.circle(Image, i, 2, (0, 255, 0), -1)
        #print(i)

    cv2.imshow("GuidingCentre", Image)
    cv2.waitKey(0)

for i in range(3):
    TempImage = cv2.resize(TempImage, (TemplateSize[1] - i, TemplateSize[0] - i))
    RectCoordinates = TemplateMatching(MaskedImage, TempImage, Image)

    FinalRectCoordinates = FilterRectCoordinates(RectCoordinates)

    # GuidingBoxes = FindGuidingBoxes(RectCoordinates)

    print(FinalRectCoordinates)
    for i in FinalRectCoordinates:
        cv2.rectangle(Image, (i[0], i[1]), (i[2], i[3]), (0, 0, 255), 1)
        # print(i)

    # GuidingBoxesCenter = CenterOfGuidingBoxes(GuidingBoxes)

    # for i in GuidingBoxesCenter:
        # cv2.circle(Image, i, 2, (0, 255, 0), -1)
        # print(i)

    cv2.imshow("GuidingCentre", Image)

    cv2.waitKey(0)
cv2.destroyAllWindows()
