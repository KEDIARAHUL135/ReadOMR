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
# Class         : Answers
# Methods       : __init__ - This method crops the omr for a question
#                            as per parameters given.
# Description   : This class is called to crop omr for different questions.
# Return        : -
################################################################################
class Answers:
    ################################################################################
    # Method        : __init__
    # Parameter     : OMRImage/Img - It holds the OMR Image after corner
    #                                detection and projective transform
    #                 {Rest all the parameters have their usual meanings as
    #                 mentioned in macros.py file. Each of these parameter is
    #                 for different question.}
    # Description   : This method crops the image for different question as
    #                 per parameters provided in ROI_Answer class.
    # Return        : -
    ################################################################################
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


################################################################################
# Class         : GetAnswer
# Methods       : __init__ - This method initialises the local variables
#                            for the question.
#                 ThresholdImage - This method converts the image to
#                                  thresholded grayscale.
#                 FindHistogram - This method takes in coordinates of a grid
#                                 and finds number of black and num of white
#                                 pixels in each grid.
#                 FindFinalAnswer - This method finds the answer string of
#                                   a particular question.
#                 MakeGrid - This method forms grid and calls other methods
#                            to find answer string.
# Description   : This class is called to get the final answer string.
# Return        : -
################################################################################
class GetAnswer:
    ################################################################################
    # Method        : __init__
    # Parameter     : Image - It holds the image of answer for a question
    #                 NumOfRows - It stores the number of rows present in OMR
    #                             for that question.
    #                 NumOfCols - It stores the number of cols present in OMR
    #                             for that question.
    #                 By_Cor_R - It tells that the answer is present in row wise
    #                            fashion or by column wise. {Row is horizontal
    #                            lines and Column is vertical line}.
    #                            Its value - For Row wise - 'R'
    #                                        For column wise - 'C'.
    #                 Alp_or_Num - It tells that answer is in alphabets or numbers.
    #                              0 for Alphabet and 1 for number.
    #                 HistogramMatrix - It stores the number of Black/White pixel
    #                                   in each grid in a 2D array. Each element
    #                                   corresponds to the grid at same place in
    #                                   the image.
    #                 AnswerString - It holds the answer to the question.
    #                 StartFromIndex - It tells if the options are starting
    #                                  from A/0 or any other alphabet/number.
    # Description   : This method initialises different parameters for the question.
    # Return        : -
    ################################################################################
    def __init__(self, Image, NumOfRows, NumOfCols, By_CorR, Alp_or_Num, StartFromIndex = 0):
        self.Image = Image
        self.NumOfRows = NumOfRows
        self.NumOfCols = NumOfCols
        self.By_CorR = By_CorR
        self.Alp_or_Num = Alp_or_Num
        self.HistogramMatrix = np.zeros((NumOfRows, NumOfCols), dtype=int)
        self.AnswerString = ""
        self.StartFromIndex = StartFromIndex

    ################################################################################
    # Method        : ThresholdImage
    # Parameter     : -
    # Description   : This method converts the image to thresholded grayscale.
    # Return        : -
    ################################################################################
    def ThresholdImage(self):
        self.Image = cv2.cvtColor(self.Image, cv2.COLOR_BGR2GRAY)
        ret, self.Image = cv2.threshold(self.Image, M.ThresholdImageAt, 255, cv2.THRESH_BINARY)

    ################################################################################
    # Method        : FindHistogram
    # Parameter     : (i, j) - This is the top left coordinate of a grid box.
    #                 WidthOfGrid - This contains the width of the grid box.
    #                 HeightOfGrid - This contains the height of the grid box.
    #                 NumOfWhite - It counts the number of White pixel in the grid box.
    #                 NumOfBlack - It counts the number of Black pixel in the grid box.
    # Description   : This method converts the image to thresholded grayscale.
    # Return        : NumOfWhite, NumOfBlack
    ################################################################################
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

    ################################################################################
    # Method        : FindFinalAnswer
    # Parameter     : MaxIndex - It is a array which stores the index corresponding
    #                            to the element containing maximum number of black
    #                            pixel for each row/col.
    #                 IndexOfMax & Max - These 2 are temporary variables for
    #                                    finding MaxIndex.
    #                 AnswerLength - This holds the total number of characters
    #                                the answer is holding{Length of MaxIndex}.
    # Description   : This method finds element with maximum value in each row/col
    #                 and according to that appends the final answer string.
    # Return        : -
    ################################################################################
    def FindFinalAnswer(self):
        # Finding max index for all col/row in HistMatrix
        if self.By_CorR == 'C':
            MaxIndex = np.zeros(self.HistogramMatrix.shape[1], dtype=int)

            for i in range(self.NumOfCols):
                IndexOfMax = -1
                Max = 0
                for j in range(self.NumOfRows):
                    if Max < self.HistogramMatrix[j, i]:
                        Max = self.HistogramMatrix[j, i]
                        IndexOfMax = j
                MaxIndex[i] = IndexOfMax

        elif self.By_CorR == 'R':
            MaxIndex = np.zeros(self.HistogramMatrix.shape[0], dtype=int)

            for i in range(self.NumOfRows):
                IndexOfMax = -1
                Max = 0
                for j in range(self.NumOfCols):
                    if Max < self.HistogramMatrix[i, j]:
                        Max = self.HistogramMatrix[i, j]
                        IndexOfMax = j
                MaxIndex[i] = IndexOfMax

        # Finding Answer from MaxIndex
        AnswerLength = len(MaxIndex)        # Length of answer is equal to number of max index found

        for i in range(AnswerLength):
            if self.Alp_or_Num == 0:                        # Alphabet if 0
                self.AnswerString += M.Alphabet[MaxIndex[i] + self.StartFromIndex]
            elif self.Alp_or_Num == 1:                      # Number if 1
                self.AnswerString += M.Numbers[MaxIndex[i] + self.StartFromIndex]

    ################################################################################
    # Method        : MakeGrid_FindAnswer
    # Parameter     : Height, Width - These hold the height and width respectively
    #                                 of complete answer image.
    #                 WidthOfGrid - This contains the width of the grid box.
    #                 HeightOfGrid - This contains the height of the grid box.
    #                 RemainderOfWidth, RemainderOfHeight - As the exact value of
    #                       height and width of grid box contains decimal value
    #                       also but pixel position value cannot be decimal so
    #                       these two variables contains the decimal value of
    #                       width and height of grid respectively.
    #                 WidthPixelSkipped, HeightPixelSkipped - These variables
    #                       count the decimal value of pixels skipped due to
    #                       integer value of piel coordinate. When the become
    #                       greater than 1, the pixel coordinate is increased
    #                       by 1 to reduce error.
    #                 HistMatrix_i, HistMatrix_j - These variables are used to
    #                                              iterate over HistogramMatrix.
    # Description   : This method finds element with maximum value in each row/col
    #                 and according to that appends the final answer string.
    # Return        : -
    ################################################################################
    def MakeGrid_FindAnswer(self):
        self.ThresholdImage()

        Height, Width = self.Image.shape[:2]
        WidthOfGrid = (Width//self.NumOfCols)
        HeightOfGrid = (Height//self.NumOfRows)
        RemainderOfWidth = ((Width/self.NumOfCols) - WidthOfGrid)
        RemainderOfHeight = ((Height/self.NumOfRows) - HeightOfGrid)
        WidthPixelSkipped = 0
        HeightPixelSkipped = 0
        HistMatrix_i = 0


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

                # Uncomment line to form grid on the image.
                ## {NOTE - comment it again in order to see actual answer}
                #cv2.rectangle(self.Image, (i, j), (i+WidthOfGrid, j+HeightOfGrid), (0, 255, 0), 1)

                NumOfWhite, NumOfBlack = self.FindHistogram(i, j, WidthOfGrid, HeightOfGrid)
                self.HistogramMatrix[HistMatrix_j, HistMatrix_i] = NumOfBlack

                HistMatrix_j += 1
                if HistMatrix_j >= self.NumOfRows:
                    break

            HistMatrix_i += 1
            if HistMatrix_i >= self.NumOfCols:
                break

        self.FindFinalAnswer()


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
        cv2.imshow("Student's Name", AnsImages.StN)
        cv2.imshow("Mobile Number", AnsImages.MN)
        cv2.imshow("Class", AnsImages.Class)
        cv2.imshow("Branch", AnsImages.Branch)
        cv2.imshow("Booklet Number", AnsImages.BN)
        cv2.imshow("School's Name", AnsImages.ScN)
        cv2.imshow("Section", AnsImages.Section)
        cv2.imshow("Father's Name", AnsImages.FN)
        cv2.imshow("Answers - 1 to 5", AnsImages.A_1t5)
        cv2.imshow("Answers - 6 to 10", AnsImages.A_6t10)
        cv2.imshow("Answers - 11 to 15", AnsImages.A_11t15)
        cv2.imshow("Answers - 16 to 20", AnsImages.A_16t20)
        cv2.imshow("Answers - 21 to 25", AnsImages.A_21t25)
        cv2.imshow("Answers - 26 to 30", AnsImages.A_26t30)


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

    # Final coordinates of 4 corner circles in another image
    FinalPoints = np.float32([[0., 0.], [(M.Size - 1), 0.],\
                              [(M.Size - 1), (M.Size - 1)], [0., (M.Size - 1)]])

    # Applying projective transform
    ProjectiveMatrix = cv2.getPerspectiveTransform(InitialPoints, FinalPoints)
    OutputImage = cv2.warpPerspective(InputImage, ProjectiveMatrix, NewSize)

    return OutputImage


################################################################################
# Function      : ExtractAnswers
# Parameter     : AnswerDict - It is the answer dictonary for each question.
#                 AnsImages - It is the object of class Answers containing
#                             cropped images of answers for each question.
#                 {Rest all the parameters have their usual meanings as
#                 mentioned in macros.py file. Each of these parameter is
#                 for different question.}
# Description   : This function initialises objects for different questions
#                 and then calls suitable method to fnd answer and then
#                 stores the answers in a dictonary.
# Return        : AnswerDict
################################################################################
def ExtractAnswers(OMRImage):
    AnswerDict = {}
    AnsImages = Answers(M.StN, M.MN, M.Class, M.Branch, M.BN, M.ScN, M.Section, M.FN, M.A_1t5,\
                  M.A_6t10, M.A_11t15, M.A_16t20, M.A_21t25, M.A_26t30, OMRImage)

    PrintImages(AnsImages=AnsImages)    # Uncomment to see all the answer images

    # Creating objects for different Questions
    ## NOTE - Pass the parameters carefully for each question.
    StN = GetAnswer(AnsImages.StN, 25, 25, 'C', 0)  # NOTE - There is a bug here- Num of rows should br 26 instead of 25
    MN = GetAnswer(AnsImages.MN, 10, 10, 'C', 1)
    Class = GetAnswer(AnsImages.Class, 1, 7, 'R', 1, 4)
    Section = GetAnswer(AnsImages.Section, 2, 7, 'R', 0)
    A_1t5 = GetAnswer(AnsImages.A_1t5, 5, 4, 'R', 0)
    A_6t10 = GetAnswer(AnsImages.A_6t10, 5, 4, 'R', 0)
    A_11t15 = GetAnswer(AnsImages.A_11t15, 5, 4, 'R', 0)
    A_16t20 = GetAnswer(AnsImages.A_16t20, 5, 4, 'R', 0)
    A_21t25 = GetAnswer(AnsImages.A_21t25, 5, 4, 'R', 0)
    A_26t30 = GetAnswer(AnsImages.A_26t30, 5, 4, 'R', 0)

    StN.MakeGrid_FindAnswer()
    MN.MakeGrid_FindAnswer()
    Class.MakeGrid_FindAnswer()
    Section.MakeGrid_FindAnswer()
    A_1t5.MakeGrid_FindAnswer()
    A_6t10.MakeGrid_FindAnswer()
    A_11t15.MakeGrid_FindAnswer()
    A_16t20.MakeGrid_FindAnswer()
    A_21t25.MakeGrid_FindAnswer()
    A_26t30.MakeGrid_FindAnswer()

    AnswerDict["Student's Name"] = StN.AnswerString
    AnswerDict["Mobile Number"] = MN.AnswerString
    AnswerDict["Class"] = Class.AnswerString
    AnswerDict["Section"] = Section.AnswerString
    AnswerDict["Answers 1-5"] = A_1t5.AnswerString
    AnswerDict["Answers 6-10"] = A_6t10.AnswerString
    AnswerDict["Answers 11-15"] = A_11t15.AnswerString
    AnswerDict["Answers 16-20"] = A_16t20.AnswerString
    AnswerDict["Answers 21-25"] = A_21t25.AnswerString
    AnswerDict["Answers 26-30"] = A_26t30.AnswerString

    return AnswerDict


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
#                 AnswerDict - It is the answer dictonary for each question.
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

    ## Print corner circles
    PrintImages(CornerCircles, True)      # Uncomment to print corner circles

    # Applying Projective transformation.
    CroppedOMRSheetImage = ProjectiveTransform(CornerCircles)

    # Extract different answers
    AnswerDict = ExtractAnswers(CroppedOMRSheetImage)

    return AnswerDict


# Crop the required OMR sheet for answer detection
AnswerDict = CropOMR_FindAnswers()

print(AnswerDict)
cv2.waitKey(0)
cv2.destroyAllWindows()