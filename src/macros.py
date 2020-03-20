###############################################################################
# File          : macros.py
# Created by    : Rahul Kedia
# Created on    : 10/01/2020
# Project       : ReadOMR
# Description   : This file contains the modifiable macros (variables)
#                 used in the main source code. By playing with these
#                 variables only, one can modify the main source code
#                 to adapt to different types of OMR Sheets and we can
#                 also enhance the output of the code.
################################################################################


# Resize image to this length every time in the code to get uniform output.
RESIZE_TO = (750, 950)

# Minimum score required for a box to be considered as guiding box.
MIN_SCORE_REQ = 8

# Minimum and maximum contour(Rect bounding the contour) areas for it to be considered as guiding.
MIN_CONTOUR_AREA = 12
MAX_CONTOUR_AREA = 500

# Run code with the use of template logic or with contour logic.
TEMPLATE_OR_CONTOUR_LOGIC = 1               # 0 for templatelogic and 1 for contour logic

# Run code with Inside line logic, or score logic or ransac logic.
INSIDELINE_OR_SCORE_OR_RANSAC_LOGIC = 3     # 1 for inside line logic and 2 for score logic and 3 for ransac logic

# Used in ransac logic, it defines that at what max distance from the line, a inlier can be considered.
# Inlier are considered from -MAX_INLIER_DIST to +MAX_INLIER_DIST from the line(as 0).
MAX_INLIER_DIST = 5

# Threshold used to check if the box is corner box or not
# A box is corner box if the number of boxes in the verticle line of BoxToCheck is greater than this threshold or not.
THRESHOLD_TO_CHECK_IF_CORNER_BOX = 10

# Minimum number of black pixel present in grid element for considering as marked.
MIN_NUM_OF_BLACK_FOR_ANSWER = 10

# Threshold length of corner circle
## It means that the corner circle must be present at what max distance from the boundary(Keep this value small).
ThreshLengthCC = 90

# Macros for HoughCircle
dp = 1.3
MinRadius = 0
MaxRadius = 20

# Threshold Image at this value:
ThresholdImageAt = 75

# List of alphabets and numbers
## Last character is '_' for empty answer(Blank space/No answer).
Alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
            'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
            'Y', 'Z', '_']
