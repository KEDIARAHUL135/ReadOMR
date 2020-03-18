###############################################################################
# File          : CropOMR.py
# Created by    : Rahul Kedia
# Created on    : 12/03/2020
# Project       : ReadOMR
# Description   : This file is used to projective transform and save the OMR
#                 Sheet.
################################################################################


import cv2
import numpy as np
import macros as M
from FindBoundingBoxes import FindBoundingBoxes


################################################################################
# Function      : SetCoordinatesOfCornerGuidingBoxes
# Parameter     : InitialCorners - It contains the initial coordinates of 4
#                             corners in clockwise order starting from top left.
#                 FinalCorners - It contains the final coordinates of the 4
#                           corners in the same order as that of InitialCorners.
# Description   : This sets the Initial and Final coordinates of the guiding
#                 corner boxes.
# Return        : InitialCorners, FinalCorners
################################################################################
def SetCoordinatesOfCornerGuidingBoxes(LeftGuidingBoxes, RightGuidingBoxes, Size, ExpandSideBy):
    if ((LeftGuidingBoxes[0][1] + LeftGuidingBoxes[0][3])//2 - ExpandSideBy[0]) >= 0 and\
       ((RightGuidingBoxes[0][1] + RightGuidingBoxes[0][3])//2 - ExpandSideBy[0]) >= 0 and\
       ((RightGuidingBoxes[-1][1] + RightGuidingBoxes[-1][3])//2 + ExpandSideBy[1]) <= (Size[1] - 1) and\
       ((LeftGuidingBoxes[-1][1] + LeftGuidingBoxes[-1][3])//2   + ExpandSideBy[1]) <= (Size[1] - 1):
        InitialCorners = np.float32([[(LeftGuidingBoxes[0][0] + LeftGuidingBoxes[0][2])//2,
                                      (LeftGuidingBoxes[0][1] + LeftGuidingBoxes[0][3])//2 - ExpandSideBy[0]],
                                     [(RightGuidingBoxes[0][0] + RightGuidingBoxes[0][2])//2,
                                      (RightGuidingBoxes[0][1] + RightGuidingBoxes[0][3])//2 - ExpandSideBy[0]],
                                     [(RightGuidingBoxes[-1][0] + RightGuidingBoxes[-1][2])//2,
                                      (RightGuidingBoxes[-1][1] + RightGuidingBoxes[-1][3])//2 + ExpandSideBy[1]],
                                     [(LeftGuidingBoxes[-1][0] + LeftGuidingBoxes[-1][2])//2,
                                      (LeftGuidingBoxes[-1][1] + LeftGuidingBoxes[-1][3])//2   + ExpandSideBy[1]]])
    else:
      print("\n\nCannot expand side more than this, if the output is still wrong, Input different image\n\n")


    # Final coordinates of 4 corner circles in another image
    FinalCorners = np.float32([[0., 0.],
                               [(Size[0] - 1), 0.],
                               [(Size[0] - 1), (Size[1] - 1)],
                               [0., (Size[1] - 1)]])

    if M.EXPAND_INITIAL_POINTS:
        ExpandInitialCorners(InitialCorners)

    return InitialCorners, FinalCorners


################################################################################
# Function      : ExpandInitialCorners
# Parameter     : InitialCorners - It contains the initial coordinates of 4
#                             corners in clockwise order starting from top left.
# Description   : This function corrects the value of InitialCorners parameter
#                 if and as required to expand the image after corner detection
#                 for cropping.
# Return        : InitialCorners
################################################################################
def ExpandInitialCorners(InitialCorners):
    for k in range(4):
        if (k//2) == 0:
            InitialCorners[k % 4][k % 2] -= M.EXPAND_BY[k]
            InitialCorners[(k - 1) % 4][k % 2] -= M.EXPAND_BY[k]
        else:
            InitialCorners[k % 4][k % 2] += M.EXPAND_BY[k]
            InitialCorners[(k - 1) % 4][k % 2] += M.EXPAND_BY[k]

    return InitialCorners


################################################################################
# Function      : ProjectiveTransform
# Parameter     : OutputImage - It is the image of cropped OMR Sheet. It is
#                               cropped in rectangle with the help of four
#                               printed corner circles of the OMR Sheet.
#                 InitialCorners - It contains the initial coordinates of
#                                 four corners in clockwise order
#                                 starting from top left.
#                 FinalCorners - It contains the final coordinates of
#                               four corners in clockwise order
#                               starting from top left.
# Description   : This function calls suitable functions one by one for
#                 detecting circles, and the rearranging/resizing the OMR
#                 sheet so that then the answers can be found from OMR Sheet.
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
#                 NewSize - It contains the new size of the image after cropping.
#                 CroppedOMR - It contains the image of cropped OMR Sheet.
# Description   : This function calls suitable functions one by one for
#                 detecting corner guiding boxes, and transforming the OMR
#                 sheet.
# Return        : CroppedOMR
################################################################################
def CropOMR(InputImage, SetExpandSideByValue=0, ExpandSideBy=[0, 0], SaveImage=False):
    LeftGuidingBoxes, RightGuidingBoxes = FindBoundingBoxes(InputImage)

    while 1:
      InitialCorners, FinalCorners = SetCoordinatesOfCornerGuidingBoxes(LeftGuidingBoxes, 
              RightGuidingBoxes, (InputImage.shape[1], InputImage.shape[0]), ExpandSideBy)
      # Applying Projective transformation.
      CroppedOMR = ProjectiveTransform(InputImage, InitialCorners, FinalCorners)
      CroppedOMR = cv2.resize(CroppedOMR, M.RESIZE_TO)
      cv2.imshow("CroppedOMR", CroppedOMR)

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

    if SaveImage:
        cv2.imwrite("CroppedOMR.png", CroppedOMR)

    return CroppedOMR, ExpandSideBy
