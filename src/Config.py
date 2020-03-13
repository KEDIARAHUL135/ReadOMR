###############################################################################
# File          : Config.py
# Created by    : Rahul Kedia
# Created on    : 11/03/2020
# Project       : ReadOMR
# Description   : This file is used to configure the OMR Sheet.
################################################################################

# Detailed documentation for this file is not provided as it is not used continuously in the program.
# To configure a OMR Sheet, call Configure() function with suitable params and follow and fill the instructions.

import cv2
from CropOMR import CropOMR


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping, CroppedImage

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [[x, y]]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append([x, y])
        cropping = False

        while True:
        	Height, Width = Image.shape[:2]
        	if 0 <= refPt[0][0] < Width and 0 <= refPt[1][0] < Width and 0 <= refPt[0][1] < Height and 0 <= refPt[1][1] < Height:
        		CroppedImage = Image[refPt[0][1]: (refPt[1][1] + 1), refPt[0][0]: (refPt[1][0] + 1)]
        		cv2.imshow("CroppedImage", CroppedImage)
        	else:
        		continue
        	Action = cv2.waitKey(1)
        	if Action == 82 and refPt[0][1] > 0:   				# top arrow
        		refPt[0][1] -= 1
        	elif Action == 81 and refPt[0][0] > 0: 				# Left arrow
        		refPt[0][0] -= 1
        	elif Action == 84 and refPt[1][1] < (Height - 1):   # bottom arrow
        		refPt[1][1] += 1
        	elif Action == 83 and refPt[1][0] < (Width - 1):    # right arrow
        		refPt[1][0] += 1
        	elif Action == 119 and refPt[0][1] < refPt[1][1]:   # w
        		refPt[0][1] += 1
        	elif Action == 97 and refPt[0][0] < refPt[1][0]:    # a
        		refPt[0][0] += 1
        	elif Action == 115 and refPt[1][1] > refPt[0][1]:   # s
        		refPt[1][1] -= 1
        	elif Action == 100 and refPt[1][0] > refPt[0][0]:   # d
        		refPt[1][0] -= 1
        	elif Action == 32:                      			# space bar
        		break


def RectBoundingRegion():
    print("In the OMR Sheet image, select the rectangular region which covers the area of the answer(options)\n"
          "in the image for the question starting from the top left corner of the region ending on bottom right\n"
          "corner of the region(drag mouse to expand the area).\n"
          "Press arrow keys to expand the cropped area and \"w, a, s, d\" to decrease the cropped area from the\n"
          "top, left, bottom and right side respectively else press space bar to confirm region.\n"
          "Press y to confirm cropped region.")

    cv2.namedWindow("OMR Image")
    cv2.setMouseCallback("OMR Image", click_and_crop)
    cv2.imshow("OMR Image", Image)

    while True:
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

    QuestionParam = [QuestionName, Corner_X, Corner_Y, Width, Length,
                     NumOfRows, NumOfCols, By_CorR, Alp_or_Num, StartFromIndex]

    return QuestionParam


def ConfirmQuestionParams(QuestionParam):
    print()
    print("Are the following details are correct for your question?")
    print("Question Name                            : {}".format(QuestionParam[0]))
    print("Cropped Region Details                   : Corner_X - {}, Corner_Y - {}, Width - {}, Length - {}"
          .format(QuestionParam[1], QuestionParam[2], QuestionParam[3], QuestionParam[4]))
    print("Number of Rows                           : {}".format(QuestionParam[5]))
    print("Number of Cols                           : {}".format(QuestionParam[6]))
    print("Each letter of answer is by column or row: {}".format(QuestionParam[7]))
    print("Alphabetical(0) or numerical(1)          : {}".format(QuestionParam[8]))
    print("Start from index                         : {}".format(QuestionParam[9]))

    Confirmation = input("Enter Y/N if the details are correct/incorrect : ")

    if Confirmation == "y" or Confirmation == "Y":
        return True
    else:
        return False


def RunCode():
    QuestionParam = AskQuestion()
    while not ConfirmQuestionParams(QuestionParam):
    	print("\nRe-enter details of the above questions - \n")
    	QuestionParam = AskQuestion()

    f.write("{}\n".format(QuestionParam))

    IfAddQ = input("\nAdd another question(Y/N)? ")

    if IfAddQ == "y" or IfAddQ == "Y":
        RunCode()

    return


def Configure(InputImagePath, ShrinkImagePercent, SizeAfterCropping):
    global Image, CroppedImage, f, OMR_Path

    OMR_Name = input("Enter OMR Sheet name : ")
    OMR_Path = "ConfigFiles/" + OMR_Name + "_Config.txt"

    # Open Config.txt file
    f = open(OMR_Path, "w")
    # Read Input OMR Image
    Image = cv2.imread(InputImagePath)
    #Image = cv2.resize(Image, (int(Image.shape[0]*ShrinkImagePercent), int(Image.shape[1]*ShrinkImagePercent)))


    CroppedImage = CropOMR(Image, SizeAfterCropping)
    Image = CroppedImage.copy()
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    RunCode()

    f.close()
