###############################################################################
# File          : altToCornerCircles.py
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
Image = cv2.imread("InputImages/Blank1.jpg")
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
    UpperRange = np.array([0, 0, 130])

    MaskedImage = cv2.inRange(HSVImage, LowerRange, UpperRange)

    cv2.imshow("Masked", MaskedImage)

    return MaskedImage

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
# Function      : FilterRectCoordinates
# Parameter     : RectCoordinates - It contains the coordinates of top left
#                                   corner and bottom right corner of the
#                                   rectangles as a list of list.
#                 DeleteElementIndex - It contains the elements of RectCoordinates
#                                      which needs to be deleted.
# Description   : This function finds the coordinates of almost same rectangle
#                 in the list RectCoordinates and if found same which some
#                 threshold, it stores those elements in a list and then finally
#                 deletes them one by one from the last.
# Return        : RectCoordinates
################################################################################
def FilterRectCoordinates(RectCoordinates):
    DeleteElementIndex = []

    for i in range(1, len(RectCoordinates)):
        # Sum1 & Sum2 contain the sum of all the elements of both the coordinates
        # of a consecutive rectangles.
        Sum1 = 0
        Sum2 = 0
        for j in RectCoordinates[i-1]:
            Sum1 = Sum1 + j
        for j in RectCoordinates[i]:
            Sum2 = Sum2 + j

        Difference = Sum1 - Sum2

        # Rectangles are considered same if Difference is between -5 to +5.
        # This threshold is to be modified
        if -10 <= Difference <= 10:
            DeleteElementIndex.append(i-1)

    # List is reversed so that while deleting elements, they are deleted from last.
    DeleteElementIndex.reverse()

    # Deleting elements
    for i in DeleteElementIndex:
        del RectCoordinates[i]

    return RectCoordinates


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
TempImage = MaskedImage[36:44, 15:32]
cv2.imshow("TempImage", TempImage)

RectCoordinates = TemplateMatching(MaskedImage, TempImage, Image)

FinalRectCoordinates = FilterRectCoordinates(RectCoordinates)

GuidingBoxes = FindGuidingBoxes(FinalRectCoordinates)

for i in GuidingBoxes:
    #cv2.rectangle(Image, (i[0], i[1]), (i[2], i[3]), (0, 0, 255), 2)
    print(i)

GuidingBoxesCenter = CenterOfGuidingBoxes(GuidingBoxes)

for i in GuidingBoxesCenter:
    cv2.circle(Image, i, 2, (0, 0, 255), -1)
    print(i)

cv2.imshow("GuidingCentre", Image)

cv2.waitKey(0)
cv2.destroyAllWindows()
