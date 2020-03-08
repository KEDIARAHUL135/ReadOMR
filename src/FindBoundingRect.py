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
import os


################################################################################
# Function      : MaskImage
# Parameter     : Image - It contains Input OMR Image.
#                 HSVImage - It contains HSV of input OMR image.
#                 LowerRange, UpperRange - They mention the range used to
#                         extract horizontal block near the edges(Black colour).
#                 MaskedImage - It contains the Masked Image.
#                 MaskedBlurImage - Blur of Masked Image.
# Description   : This function masks the input OMR image for black colour.
# Return        : MaskedBlurImage
################################################################################
def MaskImage():
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
# Description   : This function matches the template image of the masked Image
#                 to find the horizontal boxes and returns the list of
#                 boxes detected.
# Return        : BoxCoordinates
################################################################################
def TemplateMatching(MaskedImage, TemplateImage, OMRImage):
    BoxCoordinates = []

    # Code copied from -
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/
    #                                   py_template_matching/py_template_matching.html

    if (len(MaskedImage.shape)) == 3:
        img_gray = cv2.cvtColor(MaskedImage, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = MaskedImage

    if len(TemplateImage.shape) == 3:
        template = cv2.cvtColor(TemplateImage, cv2.COLOR_BGR2GRAY)
    else:
        template = TemplateImage

    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
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

        for J in range(I + 1, LengthOfBoxCoordinates):
            Rect2 = BoxCoordinates[J].copy()

            if IntersectingArea(Rect1, Rect2) is True:
                FoundIntersectingArea = 1
                break

        if FoundIntersectingArea == 0:
            FinalBoxCoordinates.append(BoxCoordinates[I])

    return FinalBoxCoordinates


################################################################################
# Function      : FindGuidingCornerBoxes
# Parameter     : BoxCoordinates - It contains the coordinates of top left
#                                  corner and bottom right corner of the
#                                  Boxes as a list of list.
#                 GuidingCornerBoxes - It contains coordinates of top left
#                                corner and bottom right corner of the four
#                                corner boxes as a list of list in the clockwise
#                                fashion starting from top left box.
# Description   : This function finds the 4 guiding corner box coordinates from
#                 BoxCoordinates list.
# Return        : GuidingCornerBoxes
################################################################################
def FindGuidingCornerBoxes(BoxCoordinates):
    # Sorting wrt y coordinate of top left corner so that top values are for Boxes
    # at the top and last values depict value for boxes at the bottom.
    BoxCoordinates = sorted(BoxCoordinates, key=lambda l: l[1])

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
            GuidingCornerBoxes = [BoxCoordinates[0], BoxCoordinates[1],
                                  BoxCoordinates[-2], BoxCoordinates[-1]]
        else:
            GuidingCornerBoxes = [BoxCoordinates[0], BoxCoordinates[1],
                                  BoxCoordinates[-1], BoxCoordinates[-2]]
    else:
        if BoxCoordinates[-1][0] < BoxCoordinates[-2][0]:
            GuidingCornerBoxes = [BoxCoordinates[1], BoxCoordinates[0],
                                  BoxCoordinates[-2], BoxCoordinates[-1]]
        else:
            GuidingCornerBoxes = [BoxCoordinates[1], BoxCoordinates[0],
                                  BoxCoordinates[-1], BoxCoordinates[-2]]

    return GuidingCornerBoxes


################################################################################
# Function      : CenterOfBoxes
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
        Center = ((i[0] + i[2]) // 2, (i[1] + i[3]) // 2)
        GuidingBoxesCenter.append(Center)

    return GuidingBoxesCenter


################################################################################
# Function      : FindGuidingBoxes
# Parameter     : FinalBoxCoordinates - Final list of boxes which donot
#                                        have any intersecting boxes.
#                 TemplateImagesFolderPath - Path of template images' folder.
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

    TemplateImagesFolderPath = os.path.abspath(os.path.join('TemplateImages'))

    # Read all template images and run.
    for ImageName in os.listdir(TemplateImagesFolderPath):
        print(ImageName)                    # Verifying name of image
        # Reading in image
        TemplateImage = cv2.imread(TemplateImagesFolderPath + "/" + ImageName)

        TemplateImageSize = TemplateImage.shape

        # For enlarging template image.
        for i in range(3):
            TemplateImageResized = cv2.resize(TemplateImage, (TemplateImageSize[1] + i, TemplateImageSize[0] + i))

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


################################################################################
# Function      : TrueGuidingBoxes
# Parameter     : GuidingBoxesList - List of boxes from which true guiding
#                                    boxes are to be founded.
#                 GuidingLineC1, GuidingLineC2 - Coordinates of centre of
#                                                guiding corner boxes.
#                 TrueGuidingBoxesList - List of true guiding boxes found.
#                 {Rest parameters are explained.}
# Description   : This function filters the true guiding boxes from the list
#                 of boxes provided.
# Return        : TrueGuidingBoxesList
################################################################################
def TrueGuidingBoxes(GuidingBoxesList, GuidingLineC1, GuidingLineC2):
    TrueGuidingBoxesList = []

    # Now let (x1, y1) & (x2, y2) be the points of guiding line(coordinates of center of guiding corner boxes).
    # Slope of this line be "Slope" and its value is ((y2 - y1)/(x2 - x1)).
    # Let inverse of slope be "B", and its value is ((x2 - x1)/(y2 - y1)).
    # Let "A" be of value (x1 - y1*B).
    # Here "A" & "B" are constants.
    # Value of x-coordinate of a point on line at y-coordinate y3 is (X = A + y3*B).
    # To check if the guiding box is truly a guiding box, the value X must lie between x3 and x4
    # where (x3, y3) & (x4, y4) are coordinates for a rectangle of guiding box.

    B = ((GuidingLineC2[0] - GuidingLineC1[0]) / (GuidingLineC2[1] - GuidingLineC1[1]))
    A = (GuidingLineC1[0] - (GuidingLineC1[1] * B))

    for Box in GuidingBoxesList:
        X = (A + (Box[1] * B))
        if Box[0] <= X <= Box[2]:
            TrueGuidingBoxesList.append(Box)

    return TrueGuidingBoxesList


################################################################################
# Function      : SplitAndFindGuidingBoxes
# Parameter     : BoxCoordinates - List of all the boxes found.
#                 LeftGuidingBoxes, RightGuidingBoxes - List of left and right
#                       guiding boxes found.(First all the boxes are divided to
#                       left and right and the true guiding boxes are found.)
#                 HalfWidthOfImage - Half of width of image(From which left and
#                                    right boxes are separated).
#                 {Rest parameters are explained.}
# Description   : This function filters the true left and right guiding boxes
#                 from the list of boxes provided.
# Return        : LeftGuidingBoxes, RightGuidingBoxes
################################################################################
def SplitAndFindGuidingBoxes(BoxCoordinates, HalfWidthOfImage, GuidingCornerBoxesCenter):
    LeftGuidingBoxes = []
    RightGuidingBoxes = []

    BoxCoordinates = sorted(BoxCoordinates, key=lambda l: l[0])

    # Filter all boxes to left and right
    for i in BoxCoordinates:
        if i[0] <= HalfWidthOfImage:
            LeftGuidingBoxes.append(i)
        else:
            RightGuidingBoxes.append(i)

    LeftGuidingBoxes = TrueGuidingBoxes(LeftGuidingBoxes, GuidingCornerBoxesCenter[0], GuidingCornerBoxesCenter[3])
    RightGuidingBoxes = TrueGuidingBoxes(RightGuidingBoxes, GuidingCornerBoxesCenter[1], GuidingCornerBoxesCenter[2])

    # Arranging from top to bottom line wise.
    LeftGuidingBoxes = sorted(LeftGuidingBoxes, key=lambda l: l[1])
    RightGuidingBoxes = sorted(RightGuidingBoxes, key=lambda l: l[1])

    return LeftGuidingBoxes, RightGuidingBoxes


################################################################################
# Function      : RunCode
# Parameter     : MaskedImage - Contains the image masked for black colour.
#                 BoxCoordinates - Final list of boxes which donot have any
#                         intersecting boxes(These are not actual guiding boxes).
#                 {Rest parameters are self explanatory}
# Description   : This function calls relevant functions one by one in order
#                 to run program.
# Return        : LeftGuidingBoxes, RightGuidingBoxes
################################################################################
def RunCode():
    MaskedImage = MaskImage()

    BoxCoordinates = FindGuidingBoxes(MaskedImage)
    GuidingCornerBoxes = FindGuidingCornerBoxes(BoxCoordinates)
    GuidingCornerBoxesCenter = CenterOfBoxes(GuidingCornerBoxes)
    LeftGuidingBoxes, RightGuidingBoxes = SplitAndFindGuidingBoxes(BoxCoordinates, Image.shape[1] // 2,
                                                                   GuidingCornerBoxesCenter)

    if len(LeftGuidingBoxes) == len(RightGuidingBoxes):
        print("Yes, program working correctly")
    else:
        print("Guiding Boxes not found correctly.")

    # =====================Just for visualisation, to be deleted==========================
    for i in LeftGuidingBoxes:
        cv2.rectangle(Image, (i[0], i[1]), (i[2], i[3]), (255, 0, 0), 1)
    for i in RightGuidingBoxes:
        cv2.rectangle(Image, (i[0], i[1]), (i[2], i[3]), (0, 0, 255), 1)
    for i in GuidingCornerBoxesCenter:
        cv2.circle(Image, i, 2, (0, 255, 0), -1)
    # ====================================================================================
    cv2.imshow("GuidingCentre", Image)

    return LeftGuidingBoxes, RightGuidingBoxes


################################################################################
# Function      : FindBoundingBoxes
# Parameter     : Image - Reads the input image of omr sheet.
#                 InputImagePath - Path from which input image is to be read.
#                 ResizeInputImageTo - Resize input image to this size.
#                 {Rest parameters are self explanatory}
# Description   : This function read the input omr image and calls RunCode to
#                 ultimately find the guiding boxes of left side and right side.
# Return        : LeftGuidingBoxes, RightGuidingBoxes
################################################################################
def FindBoundingBoxes(InputImagePath=None, ResizeInputImageTo=None):
    global Image

    # Read and resize Input OMR Image
    if InputImagePath == None:
        Image = cv2.imread("InputImages/OMR1/Blank.jpeg")
    else:
        Image = cv2.imread(InputImagePath)

    if ResizeInputImageTo == None:
        Image = cv2.resize(Image, (600, 800))       # Default Value is set to (600, 800).
    else:
        Image = cv2.resize(Image, ResizeInputImageTo)

    cv2.imshow("Input", Image)
    print(Image.shape)
    LeftGuidingBoxes, RightGuidingBoxes = RunCode()

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return LeftGuidingBoxes, RightGuidingBoxes


# Call this function(FindBoundingBoxes) to run code present in this file with suitable parameters.
FindBoundingBoxes()
