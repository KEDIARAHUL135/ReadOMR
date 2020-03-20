###############################################################################
# File          : FindBoundingBoxes.py
# Created by    : Rahul Kedia
# Created on    : 06/03/2020
# Project       : ReadOMR
# Description   : This file aims to find the guiding boxes from the OMR Sheet 
#                 with reference to which the OMR Sheet will be cropped.
################################################################################

import numpy as np
import cv2
import os
import macros as M
import CheckBrightness as CB


################################################################################
# Function      : MaskImage
# Parameter     : HSVImage - It contains HSV of input OMR image.
#                 LowerRange, UpperRange - They mention the range used to extract
#                                   horizontal block near the edges(Black colour).
#                 MaskedImage - It contains the Masked Image.
#                 MaskedBlurImage - Blur of Masked Image.
# Description   : This function masks the input OMR image for black to a range 
#                 of dark gray colour.
# Return        : MaskedBlurImage
################################################################################
def MaskImage(UpperLimitOfValue):
    HSVImage = cv2.cvtColor(Image, cv2.COLOR_BGR2HSV)

    # Setting range
    LowerRange = np.array([0, 0, 0])
    UpperRange = np.array([255, 255, UpperLimitOfValue])

    # Masking
    MaskedImage = cv2.inRange(HSVImage, LowerRange, UpperRange)
    
    # Blurring
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
        GrayImage = cv2.cvtColor(MaskedImage, cv2.COLOR_BGR2GRAY)
    else:
        GrayImage = MaskedImage

    if len(TemplateImage.shape) == 3:
        TemplateImage = cv2.cvtColor(TemplateImage, cv2.COLOR_BGR2GRAY)
    
    w, h = TemplateImage.shape[::-1]

    res = cv2.matchTemplate(GrayImage, TemplateImage, cv2.TM_CCOEFF_NORMED)
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
#                                  corner and bottom right corner of the
#                                  boxes as a list of list.
#                 LengthOfBoxCoordinates - Stores the length of BoxCoordinates.
#                 FoundIntersectingArea - Flag of whether Intersecting area is
#                                         found or not.
#                 Rect1, Rect2 - Stores 2 rectangles to be compared.
#                 FinalBoxCoordinates - Final list of boxes which donot
#                                       have any intersecting boxes.
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
#                 boxes in the verticle line of BoxToCheck is greater
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

    if Count >= M.THRESHOLD_TO_CHECK_IF_CORNER_BOX:     # Threshold Value
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
            # For top left corner
            if Corner.Name == "TL":                                           
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

            # For top right corner
            elif Corner.Name == "TR":                                         
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

            # For bottom right corner
            elif Corner.Name == "BR":                                         
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

            # For bottom left corner
            elif Corner.Name == "BL":                                         
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
#                 ImageShape - Holds shape of OMR image.
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

    # Creating objects
    TLCornerTag = CornerTag("TL", 0, 0, 1, 1, 0, 1)
    TRCornerTag = CornerTag("TR", (ImageShape[1] - 1), 0, -1, 1, 2, 1)
    BRCornerTag = CornerTag("BR", (ImageShape[1] - 1), (ImageShape[0] - 1), -1, -1, 2, 3)
    BLCornerTag = CornerTag("BL", 0, (ImageShape[0] - 1), 1, -1, 0, 3)

    # Calling FindCornerBox and appending the GuidingCornerBox list.
    GuidingCornerBoxes.append(FindCornerBox(BoxCoordinates, TLCornerTag, IterateTill))
    GuidingCornerBoxes.append(FindCornerBox(BoxCoordinates, TRCornerTag, IterateTill))
    GuidingCornerBoxes.append(FindCornerBox(BoxCoordinates, BRCornerTag, IterateTill))
    GuidingCornerBoxes.append(FindCornerBox(BoxCoordinates, BLCornerTag, IterateTill))

    return GuidingCornerBoxes


################################################################################
# Function      : CenterOfBoxes
# Parameter     : BoxesCenter - It contains the coordinates of centre of boxes.
#                 Boxes - It contains list of coordinates of boxes.
# Description   : This function finds the centre of boxes present in the list 
#                 and returns the list of center coordinates of the respective 
#                 boxes.
# Return        : BoxesCenter
################################################################################
def CenterOfBoxes(Boxes):
    BoxesCenter = []

    for i in Boxes:
        Center = ((i[0] + i[2]) // 2, (i[1] + i[3]) // 2)
        BoxesCenter.append(Center)

    return BoxesCenter


################################################################################
# Function      : CheckBoundaryForAllBlack
# Parameter     : FoundWhite - Flag for if non black pixel is found on the
#                              boundary.(True if non black found and False if not).
#                 {Rest parameters are self explanatory}
# Description   : This function checks the boundary of the box for all black
#                 pixel.
# Return        : True - If all are black on the boundary.
#                 False - If all are not black on the boundary.
################################################################################
def CheckBoundaryForAllBlack(x1, y1, x2, y2, MaskedImage):
    FoundWhite = False
    # Flag for boundary with white pixel [Top, Right, Bottom, Left] - order used.
    BoundaryWithWhite = [0, 0, 0, 0]      

    for i in range(x1, (x2+1)):                     # Moving right
        if MaskedImage[y1][i] != 0:                 # Checking top boundary
            FoundWhite = True
            BoundaryWithWhite[0] = 1

        if MaskedImage[y2][i] != 0:                 # Checking bottom boundary
            FoundWhite = True
            BoundaryWithWhite[2] = 1

    for j in range(y1, (y2+1)):                     # Moving down
        if MaskedImage[j][x1] != 0:                 # Checking left boundary
            FoundWhite = True
            BoundaryWithWhite[3] = 1

        if MaskedImage[j][x2] != 0:                 # Checking right boundary
            FoundWhite = True
            BoundaryWithWhite[1] = 1

    if FoundWhite:
        return False, BoundaryWithWhite            # Some are white.
    else:
        return True, BoundaryWithWhite             # All are black.


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
            Flag, BoundaryWithWhite = CheckBoundaryForAllBlack(x1, y1, x2, y2, MaskedImage)
            if Flag:
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
# Function      : FindGuidingBoxes_ContourLogic
# Parameter     : BoxCoordinates - It contains the coordinates of top left boxes 
#                       as corner and bottom right corner of the a list of list.            
#                 {Rest parameters are self explanatory}
# Description   : This function finds the coordinates of boxes.
#                 It does it by drawing contours, making a rectangle around 
#                 them and then expanding the rectangle till all the pixels on 
#                 its boundary are black(0 value).
# Return        : return value from FilterBoxCoordinates
################################################################################
def FindGuidingBoxes_ContourLogic(MaskedImage):
    BoxCoordinates = []
    Height, Width = MaskedImage.shape[:2]

    MaskedCopy = MaskedImage.copy()
    Copy2 = Image.copy()

    # Finding edges and then contours.
    EdgeImage = cv2.Canny(MaskedCopy, 30, 200) 
    Contours, Hierarchy = cv2.findContours(EdgeImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
    
    for Contour in Contours:
        # Creating the bounding rectangle.
        (x, y, w, h) = cv2.boundingRect(Contour)
        # Crecking conditions of shape(verticle box or horizontal box) and area.
        if w > h and w*h >= M.MIN_CONTOUR_AREA and w*h <= M.MAX_CONTOUR_AREA:
            # Expanding box wrt boundaries till total black.
            x1, y1, x2, y2 = x, y, x+w-1, y+h-1
            while 1:
                ValueChanged = 0            # Flag to break loop if expanded from all sides.
                print("({}, {}, {}, {})".format(x1, y1, x2, y2))
                Copy3 = Copy2.copy()
                cv2.rectangle(Copy3, (x1, y1), (x2, y2), (0, 0, 255), thickness=1)
                cv2.imshow("Running code on contour", Copy3)
                cv2.waitKey(1)
                
                # Check Boundary of box for all black.
                Flag, BoundaryWithWhite = CheckBoundaryForAllBlack(x1, y1, x2, y2, MaskedImage)
                Area = ((x2 - x1)*(y2 - y1))
                # Again checking max area limit to break if exceeded
                if Area >= M.MAX_CONTOUR_AREA:
                    break
                # Expanding rectangle
                if not Flag:
                    if BoundaryWithWhite[0] == 1 and y1 > 0:            # Top edge
                        y1 -= 1
                        ValueChanged = 1
                    if BoundaryWithWhite[1] == 1 and x2 < (Width - 2):  # Right edge
                        x2 += 1
                        ValueChanged = 1
                    if BoundaryWithWhite[2] == 1 and y2 < (Height -2):  # Bottom edge
                        y2 += 1
                        ValueChanged = 1
                    if BoundaryWithWhite[3] == 1 and x1 > 0:            # Left edge
                        x1 -= 1
                        ValueChanged = 1
                    if ValueChanged == 0:
                        break
                else:
                    break
            
            # Appending box coordinates value after finding and expanding rectangle.
            BoxCoordinates.append([x1, y1, x2, y2])

            cv2.rectangle(Copy2, (x1, y1), (x2, y2), (0, 0, 255), thickness=1)
    cv2.imshow('Contours', Copy2)

    #BoxCoordinates = FilterBoxCoordinates(BoxCoordinates)
    return FilterBoxCoordinates(ShrinkBoxWRTBoundary(BoxCoordinates, MaskedImage))


################################################################################
# Function      : FindGuidingBoxes_TemplateLogic
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
#                 the masked OMR image and then filtering out repeating boxes.
# Return        : return value from FilterBoxCoordinates
################################################################################
def FindGuidingBoxes_TemplateLogic(MaskedImage):
    FinalBoxCoordinates = []

    TemplateImagesFolderPath = os.path.abspath(os.path.join('TemplateImages'))

    # Read all template images and run.
    for ImageName in os.listdir(TemplateImagesFolderPath):
        TemplateImage = cv2.imread(TemplateImagesFolderPath + "/" + ImageName)
        TemplateImageSize = TemplateImage.shape

        # For enlarging template image.
        for i in range(3):
            TemplateImageResized = cv2.resize(TemplateImage, (TemplateImageSize[1] + i, 
                                                              TemplateImageSize[0] + i))

            BoxCoordinates = TemplateMatching(MaskedImage, TemplateImageResized, Image)
            RetBoxCoordinates = FilterBoxCoordinates(BoxCoordinates)
            for j in RetBoxCoordinates:
                FinalBoxCoordinates.append(j)

        # For diminishing template image.
        for i in range(3):
            TemplateImageResized = cv2.resize(TemplateImage, (TemplateImageSize[1] - i, 
                                                              TemplateImageSize[0] - i))
            BoxCoordinates = TemplateMatching(MaskedImage, TemplateImageResized, Image)

            RetBoxCoordinates = FilterBoxCoordinates(BoxCoordinates)
            for j in RetBoxCoordinates:
                FinalBoxCoordinates.append(j)

    return FilterBoxCoordinates(ShrinkBoxWRTBoundary(FinalBoxCoordinates, MaskedImage))


################################################################################
# Function      : FilterGuidingBoxes_RansacLogic
# Parameter     : BoxesList - List of boxes from which true guiding boxes are 
#                             to be founded.       
#                 GuidingBoxesList - List of true guiding boxes found.
#                 CenterInliersList - 2D list of inliers element numbers and 
#                           inliers count and its first two elements are the 
#                           element numbers wrt which inliers are being found.
#                 {Rest parameters are self explanatory.}
# Description   : This function filters the guiding boxes from the list
#                 of boxes provided by using logic inspired by RANSAC.
# Return        : GuidingBoxesList
################################################################################
def FilterGuidingBoxes_RansacLogic(BoxesList):
    CenterOfBoxesList = CenterOfBoxes(BoxesList)
    GuidingBoxesList = []
    CenterInliersList = []
    LengthOfBoxesList = len(CenterOfBoxesList)

    # Finding inliers wrt center coordinates.
    for i in range(LengthOfBoxesList):
        for j in range((i+1), LengthOfBoxesList):
            InliersList = [i, j]
            InlierCount = 0
            # Now let (x1, y1) & (x2, y2) be the points of line(coordinates of center of boxes).
            # Slope of this line be "Slope" and its value is ((y2 - y1)/(x2 - x1)).
            # Let inverse of slope be "B", and its value is ((x2 - x1)/(y2 - y1)).
            # Let "A" be of value (x1 - y1*B).
            # Here "A" & "B" are constants.
            # Value of x-coordinate of a point on line at y-coordinate y3 is (X = A + y3*B).
            # To check if the center  is inlier, the value (X - x-coordinate of center) must lie
            # between +-(M.MAX_INLIER_DIST).

            if (CenterOfBoxesList[j][1] - CenterOfBoxesList[i][1]) == 0:
                B = 100000                                      # A big value
            else:
                B = ((CenterOfBoxesList[j][0] - CenterOfBoxesList[i][0]) /\
                     (CenterOfBoxesList[j][1] - CenterOfBoxesList[i][1]))
            A = (CenterOfBoxesList[i][0] - (CenterOfBoxesList[i][1] * B))

            for k in range(LengthOfBoxesList):
                X = (A + (CenterOfBoxesList[k][1] * B))
                if (-(M.MAX_INLIER_DIST)) <= (X - CenterOfBoxesList[k][0]) <=\
                      M.MAX_INLIER_DIST:
                    InliersList.append(k)
                    InlierCount += 1
            
            InliersList.append(InlierCount)
            # Appending the CenterInliersList list.
            CenterInliersList.append(InliersList)

    # Finding list with max inlier details. 
    MaxInlierList = [0]
    for InlierList in CenterInliersList:
        if InlierList[-1] >= MaxInlierList[-1]:
            MaxInlierList = InlierList
    
    print(MaxInlierList)

    # Storing the values of boxes which are in maximum inliers.
    for i in range(2, (len(MaxInlierList) - 1)):
        GuidingBoxesList.append(BoxesList[MaxInlierList[i]])

    return GuidingBoxesList


################################################################################
# Function      : FilterGuidingBoxes_ScoreLogic
# Parameter     : BoxesList - List of boxes from which true guiding
#                             boxes are to be founded.
#                 GuidingBoxesList - List of true guiding boxes found.
#                 Scores - Holds the score of respective boxes.
#                 {Rest parameters are explained.}
# Description   : This function filters the guiding boxes from the list
#                 of boxes provided by using logic of scores. Score of a box 
#                 denotes that how many boxes have intersecting area with the 
#                 box to be scored. If the score is below a minimum threshold, 
#                 then it is considered as a guiding box.
# Return        : GuidingBoxesList
################################################################################
def FilterGuidingBoxes_ScoreLogic(BoxesList):
    GuidingBoxesList = []
    Scores = []

    # Finding score and storing it.
    for BoxToBeScored in BoxesList:
        Score = 0
        for Box in BoxesList:
            if Box[2] > BoxToBeScored[0] and Box[0] < BoxToBeScored[2]:
                Score += 1

        Scores.append(Score)

    # Comparing score with threshold and saving it as guiding box.
    for i in range(len(Scores)):
        if Scores[i] >= M.MIN_SCORE_REQ:
            GuidingBoxesList.append(BoxesList[i])

    return GuidingBoxesList


################################################################################
# Function      : FilterGuidingBoxes_InsideLineLogic
# Parameter     : BoxesList - List of boxes from which true guiding
#                                    boxes are to be founded.
#                 GuidingLineC1, GuidingLineC2 - Coordinates of centre of
#                                                guiding corner boxes.
#                 GuidingBoxesList - List of true guiding boxes found.
#                 {Rest parameters are explained.}
# Description   : This function filters the guiding boxes from the list
#                 of boxes provided by using logic of boxes intersected by lines.
#                 Line is drawn from the center of two tentative corner 
#                 guiding boxes found. All the boxes crossing that line are 
#                 considered to be guiding boxes.
# Return        : GuidingBoxesList
################################################################################
def FilterGuidingBoxes_InsideLineLogic(BoxesList, GuidingLineC1, GuidingLineC2):
    GuidingBoxesList = []

    # Now let (x1, y1) & (x2, y2) be the points of guiding line(coordinates of center of 
    # guiding corner boxes).
    # Slope of this line be "Slope" and its value is ((y2 - y1)/(x2 - x1)).
    # Let inverse of slope be "B", and its value is ((x2 - x1)/(y2 - y1)).
    # Let "A" be of value (x1 - y1*B).
    # Here "A" & "B" are constants.
    # Value of x-coordinate of a point on line at y-coordinate y3 is (X = A + y3*B).
    # To check if the guiding box is truly a guiding box, the value X must lie between 
    # x3 and x4 where (x3, y3) & (x4, y4) are coordinates for a rectangle of guiding box.

    B = ((GuidingLineC2[0] - GuidingLineC1[0]) / (GuidingLineC2[1] - GuidingLineC1[1]))
    A = (GuidingLineC1[0] - (GuidingLineC1[1] * B))

    for Box in BoxesList:
        X = (A + (Box[1] * B))
        if Box[0] <= X <= Box[2]:
            GuidingBoxesList.append(Box)

    return GuidingBoxesList


################################################################################
# Function      : SplitAndFindGuidingBoxes
# Parameter     : BoxCoordinates - List of all the boxes found.
#                 LeftBoxes, RightBoxes - List of left and right boxes found.
#                       (First all the boxes are divided to left and right and
#                        the true guiding boxes are found.)
#                 HalfWidthOfImage - Half of width of image(From which left and
#                                    right boxes are separated).
#                 LeftGuidingBoxes, RightGuidingBoxes - These are list of left 
#                                                and right guiding boxes found.
#                 {Rest parameters self explanatory.}
# Description   : This function filters the true left and right guiding boxes
#                 from the list of boxes provided by applying logic asked.
# Return        : LeftGuidingBoxes, RightGuidingBoxes
################################################################################
def SplitAndFindGuidingBoxes(BoxCoordinates, HalfWidthOfImage, GuidingCornerBoxesCenter):
    LeftBoxes = []
    RightBoxes = []

    # Filter all boxes to left and right
    for i in BoxCoordinates:
        if i[0] <= HalfWidthOfImage:
            LeftBoxes.append(i)
        else:
            RightBoxes.append(i)

    # Calling different logic functions as asked.
    if M.INSIDELINE_OR_SCORE_OR_RANSAC_LOGIC == 1:
        LeftGuidingBoxes = FilterGuidingBoxes_InsideLineLogic(LeftBoxes, GuidingCornerBoxesCenter[0], 
                                            GuidingCornerBoxesCenter[3])
        RightGuidingBoxes = FilterGuidingBoxes_InsideLineLogic(RightBoxes, GuidingCornerBoxesCenter[1], 
                                             GuidingCornerBoxesCenter[2])
    
    elif M.INSIDELINE_OR_SCORE_OR_RANSAC_LOGIC == 2:
        LeftGuidingBoxes = FilterGuidingBoxes_ScoreLogic(LeftBoxes)
        RightGuidingBoxes = FilterGuidingBoxes_ScoreLogic(RightBoxes)
    
    elif M.INSIDELINE_OR_SCORE_OR_RANSAC_LOGIC == 3:
        LeftGuidingBoxes = FilterGuidingBoxes_RansacLogic(LeftBoxes)
        RightGuidingBoxes = FilterGuidingBoxes_RansacLogic(RightBoxes)    
    

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

        FinalBoxCoordinates.append([XCoordinates[0], YCoordinates[0], XCoordinates[-1], 
                                    YCoordinates[-1]])

    return FinalBoxCoordinates


################################################################################
# Function      : RANSAC_OnArea
# Parameter     : BoxesList - List of boxes on which logic is to be applied to 
#                             filter boxes.
#                 LengthReq - The length of BoxesList required to match other 
#                             list of guiding boxes.
#                 {Rest parameters are self explanatory}
# Description   : This function applies the ransac motivated algo on the areas 
#                 of boxes to find the most related boxes of required number.
#                 The logic is that if we plot the areas of all the boxes on a 
#                 1D axis, the areas corresponding to the guding boxes will be 
#                 close to each other and the outliers will have different areas 
#                 and their point on the axis will be at some distance thus the 
#                 areas of required boxes will form a cluster and the axis will 
#                 contain some outliers. We will for each box area, see how many 
#                 boxes have area in the range of -to+ of DifferenceInArea from 
#                 that point and these points are known as inliers for that point 
#                 for a particular lenth DifferenceInArea. After getting this, 
#                 we will check that if any box have LengthReq number of inliers 
#                 thus those areas will correspond to guiding boxes. If no such 
#                 cluster is found for a value of DifferenceInArea, then we will 
#                 increment this value by 1 and check again. Small increments 
#                 are done to avoid involving outliers.
# Return        : FinalBoxesList - If required number of boxes are found
#                 BoxesList - If required number of boxes are not found.
################################################################################
def RANSAC_OnArea(BoxesList, LengthReq, ImageArea):
    FinalBoxesList = []
    AreaOfBoxesList = []

    DifferenceInArea = 0

    # Finding area of all respective boxes.
    for Box in BoxesList:
        AreaOfBoxesList.append((Box[0] - Box[2])*(Box[1] - Box[3]))
    

    while DifferenceInArea <= ImageArea:
        TotalInliersList = []
        for i in range(len(AreaOfBoxesList)):
            InlierCount = 0
            InlierList = []
            for j in range(len(AreaOfBoxesList)):
                if (-(DifferenceInArea)) <= (AreaOfBoxesList[i] - AreaOfBoxesList[j])\
                                         <= DifferenceInArea:
                    InlierList.append(j)
                    InlierCount += 1
            InlierList.append(InlierCount)
            TotalInliersList.append(InlierList)

        for InlierList in TotalInliersList:
            if InlierList[-1] == LengthReq:
                print("Found all inliers wrt area.")
                for i in range(len(InlierList)-1):
                    FinalBoxesList.append(BoxesList[InlierList[i]])
                print(AreaOfBoxesList   )    
                return FinalBoxesList
        DifferenceInArea += 1

    print("Cannot find inliers wrt area.")
    return BoxesList


################################################################################
# Function      : RunCode
# Parameter     : MaskedImage - Contains the image masked for black colour.
#                 BoxCoordinates - List of boxes found.
#                 GuidingCornerBoxes - List of the 4 guiding corner boxes.
#                 LeftGuidingBoxes, RightGuidingBoxes - These are list of left 
#                                                and right guiding boxes found.
#                 {Rest parameters are self explanatory}
# Description   : This function calls relevant functions one by one in order
#                 to run program.
# Return        : LeftGuidingBoxes, RightGuidingBoxes
################################################################################
def RunCode(UpperLimitOfValue):
    MaskedImage = MaskImage(UpperLimitOfValue)

    # Finding boxes with logic asked.
    if M.TEMPLATE_OR_CONTOUR_LOGIC == 0:
        BoxCoordinates = FindGuidingBoxes_TemplateLogic(MaskedImage)
    else:
        BoxCoordinates = FindGuidingBoxes_ContourLogic(MaskedImage)

    # Finding guiding corner boxes and their center
    GuidingCornerBoxes = FindGuidingCornerBoxes(BoxCoordinates, MaskedImage.shape)
    GuidingCornerBoxesCenter = CenterOfBoxes(GuidingCornerBoxes)
    LeftGuidingBoxes, RightGuidingBoxes = SplitAndFindGuidingBoxes(BoxCoordinates, 
                                    Image.shape[1] // 2, GuidingCornerBoxesCenter)
    LeftGuidingBoxes = ShrinkTotalBox(LeftGuidingBoxes, MaskedImage)
    RightGuidingBoxes = ShrinkTotalBox(RightGuidingBoxes, MaskedImage)

    # Checking if number of left and right guiding boxes found are equal.
    LenOfLeftGB = len(LeftGuidingBoxes)
    LenOfRightGB = len(RightGuidingBoxes)
    if LenOfLeftGB == LenOfRightGB:
        print("Yes, program working correctly")
    else:
        print("Guiding Boxes not found correctly.")
        print("Appyling RANSAC on areas.")
        # Applying RANSAC inspired algo on areas of boxes of list which have higher 
        # number of boxes.
        if LenOfLeftGB > LenOfRightGB:
            LeftGuidingBoxes = RANSAC_OnArea(LeftGuidingBoxes, LenOfRightGB,\
                                             Image.shape[0]*Image.shape[0])
        else:
            RightGuidingBoxes = RANSAC_OnArea(RightGuidingBoxes, LenOfLeftGB,\
                                              Image.shape[0]*Image.shape[0])

    # If RANSAC logic is used, then find guiding corner values again.
    if M.INSIDELINE_OR_SCORE_OR_RANSAC_LOGIC == 3:
        GuidingCornerBoxes = [LeftGuidingBoxes[0], RightGuidingBoxes[0],\
                              RightGuidingBoxes[-1], LeftGuidingBoxes[-1]]
        GuidingCornerBoxesCenter = CenterOfBoxes(GuidingCornerBoxes)
    
    # =====================Just for visualisation, to be deleted==========================
    ImageCopy = Image.copy()
    for i in LeftGuidingBoxes:
        cv2.rectangle(Image, (i[0], i[1]), (i[2], i[3]), (255, 0, 0), 1)
    for i in RightGuidingBoxes:
        cv2.rectangle(Image, (i[0], i[1]), (i[2], i[3]), (0, 0, 255), 1)
    for i in BoxCoordinates:
        cv2.rectangle(ImageCopy, (i[0], i[1]), (i[2], i[3]), (0, 255, 0), 1)
    for i in GuidingCornerBoxesCenter:
        cv2.circle(Image, i, 2, (0, 255, 0), -1)
    cv2.imshow("GuidingBoxes", Image)
    #cv2.imshow("AllBoxes", ImageCopy)
    # ====================================================================================
    
    return LeftGuidingBoxes, RightGuidingBoxes


################################################################################
# Function      : FindBoundingBoxes
# Parameter     : Image - Reads the input image of OMR sheet.
# Description   : This function makes the input OMR image global and calls 
#                 RunCode to ultimately find the guiding boxes of left side 
#                 and right side.
# Return        : LeftGuidingBoxes, RightGuidingBoxes
################################################################################
def FindBoundingBoxes(InputImage):
    global Image

    Image = InputImage.copy()

    #Checking brightness value and setting upper limit of "Value"
    UpperLimitOfValue = CB.CheckBrightness(Image)
    
    LeftGuidingBoxes, RightGuidingBoxes = RunCode(UpperLimitOfValue)

    cv2.waitKey(1)
    #cv2.destroyAllWindows()

    return LeftGuidingBoxes, RightGuidingBoxes
