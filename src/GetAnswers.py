###############################################################################
# File          : GetAnswers.py
# Created by    : Rahul Kedia
# Created on    : 05/03/2020
# Project       : ReadOMR
# Description   : This file contains the class of source code responsible to
#                 find the answer to a particular question.
################################################################################
import numpy as np
import cv2
import macros as M


class FindAnswer:
    ################################################################################
    # Method        : __init__
    # Parameter     : C_X, C_Y - It stores the coordinate of top left
    #                            corner of the answer area(rectangle).
    #                 Width, Length - It stores the coordinate of top left
    #                                 corner of the answer area(rectangle).
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
    def __init__(self, Corner_X, Corner_Y, Width, Length, NumOfRows, NumOfCols, By_CorR, Alp_or_Num, StartFromIndex=0):
        self.C_X = Corner_X
        self.C_Y = Corner_Y
        self.Width = Width
        self.Length = Length
        self.NumOfRows = NumOfRows
        self.NumOfCols = NumOfCols
        self.By_CorR = By_CorR
        self.Alp_or_Num = Alp_or_Num
        self.HistogramMatrix = np.zeros((NumOfRows, NumOfCols), dtype=int)
        self.AnswerString = ""
        self.StartFromIndex = StartFromIndex

    ################################################################################
    # Method        : AnswerImage
    # Parameter     : OMRImage - It holds the OMR sheet image after cropping it
    #                            from corner circles.
    # Description   : This method answer area from the OMR image
    # Return        : -
    ################################################################################
    def AnswerImage(self, OMRImage):
        self.Image = OMRImage[self.C_Y:self.C_Y + self.Length, self.C_X:self.C_X + self.Width]
        
    ################################################################################
    # Method        : ThresholdImage
    # Parameter     : -
    # Description   : This method converts the image to thresholded grayscale.
    # Return        : -
    ################################################################################
    def ThresholdImage(self):
        self.ThreshImage = cv2.cvtColor(self.Image, cv2.COLOR_BGR2GRAY)
        ret, self.ThreshImage = cv2.threshold(self.ThreshImage, M.ThresholdImageAt, 255, cv2.THRESH_BINARY)


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
    def FindHistogram(self, i, j, HeightOfGrid, WidthOfGrid):
        GridImage = self.ThreshImage[j:j+WidthOfGrid, i:i+HeightOfGrid]
        Height, Width = GridImage.shape[:2]
        NumOfWhite = NumOfBlack = 0

        for i in range(Height):
            for j in range(Width):
                if GridImage[i, j] == 255:
                    NumOfWhite += 1
                else:
                    NumOfBlack += 1

        return NumOfWhite, NumOfBlack

    ################################################################################
    # Method        : MakeGrid_EvalHistogram
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
    #                       integer value of pixel coordinate. When the become
    #                       greater than 1, the pixel coordinate is increased
    #                       by 1 to reduce error.
    #                 HistMatrix_i, HistMatrix_j - These variables are used to
    #                                              iterate over HistogramMatrix.
    # Description   : This method makes grid on image and calls FindHistogram method 
    #                 to find the histogram for the grid and saves its value in 
    #                 HistogramMatrix.
    # Return        : -
    ################################################################################
    def MakeGrid_EvalHistogram(self):
        ImageCopy = self.Image.copy()
        ThreshImageCopy = self.ThreshImage.copy()

        Height, Width = self.Image.shape[:2]
        GridWidth = Width/self.NumOfCols
        GridHeight = Height/self.NumOfRows
        
        i = 0
        HistMatrix_i = 0
        while i < Height:
            j = 0
            HistMatrix_j = 0
            while j < Width:
                #cv2.rectangle(ImageCopy, (int(j), int(i)), (int(j+GridWidth-1), int(i+GridHeight-1)), (0, 255, 0), 1)
                #cv2.rectangle(ThreshImageCopy, (int(j), int(i)), (int(j+GridWidth-1), int(i+GridHeight-1)), (0, 255, 0), 1)
                #cv2.imshow("GridImage", ImageCopy)
                #cv2.imshow("ThreshImage", ThreshImageCopy)


                NumOfWhite, NumOfBlack = self.FindHistogram(int(j), int(i), int(GridWidth-1), int(GridHeight-1))
                self.HistogramMatrix[HistMatrix_i, HistMatrix_j] = NumOfBlack

                HistMatrix_j += 1
                
                if HistMatrix_j >= self.NumOfCols:
                    break

                j += GridWidth
                
            HistMatrix_i += 1
            if HistMatrix_i >= self.NumOfRows:
                break

            i += GridHeight

    ################################################################################
    # Method        : FindAnswerString
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
    def FindAnswerString(self):
        # Finding max index for all col/row in HistMatrix
        if self.By_CorR == 'C':
            MaxIndex = np.zeros(self.HistogramMatrix.shape[1], dtype=int)

            for i in range(self.NumOfCols):
                IndexOfMax = -1
                Max = 0
                for j in range(self.NumOfRows):
                    if Max < self.HistogramMatrix[j, i] and self.HistogramMatrix[j, i] >= M.MIN_NUM_OF_BLACK_FOR_ANSWER:
                        Max = self.HistogramMatrix[j, i]
                        IndexOfMax = j
                MaxIndex[i] = IndexOfMax

        elif self.By_CorR == 'R':
            MaxIndex = np.zeros(self.HistogramMatrix.shape[0], dtype=int)

            for i in range(self.NumOfRows):
                IndexOfMax = -1
                Max = 0
                for j in range(self.NumOfCols):
                    if Max < self.HistogramMatrix[i, j] and self.HistogramMatrix[i, j] >= M.MIN_NUM_OF_BLACK_FOR_ANSWER:
                        Max = self.HistogramMatrix[i, j]
                        IndexOfMax = j
                MaxIndex[i] = IndexOfMax

        # Finding Answer from MaxIndex
        AnswerLength = len(MaxIndex)        # Length of answer is equal to number of max index found

        for i in range(AnswerLength):
            if self.Alp_or_Num == 0:                        # Alphabet if 0
                self.AnswerString += M.Alphabet[MaxIndex[i] + self.StartFromIndex]
            elif self.Alp_or_Num == 1:                      # Number if 1
                if MaxIndex[i] == -1:
                    self.AnswerString += '_'
                else:    
                    self.AnswerString += str(MaxIndex[i] + self.StartFromIndex)

    ################################################################################
    # Method        : FindAnswer
    # Parameter     : OMRImage - Contains the image of Cropped OMR provided.
    # Description   : This method calls other suitable methods line wise to find the 
    #                 answer string of the question.
    # Return        : AnswerString
    ################################################################################
    def FindAnswer(self, OMRImage):
        self.AnswerImage(OMRImage)
        self.ThresholdImage()
        self.MakeGrid_EvalHistogram()
        self.FindAnswerString()

        #cv2.waitKey(0)

        return self.AnswerString
