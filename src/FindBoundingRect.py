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
# Class         : CornerTag
# Parameter     : Name - Name of corner
#                 StartX, StartY - x&y coordinates of the corner.
#                 IncX, IncY - The value by which x&y will be incremented in
#                              order to expand the square from corner.
#                              It can be negative also.
#                 CheckX, CheckY - Holds those element number of the box which
#                       will tell that if the box may collide to expanding
#                       square, the which x or y coordinate of box may get
#                       equal to x or y coordinate respectively of the corner
#                       of expanding box.
# Description   : Holds the info about a corner to make code simpler.
# Return        : -
################################################################################
class CornerTag:
    def __init__(self, Name, StartX, StartY, IncX, IncY, CheckX, CheckY):
        self.Name = Name
        self.StartX = StartX
        self.StartY = StartY
        self.IncX = IncX
        self.IncY = IncY
        self.CheckX = CheckX
        self.CheckY = CheckY


################################################################################
# Function      : CheckIfCornerBox
# Parameter     : BoxCoordinates - It contains the coordinates of top left
#                                  corner and bottom right corner of the
#                                  boxes as a list of list.
#                 BoxToCheck - Holds coordinates of the box for which we have
#                           to confirm whether it is a guiding corner box or not.
#                 X - x coordinate of the centre of BoxToCheck.
#                 Count - Keeps a count of number of boxes which lie in the
#                         straight line with the BoxToCheck.
# Description   : This function confirms whether the BoxToCheck is the guiding
#                 corner boxes or not. It does it by seeing that number of
#                 guiding boxes in the verticle line of BoxToCheck is greater
#                 than a particular threshold or not.
#                 {This might give false output also if the image is not straight}
# Return        : True - If it is a guiding corner box
#                 False - If it is not a guiding corner box
################################################################################
def CheckIfCornerBox(BoxToCheck, BoxCoordinates):
    Count = 0
    X = (BoxToCheck[0] + BoxToCheck[2])/2

    for Box in BoxCoordinates:
        if Box[0] <= X <= Box[2]:
            Count += 1

    if Count >= 10:     # Threshold Value
        return True
    else:
        return False


################################################################################
# Function      : FindCornerBox
# Parameter     : BoxCoordinates - It contains the coordinates of top left
#                                  corner and bottom right corner of the
#                                  boxes as a list of list.
#                 Corner - This is object of class CornerTag passed. Will find
#                          corner guiding box nearest to this corner.
#                 IterateTill - Holds the shorter side length value of image so
#                               that loop does not exceed the image.
#                 X, Y - x&y coordinate of the corner nearer to which guiding
#                        corner is being found.
#                 NumOfIterations - Keeps a count of number of iterations.
#                 FoundCorner - Flag for if corner is found or not.
#                 CornerBoxFound - Holds coordinates of the corner box found.
# Description   : This function finds the tentative guiding corner box of the OMR
#                 nearer to the corner asked and then confirms if by calling
#                 CheckIfCornerBox.
#                 {This might give false output also if the image is not straight}
# Return        : CornerBoxFound
################################################################################
def FindCornerBox(BoxCoordinates, Corner, IterateTill):
    X = Corner.StartX
    Y = Corner.StartY
    NumOfIterations = 0
    FoundCorner = 0

    while NumOfIterations < IterateTill:
        for Box in BoxCoordinates:
            if Corner.Name == "TL":                                           # For top left corner
                if X == Box[Corner.CheckX] and Y >= Box[Corner.CheckX + 1]:
                    if CheckIfCornerBox(Box, BoxCoordinates):
                        CornerBoxFound = Box
                        FoundCorner = 1
                        break
                elif Y == Box[Corner.CheckY] and X >= Box[Corner.CheckY - 1]:
                    if CheckIfCornerBox(Box, BoxCoordinates):
                        CornerBoxFound = Box
                        FoundCorner = 1
                        break

            elif Corner.Name == "TR":                                         # For top right corner
                if X == Box[Corner.CheckX] and Y >= Box[Corner.CheckX + 1]:
                    if CheckIfCornerBox(Box, BoxCoordinates):
                        CornerBoxFound = Box
                        FoundCorner = 1
                        break
                elif Y == Box[Corner.CheckY] and X <= Box[Corner.CheckY - 1]:
                    if CheckIfCornerBox(Box, BoxCoordinates):
                        CornerBoxFound = Box
                        FoundCorner = 1
                        break

            elif Corner.Name == "BR":                                         # For bottom right corner
                if X == Box[Corner.CheckX] and Y <= Box[Corner.CheckX + 1]:
                    if CheckIfCornerBox(Box, BoxCoordinates):
                        CornerBoxFound = Box
                        FoundCorner = 1
                        break
                elif Y == Box[Corner.CheckY] and X <= Box[Corner.CheckY - 1]:
                    if CheckIfCornerBox(Box, BoxCoordinates):
                        CornerBoxFound = Box
                        FoundCorner = 1
                        break

            elif Corner.Name == "BL":                                         # For bottom left corner
                if X == Box[Corner.CheckX] and Y <= Box[Corner.CheckX + 1]:
                    if CheckIfCornerBox(Box, BoxCoordinates):
                        CornerBoxFound = Box
                        FoundCorner = 1
                        break
                elif Y == Box[Corner.CheckY] and X >= Box[Corner.CheckY - 1]:
                    if CheckIfCornerBox(Box, BoxCoordinates):
                        CornerBoxFound = Box
                        FoundCorner = 1
                        break

        if FoundCorner:
            break

        X += Corner.IncX
        Y += Corner.IncY
        NumOfIterations += 1

    if FoundCorner:
        return CornerBoxFound
    else:
        print("Corner not found for - " + Corner.Name)
        return CornerBoxFound


################################################################################
# Function      : FindGuidingCornerBoxes
# Parameter     : BoxCoordinates - It contains the coordinates of top left
#                                  corner and bottom right corner of the
#                                  boxes as a list of list.
#                 ImageShape - Holds shape of omr image.
#                 GuidingCornerBoxes - Hold coordinates of the guiding corner boxes.
#                 TL/TR/BR/BL CornerTag - These are objects of class CornerTag.
# Description   : This function finds the guiding corner boxes of the OMR.
#                 {This might give false output also if the image is not straight}
# Return        : GuidingCornerBoxes
################################################################################
def FindGuidingCornerBoxes(BoxCoordinates, ImageShape):
    GuidingCornerBoxes = []

    if ImageShape[0] <= ImageShape[1]:
        IterateTill = ImageShape[0]
    else:
        IterateTill = ImageShape[1]

    TLCornerTag = CornerTag("TL", 0, 0, 1, 1, 0, 1)
    TRCornerTag = CornerTag("TR", (ImageShape[1] - 1), 0, -1, 1, 2, 1)
    BRCornerTag = CornerTag("BR", (ImageShape[1] - 1), (ImageShape[0] - 1), -1, -1, 2, 3)
    BLCornerTag = CornerTag("BL", 0, (ImageShape[0] - 1), 1, -1, 0, 3)

    GuidingCornerBoxes.append(FindCornerBox(BoxCoordinates, TLCornerTag, IterateTill))
    GuidingCornerBoxes.append(FindCornerBox(BoxCoordinates, TRCornerTag, IterateTill))
    GuidingCornerBoxes.append(FindCornerBox(BoxCoordinates, BRCornerTag, IterateTill))
    GuidingCornerBoxes.append(FindCornerBox(BoxCoordinates, BLCornerTag, IterateTill))

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
# Function      : CheckBoundaryForAllBlack
# Parameter     : FoundWhite - Flag for if non black pixel is found on the
#                              boundary.
#                 {Rest parameters are self explanatory}
# Description   : This function checks the boundary of the box for all black
#                 pixel.
# Return        : True - If all are black on boundary.
#                 False - If all are not black o boundary.
################################################################################
def CheckBoundaryForAllBlack(x1, y1, x2, y2, MaskedImage):
    FoundWhite = 0

    for i in range(x1, (x2+1)):                     # Moving right
        if MaskedImage[y1][i] != 0 or MaskedImage[y2][i] != 0:
            FoundWhite = 1

    if FoundWhite == 0:
        for j in range(y1, (y2+1)):                 # Moving down
            if MaskedImage[j][x1] != 0 or MaskedImage[j][x2] != 0:
                FoundWhite = 1

    if FoundWhite == 0:
        return True             # All are black.
    else:
        return False            # Some are white.


################################################################################
# Function      : ShrinkBoxWRTBoundary
# Parameter     : ShrinkedBoxCoordinates - It contains the list of coordinates
#                                          of box after shrinking wrt boundary.
#                 FinalBox - It contains coordinates of individual shrinked box
#                            and is then appended to ShrinkedBoxCoordinates.
#                 {Rest parameters are self explanatory}
# Description   : This function shrinks the boxes wrt the boundary. A box is
#                 shrinked if all the pixels on the boundary of the box are
#                 black and the central pixel of the box is not black.
# Return        : ShrinkedBoxCoordinates
################################################################################
def ShrinkBoxWRTBoundary(BoxCoordinates, MaskedImage):
    ShrinkedBoxCoordinates = []
    for Box in BoxCoordinates:
        x1, y1, x2, y2 = Box[0], Box[1], Box[2], Box[3]
        FinalBox = Box

        while x1 <= x2 and y1 <= y2:
            # Check Boundary of box for all black.
            if CheckBoundaryForAllBlack(x1, y1, x2, y2, MaskedImage):
                # Check center of box for non white
                if MaskedImage[int((y2+y1)/2)][int((x1+x2)/2)] != 0:
                    FinalBox = [x1, y1, x2, y2]

            x1 += 1
            y1 += 1
            x2 -= 1
            y2 -= 1

        ShrinkedBoxCoordinates.append(FinalBox)

    return ShrinkedBoxCoordinates


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

    return FilterBoxCoordinates(ShrinkBoxWRTBoundary(FinalBoxCoordinates, MaskedImage))


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
# Function      : ShrinkTotalBox
# Parameter     : {All the parameters are explanatory.}
# Description   : This function shrinks the box to the guiding box completely.
#                 It does it by storing all the x and y coordinates of those
#                 pixels which do not have black colour in XCoordinates and
#                 YCoordinates respectively. Then the shrinked box will have
#                 coordinates of top left corner as (min(XCoordinates),
#                 min(YCoordinates)) and the bottom right corner as
#                 (max(XCoordinates), max(YCoordinates)).
# Return        : FinalBoxCoordinates
################################################################################
def ShrinkTotalBox(BoxCoordinates, MaskedImage):
    FinalBoxCoordinates = []

    for Box in BoxCoordinates:
        XCoordinates = []
        YCoordinates = []
        x1, y1, x2, y2 = Box[0], Box[1], Box[2], Box[3]

        for i in range(x1, (x2+1)):
            for j in range(y1, (y2+1)):
                # MaskedImage[j][i]
                if MaskedImage[j][i] != 0:
                    XCoordinates.append(i)
                    YCoordinates.append(j)

        XCoordinates = sorted(XCoordinates)
        YCoordinates = sorted(YCoordinates)

        FinalBoxCoordinates.append([XCoordinates[0], YCoordinates[0], XCoordinates[-1], YCoordinates[-1]])

    return FinalBoxCoordinates


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
    GuidingCornerBoxes = FindGuidingCornerBoxes(BoxCoordinates, MaskedImage.shape)
    GuidingCornerBoxesCenter = CenterOfBoxes(GuidingCornerBoxes)
    LeftGuidingBoxes, RightGuidingBoxes = SplitAndFindGuidingBoxes(BoxCoordinates, Image.shape[1] // 2,
                                                                   GuidingCornerBoxesCenter)
    LeftGuidingBoxes = ShrinkTotalBox(LeftGuidingBoxes, MaskedImage)
    RightGuidingBoxes = ShrinkTotalBox(RightGuidingBoxes, MaskedImage)

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
    cv2.imshow("GuidingBoxes", Image)

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
    if InputImagePath is None:
        Image = cv2.imread("InputImages/Blank1.jpg")
    else:
        Image = cv2.imread(InputImagePath)

    if ResizeInputImageTo is None:
        Image = cv2.resize(Image, (600, 800))       # Default Value is set to (600, 800).
    else:
        Image = cv2.resize(Image, ResizeInputImageTo)

    cv2.imshow("Input", Image)
    #print(Image.shape)
    LeftGuidingBoxes, RightGuidingBoxes = RunCode()

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return LeftGuidingBoxes, RightGuidingBoxes


# Call this function(FindBoundingBoxes) to run code present in this file with suitable parameters.
FindBoundingBoxes()
