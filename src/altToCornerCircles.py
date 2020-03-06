###############################################################################
# File          : altToCornerCircles.py
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
    UpperRange = np.array([0, 0, 130])

    MaskedImage = cv2.inRange(HSVImage, LowerRange, UpperRange)

    cv2.imshow("Masked", MaskedImage)

    return MaskedImage


MaskedImage = MaskImage(Image)

cv2.waitKey(0)
cv2.destroyAllWindows()