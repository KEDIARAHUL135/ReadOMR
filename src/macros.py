###############################################################################
# File          : macros.py
# Created by    : Rahul Kedia
# Created on    : 10/01/2020
# Project       : ReadOMR
# Description   : This file contains the modifiable macros (variables)
#                 used in the main source code. By playing with these
#                 variables onyl, one can modify the main source code
#                 to adapt to different types of OMR Sheets and we can
#                 also enhance the output of the code.
################################################################################


# Input Image Path
InputImagePath = "InputImages/Blank.jpeg"


# Size of OMR Sheet - square of length -> Size
Size = 800  # DONOT CHANGE THIS


# Thershold length of corner circle
## It menas that the corner circle must be present at what max distance from the boundary
ThreshLengthCC = 90


# Macros for HoughCircle
dp = 1.3
MinRadius = 0
MaxRadius = 20