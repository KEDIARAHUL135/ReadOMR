###############################################################################
# File          : CropOMR.py
# Created by    : Rahul Kedia
# Created on    : 12/03/2020
# Project       : ReadOMR
# Description   : This file is used to crop the OMR Sheet from appropriate 
#                 positions and projective transform it for further use.
################################################################################


import cv2
import numpy as np
import macros as M
from FindBoundingBoxes import FindBoundingBoxes


################################################################################
# Function      : SetCoordinatesOfCornerGuidingBoxes
# Parameter     : LeftGuidingBoxes, RightGuidingBoxes - List of guiding boxes 
#                               found on the left and right hand side of the OMR.
#                 Size - New size of image.
#                 ExpandSideBy - It is a list of 2 values by which we want to 
#                                expand the top and bottom side respectively.
#                 InitialCorners - It contains the initial coordinates of 4
#                             corners in clockwise order starting from top left.
#                 FinalCorners - It contains the final coordinates of the 4
#                           corners in the same order as that of InitialCorners.
#                 Coordinates - It holds the value of initial coordinates in a 
#                               from of list for better readability.
# Description   : This sets the Initial and Final coordinates of the guiding
#                 corner boxes.
# Return        : InitialCorners, FinalCorners
################################################################################
def SetCoordinatesOfCornerGuidingBoxes(LeftGuidingBoxes, RightGuidingBoxes, Size, ExpandSideBy):
    # Setting the value of Coordinates to beautify the code.
    Coordinates = []
    Coordinates.append((LeftGuidingBoxes[0][0] + LeftGuidingBoxes[0][2])//2)
    Coordinates.append((LeftGuidingBoxes[0][1] + LeftGuidingBoxes[0][3])//2 - ExpandSideBy[0])
    Coordinates.append((RightGuidingBoxes[0][0] + RightGuidingBoxes[0][2])//2)
    Coordinates.append((RightGuidingBoxes[0][1] + RightGuidingBoxes[0][3])//2 - ExpandSideBy[0])
    Coordinates.append((RightGuidingBoxes[-1][0] + RightGuidingBoxes[-1][2])//2)
    Coordinates.append((RightGuidingBoxes[-1][1] + RightGuidingBoxes[-1][3])//2 + ExpandSideBy[1])
    Coordinates.append((LeftGuidingBoxes[-1][0] + LeftGuidingBoxes[-1][2])//2)
    Coordinates.append((LeftGuidingBoxes[-1][1] + LeftGuidingBoxes[-1][3])//2   + ExpandSideBy[1])
    
    # Checking boundary conditions and assigning the value.
    if Coordinates[1] >= 0 and Coordinates[3] >= 0 and Coordinates[5] <= (Size[1] - 1) and\
       Coordinates[7] <= (Size[1] - 1):
        InitialCorners = np.float32([[Coordinates[0], Coordinates[1]], 
                                     [Coordinates[2], Coordinates[3]],
                                     [Coordinates[4], Coordinates[5]],
                                     [Coordinates[6], Coordinates[7]]])
    else:
      print("\n\nCannot expand side more than this, if the output is still wrong, Input different image\n\n")


    # Final coordinates of 4 corner circles in another image
    FinalCorners = np.float32([[0., 0.],
                               [(Size[0] - 1), 0.],
                               [(Size[0] - 1), (Size[1] - 1)],
                               [0., (Size[1] - 1)]])

    return InitialCorners, FinalCorners


################################################################################
# Function      : ProjectiveTransform
# Parameter     : OutputImage - It is the image of cropped and projective 
#                               transformed OMR Sheet.
#                 InitialCorners - It contains the initial coordinates of 4 corners
#                                  in clockwise order starting from top left.
#                 FinalCorners - It contains the final coordinates of 4 corners
#                                in clockwise order starting from top left.
# Description   : This function applies projective transform on cropped OMR Sheet.
# Return        : OutputImage
################################################################################
def ProjectiveTransform(InputImage, InitialCorners, FinalCorners):
    Rows, Cols = InputImage.shape[:2]
    
    # Applying projective transform
    ProjectiveMatrix = cv2.getPerspectiveTransform(InitialCorners, FinalCorners)
    OutputImage = cv2.warpPerspective(InputImage, ProjectiveMatrix, (Cols, Rows))

    return OutputImage


################################################################################
# Function      : CropOMR
# Parameter     : InputImage - It is the image of OMR Sheet.
#                 SetExpandSideByValue - Flag for if we want to set the 
#                               ExpandSideBy value or else use it.(0 by default
#                               for using else 1 for setting the value)
#                 CroppedOMR - It contains the image of cropped OMR Sheet.
#                 ExpandSideBy - It is a list of 2 values by which we want to 
#                                expand the top and bottom side respectively.
#                 {Other parameters are self explanatory.}
# Description   : This function calls suitable functions one by one for
#                 detecting corner guiding boxes, and transforming the OMR
#                 sheet.
# Return        : CroppedOMR, ExpandSideBy
################################################################################
def CropOMR(InputImage, SetExpandSideByValue=0, ExpandSideBy=[0, 0]):
    LeftGuidingBoxes, RightGuidingBoxes = FindBoundingBoxes(InputImage)

    # Using infinite loop to set ExpandSideBy value or it will break in the first iteration 
    # only if we donot wish to set the value.
    while 1:
        # Setting Initial and Final corners values.
        InitialCorners, FinalCorners = SetCoordinatesOfCornerGuidingBoxes(LeftGuidingBoxes, 
                RightGuidingBoxes, (InputImage.shape[1], InputImage.shape[0]), ExpandSideBy)
        
        # Applying Projective transformation.
        CroppedOMR = ProjectiveTransform(InputImage, InitialCorners, FinalCorners)
        CroppedOMR = cv2.resize(CroppedOMR, M.RESIZE_TO)
        cv2.imshow("CroppedOMR", CroppedOMR)

        # Ask for setting the value of ExpandSideBy if prompted.
        if SetExpandSideByValue:
            print("\nCheck if all the answer circles of the OMR are present in the CroppedOMR image.")
            print("If yes then press 'Y' else press top arrow key or bottom arrow key")
            print("to expand the side from respective sides.\n")
            Key = cv2.waitKey(0)
            if Key == 89 or Key == 121:   # Key = 'Y'/'y'
                break
            elif Key == 82:               # Top key pressed
                ExpandSideBy[0] += 10
            elif Key == 84:               # Bottom key pressed
                ExpandSideBy[1] += 10
        else:
            break

    return CroppedOMR, ExpandSideBy
