###############################################################################
# File          : Config.py
# Created by    : Rahul Kedia
# Created on    : 11/03/2020
# Project       : ReadOMR
# Description   : This file is used to configure the OMR Sheet.
################################################################################

import cv2
import numpy as np


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping, CroppedImage

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False
        CroppedImage = Image[refPt[0][1]: (refPt[1][1] + 1), refPt[0][0]: (refPt[1][0] + 1)]
        cv2.imshow("CroppedImage", CroppedImage)


def RectBoundingRegion():
    print("In the OMR Sheet image, select the rectangular region which covers the area of the answer(options)\n "
          "in the image for the question starting from the top left corner of the region ending on bottom right\n "
          "corner of the region(drag mouse to expand the area).")

    cv2.namedWindow("OMR Image")
    cv2.setMouseCallback("OMR Image", click_and_crop)
    cv2.imshow("OMR Image", Image)

    while True:
        # display the image and wait for a keypress
        #cv2.imshow("RectBoundingRegion", CroppedImage)
        key = cv2.waitKey(1) & 0xFF

        # if the 'c' key is pressed, break from the loop
        if key == ord("Y") or key == ord("y"):
            cv2.destroyAllWindows()
            break




def AskQuestion():
    QuestionName = input("Enter name of the question : ")
    RectBoundingRegion()
    Corner_X = refPt[0][0]
    Corner_Y = refPt[0][1]
    Width = refPt[1][0] - refPt[0][0] + 1
    Length = refPt[1][1] - refPt[0][1] + 1
    NumOfRows = int(input("Enter the number of rows in OMR : "))
    NumOfCols = int(input("Enter the number of columns in OMR : "))
    By_CorR = input('Each letter of the answer is present in column or row? (Press "R" for Row or "C" for column): ')
    Alp_or_Num = int(input("Answer is alphabetical or numerical(Enter 0 if alphabetical or 1 if numerical): "))
    StartFromIndex = int(input("Answer is started from index : "))

    QuestionParam = [QuestionName, Corner_X, Corner_Y, Width, Length, NumOfRows, NumOfCols, By_CorR, Alp_or_Num, StartFromIndex]

    return QuestionParam


def RunCode():
    QuestionParam = AskQuestion()
    f.write("{}\n".format(QuestionParam))


def Configure(InputImagePath=None, ResizeInputImageTo=None):
    global Image, f

    # Open Config.txt file
    f = open("Config.txt", "w")
    # Read and resize Input OMR Image
    if InputImagePath == None:
        Image = cv2.imread("InputImages/Blank2.jpeg")
    else:
        Image = cv2.imread(InputImagePath)

    if ResizeInputImageTo == None:
        Image = cv2.resize(Image, (600, 800))       # Default Value is set to (600, 800).
    else:
        Image = cv2.resize(Image, ResizeInputImageTo)

    RunCode()

    f.close()

Configure()
