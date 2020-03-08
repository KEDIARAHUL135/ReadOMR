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
import time

t1 = time.time()
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
    UpperRange = np.array([255, 255, 100])

    MaskedImage = cv2.inRange(HSVImage, LowerRange, UpperRange)

    MaskedBlurImage = cv2.GaussianBlur(MaskedImage, (3, 3), 0)

    cv2.imshow("Masked", MaskedBlurImage)

    return MaskedBlurImage

################################################################################
# Function      : TemplateMatching
# Parameter     : MaskedImage - It contains the Masked Image.
#                 TemplateImage - It contains template image of horizontal
#                                 boxes to be found.
#                 OMRImage - It contains input OMR Image.
#                 BoxCoordinates - It contains the coordinates of top left
#                                   corner and bottom right corner of the
#                                   boxes as a list of list.
#                 {Rest all the parameters ate copied from the link given
#                 and are self explanatory.}
# Description   : This function matches the template image o the masked Image
#                 to find the horizontal boxes and returns the list of
#                 boxes detected.
# Return        : BoxCoordinates
################################################################################
def TemplateMatching(MaskedImage, TemplateImage, OMRImage):
    BoxCoordinates = []

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
        BoxCoordinates.append([pt[0], pt[1], (pt[0] + w), (pt[1] + h)])
        #cv2.rectangle(OMRImage, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

    return BoxCoordinates


################################################################################
# Function      : IntersectingArea
# Parameter     : {Self explanatory}
# Description   : This function checks if there is some intersecting area
#                 between 2 rectangles/boxes.
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
# Function      : FilterBoxCoordinates
# Parameter     : BoxCoordinates - It contains the coordinates of top left
#                                   corner and bottom right corner of the
#                                   boxes as a list of list.
#                 LengthOfBoxCoordinates - Stores the length of BoxCoordinates.
#                 FoundIntersectingArea - Flag of whether Intersecting area is
#                                         found or not.
#                 Rect1, Rect2 - Stores 2 rectangles to be compared.
#                 FinalBoxCoordinates - Final list of boxes which donot
#                                        have any intersecting boxes.
# Description   : This function finds the intersecting area of 2 boxes
#                 from the list BoxCoordinates and if no intersecting box
#                 is found, it stores the box in FinalBoxCoordinates.
# Return        : FinalBoxCoordinates
################################################################################
def FilterBoxCoordinates(BoxCoordinates):
    FinalBoxCoordinates = []

    LengthOfBoxCoordinates = len(BoxCoordinates)

    for I in range(LengthOfBoxCoordinates):
        FoundIntersectingArea = 0
        Rect1 = BoxCoordinates[I].copy()

        for J in range(I+1, LengthOfBoxCoordinates):
            Rect2 = BoxCoordinates[J].copy()

            if IntersectingArea(Rect1, Rect2) is True:
                FoundIntersectingArea = 1
                break

        if FoundIntersectingArea == 0:
            FinalBoxCoordinates.append(BoxCoordinates[I])

    return FinalBoxCoordinates


################################################################################
# Function      : FindGuidingBoxes
# Parameter     : BoxCoordinates - It contains the coordinates of top left
#                                   corner and bottom right corner of the
#                                   Boxes as a list of list.
#                 GuidingBoxes - It contains coordinates of top left
#                                corner and bottom right corner of the four
#                                corner boxes as a list of list in the
#                                clockwise fashion starting from top left
#                                box.
# Description   : This function finds the 4 corner box coordinates from
#                 BoxCoordinates list.
# Return        : GuidingBoxes
################################################################################
def FindGuidingCornerBoxes(BoxCoordinates):
    # Sorting wrt y coordinate of top left corner so that top values are for Boxes
    # at the top and last values depict value for boxes at the bottom.
    BoxCoordinates = sorted(BoxCoordinates, key=lambda l:l[1])
    
    # In this loop it is made sure that first 2 values are for top 2 boxes
    # (left and right) and last 2 values are for bottom 2 boxes(left and right).
    while 1:
        # For first 2 values
        if -10 <= (BoxCoordinates[0][0] - BoxCoordinates[1][0]) <= 10:
            del BoxCoordinates[1]
        # For last 2 values
        elif -10 <= (BoxCoordinates[-1][0] - BoxCoordinates[-2][0]) <= 10:
            del BoxCoordinates[-2]
        # Break if done
        else:
            break

    # GuidingBoxes value is set by filtering boxes in a cyclic
    # order starting from top left box.
    if BoxCoordinates[0][0] < BoxCoordinates[1][0]:
        if BoxCoordinates[-1][0] < BoxCoordinates[-2][0]:
            GuidingBoxes = [BoxCoordinates[0], BoxCoordinates[1],
                            BoxCoordinates[-2], BoxCoordinates[-1]]
        else:
            GuidingBoxes = [BoxCoordinates[0], BoxCoordinates[1],
                            BoxCoordinates[-1], BoxCoordinates[-2]]
    else:
        if BoxCoordinates[-1][0] < BoxCoordinates[-2][0]:
            GuidingBoxes = [BoxCoordinates[1], BoxCoordinates[0],
                            BoxCoordinates[-2], BoxCoordinates[-1]]
        else:
            GuidingBoxes = [BoxCoordinates[1], BoxCoordinates[0],
                            BoxCoordinates[-1], BoxCoordinates[-2]]

    return GuidingBoxes


################################################################################
# Function      : CenterOfGuidingBoxes
# Parameter     : GuidingBoxesCenter - It contains the coordinates of centre of
#                                   guiding/corner boxes found.
#                 GuidingBoxes - It contains coordinates of top left
#                                corner and bottom right corner of the four
#                                corner boxes as a list of list in the
#                                clockwise fashion starting from top left
#                                box.
# Description   : This function finds the centre of 4 corner box found.
# Return        : GuidingBoxesCenter
################################################################################
def CenterOfBoxes(GuidingBoxes):
    GuidingBoxesCenter = []

    for i in GuidingBoxes:
        Center = ((i[0] + i[2])//2, (i[1] + i[3])//2)
        GuidingBoxesCenter.append(Center)

    return GuidingBoxesCenter


################################################################################
# Function      : CenterOfGuidingBoxes
# Parameter     : FinalBoxCoordinates - Final list of boxes which donot
#                                        have any intersecting boxes.
#                 TemplateImage - It reads the template image of guiding boxes.
#                 BoxCoordinates - It contains the coordinates of top left
#                                   corner and bottom right corner of the
#                                   guiding boxes as a list of list.
#                 RetBoxCoordinates - Holds return value of FilterBoxCoordinates.
#                 {Rest parameters are self explanatory}
# Description   : This function finds the coordinates of guiding boxes.
#                 It does it by matching different sizes of template image with
#                 the omr image and then filtering out repeating boxes.
# Return        : return value from FilterBoxCoordinates
################################################################################
def FindGuidingBoxes(MaskedImage):
    FinalBoxCoordinates = []
    # Reads the template image.
    TemplateImage = cv2.imread("TemplateImage.png")
    cv2.imshow("TemplateImage", TemplateImage)
    TemplateImageSize = TemplateImage.shape

    # For enlarging template image.
    for i in range(3):
        TemplateImageResized = cv2.resize(TemplateImage, (TemplateImageSize[1]+i, TemplateImageSize[0]+i))

        BoxCoordinates = TemplateMatching(MaskedImage, TemplateImageResized, Image)
        RetBoxCoordinates = FilterBoxCoordinates(BoxCoordinates)
        for j in RetBoxCoordinates:
            FinalBoxCoordinates.append(j)

    # For diminishing template image.
    for i in range(3):
        TemplateImageResized = cv2.resize(TemplateImage, (TemplateImageSize[1] - i, TemplateImageSize[0] - i))
        BoxCoordinates = TemplateMatching(MaskedImage, TemplateImageResized, Image)

        RetBoxCoordinates = FilterBoxCoordinates(BoxCoordinates)
        for j in RetBoxCoordinates:
            FinalBoxCoordinates.append(j)

    return FilterBoxCoordinates(FinalBoxCoordinates)


def SplitGuidingBoxes(BoxCoordinates, HalfWidthOfImage):
    pass

################################################################################
# Function      : RunCode
# Parameter     : MaskedImage - Contains the image masked for black colour.
#                 FinalBoxCoordinates - Final list of rectangles which donot
#                                        have any intersecting rectangles.
#                 {Rest parameters are self explanatory}
# Description   : This function calls relevant functions one by one in order
#                 to run program.
# Return        : -
################################################################################
def RunCode():
    MaskedImage = MaskImage(Image)

    FinalBoxCoordinates = FindGuidingBoxes(MaskedImage)
    GuidingCornerBoxes = FindGuidingCornerBoxes(FinalBoxCoordinates)
    GuidingCornerBoxesCenter = CenterOfBoxes(GuidingCornerBoxes)
    #LeftGuidingBoxes, RightGuidingBoxes = SplitGuidingBoxes(FinalBoxCoordinates, Image.shape[1]//2)

    for i in FinalBoxCoordinates:
        cv2.rectangle(Image, (i[0], i[1]), (i[2], i[3]), (0, 0, 255), 1)
    for i in GuidingCornerBoxesCenter:
        cv2.circle(Image, i, 2, (0, 255, 0), -1)

    cv2.imshow("GuidingCentre", Image)


RunCode()
t2 = time.time()
cv2.waitKey(0)
cv2.destroyAllWindows()
print(t2-t1)
